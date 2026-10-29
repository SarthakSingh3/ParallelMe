"""Streamlit Interactive Application for ParallelMe Decision Simulator."""

import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from parallelme.engine import run_simulation
from parallelme.export import (
    export_decision_to_json,
    export_observations_to_csv,
    export_simulation_run_to_csv,
    import_decision_from_json,
)
from parallelme.models import Decision, Observation, Scenario, TrackConfig
from parallelme.persistence import Database
from parallelme.sensitivity import check_scenario_ranking_fragility, run_parameter_sweep
from parallelme.validation import InfeasibleScenarioError, ValidationError, validate_decision


st.set_page_config(
    page_title="ParallelMe — Decision Simulator",
    page_icon="⚖️",
    layout="wide",
)

# Initialize database
DB_PATH = Path("parallelme.db")
db = Database(str(DB_PATH))

# Load or initialize active decision in session state
if "active_decision" not in st.session_state:
    all_decisions = db.list_decisions()
    if all_decisions:
        st.session_state["active_decision"] = all_decisions[0]
    else:
        # Load default example if db is empty
        example_path = Path("examples/learning_decision.json")
        if example_path.exists():
            example_dec = import_decision_from_json(example_path)
            db.save_decision(example_dec)
            st.session_state["active_decision"] = example_dec
        else:
            st.session_state["active_decision"] = Decision(title="New Decision")

if "last_simulation_run" not in st.session_state:
    st.session_state["last_simulation_run"] = None


# Sidebar: Decision Selection and Navigation
st.sidebar.title("⚖️ ParallelMe")
st.sidebar.caption("Transparent Decision Simulator & Feedback Engine")

st.sidebar.markdown("---")
st.sidebar.subheader("Active Decision")

decisions_list = db.list_decisions()
dec_titles = {d.id: d.title for d in decisions_list}

selected_id = st.sidebar.selectbox(
    "Select Decision",
    options=list(dec_titles.keys()),
    format_func=lambda did: dec_titles.get(did, "Unknown"),
    index=list(dec_titles.keys()).index(st.session_state["active_decision"].id)
    if st.session_state["active_decision"].id in dec_titles
    else 0,
)

if selected_id and selected_id != st.session_state["active_decision"].id:
    st.session_state["active_decision"] = db.get_decision(selected_id)
    st.session_state["last_simulation_run"] = None
    st.rerun()

# New Decision Form
with st.sidebar.expander("➕ Create New Decision"):
    new_title = st.text_input("Title", value="Career Strategy 2026")
    new_desc = st.text_area("Description", value="Trade-off exploration")
    new_horizon = st.number_input("Horizon (Weeks)", min_value=1, max_value=52, value=12)
    new_max_hrs = st.number_input("Max Weekly Hours", min_value=1.0, max_value=168.0, value=20.0)

    if st.button("Create Decision"):
        new_dec = Decision(
            title=new_title,
            description=new_desc,
            time_horizon_weeks=int(new_horizon),
            max_weekly_hours=float(new_max_hrs),
            scenarios=[],
        )
        try:
            validate_decision(new_dec)
            db.save_decision(new_dec)
            st.session_state["active_decision"] = new_dec
            st.sidebar.success("Created!")
            st.rerun()
        except ValidationError as e:
            st.sidebar.error(str(e))

# JSON Import / Export
st.sidebar.markdown("---")
st.sidebar.subheader("Export & Import")

active_dec: Decision = st.session_state["active_decision"]
json_export_str = export_decision_to_json(active_dec)

st.sidebar.download_button(
    label="📥 Export Decision (JSON)",
    data=json_export_str,
    file_name=f"{active_dec.title.replace(' ', '_').lower()}.json",
    mime="application/json",
)

uploaded_file = st.sidebar.file_uploader("Upload Decision JSON", type=["json"])
if uploaded_file is not None:
    try:
        content = uploaded_file.read().decode("utf-8")
        imported_dec = import_decision_from_json(content)
        db.save_decision(imported_dec)
        st.session_state["active_decision"] = imported_dec
        st.sidebar.success("Successfully imported decision!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Import failed: {e}")


# Main Content Area: Tabs
tab_overview, tab_scenarios, tab_simulate, tab_sensitivity, tab_observations = st.tabs(
    [
        "📋 Overview & Constraints",
        "🎛️ Alternative Scenarios",
        "🎲 Monte Carlo Simulation",
        "🔍 Sensitivity Analysis",
        "📈 Empirical Observations",
    ]
)


# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW & CONSTRAINTS
# -----------------------------------------------------------------------------
with tab_overview:
    st.header(active_dec.title)
    if active_dec.description:
        st.markdown(f"*{active_dec.description}*")

    col1, col2, col3 = st.columns(3)
    col1.metric("Planning Horizon", f"{active_dec.time_horizon_weeks} Weeks")
    col2.metric("Weekly Budget Capacity", f"{active_dec.max_weekly_hours:.1f} hrs/week")
    col3.metric("Scenarios Defined", len(active_dec.scenarios))

    st.markdown("### Resource Feasibility Audit")
    if not active_dec.scenarios:
        st.info("No scenarios defined yet. Go to the 'Alternative Scenarios' tab to add at least 2 options.")
    else:
        audit_rows = []
        for s in active_dec.scenarios:
            total_allocated = s.total_planned_hours
            is_feasible = total_allocated <= active_dec.max_weekly_hours + 1e-9
            audit_rows.append(
                {
                    "Scenario Name": s.name,
                    "Total Weekly Hours": f"{total_allocated:.1f} hrs",
                    "Budget Capacity": f"{active_dec.max_weekly_hours:.1f} hrs",
                    "Feasibility": "✅ Feasible" if is_feasible else "❌ Over Budget",
                }
            )
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True)

    with st.expander("🗑️ Delete this Decision"):
        if st.button("Permanently Delete Decision", type="primary"):
            db.delete_decision(active_dec.id)
            remaining = db.list_decisions()
            if remaining:
                st.session_state["active_decision"] = remaining[0]
            else:
                st.session_state["active_decision"] = Decision(title="Default Decision")
            st.rerun()


# -----------------------------------------------------------------------------
# TAB 2: ALTERNATIVE SCENARIOS
# -----------------------------------------------------------------------------
with tab_scenarios:
    st.subheader("Manage Scenarios")
    st.markdown("Scenarios represent competing resource allocation choices evaluated under uncertainty.")

    for i, sc in enumerate(active_dec.scenarios):
        with st.expander(f"Scenario {i+1}: {sc.name} ({sc.total_planned_hours:.1f} hrs/week)", expanded=(i == 0)):
            st.write(f"**Description:** {sc.description or 'No description provided.'}")

            col_alloc, col_cfg = st.columns(2)
            with col_alloc:
                st.markdown("**Weekly Allocations:**")
                alloc_df = pd.DataFrame(
                    [{"Track": k, "Planned Hours/Week": v} for k, v in sc.allocations.items()]
                )
                st.dataframe(alloc_df, use_container_width=True)

            with col_cfg:
                st.markdown("**Assumptions & Thresholds:**")
                cfg_rows = []
                for t, cfg in sc.track_configs.items():
                    cfg_rows.append(
                        {
                            "Track": t,
                            "Baseline": cfg.baseline_skill,
                            "Velocity Mean": cfg.velocity_mean,
                            "Velocity SD": cfg.velocity_sd,
                            "Distribution": cfg.velocity_dist,
                            "Target Threshold": sc.target_thresholds.get(t, "None"),
                        }
                    )
                st.dataframe(pd.DataFrame(cfg_rows), use_container_width=True)

            if st.button(f"Remove Scenario '{sc.name}'", key=f"del_sc_{sc.id}"):
                active_dec.scenarios = [s for s in active_dec.scenarios if s.id != sc.id]
                db.save_decision(active_dec)
                st.rerun()

    st.markdown("---")
    st.subheader("Add Alternative Scenario")
    with st.form("add_scenario_form"):
        sc_name = st.text_input("Scenario Name", value="New Alternative")
        sc_desc = st.text_area("Scenario Description", value="")

        st.markdown("**Skill Track Allocations (Hours/Week)**")
        col_t1, col_t2 = st.columns(2)
        t1_name = col_t1.text_input("Track 1 Name", value="DSA")
        t1_hrs = col_t1.number_input("Track 1 Weekly Hours", min_value=0.0, max_value=active_dec.max_weekly_hours, value=10.0)
        t1_vel = col_t1.number_input("Track 1 Velocity (units/hr)", min_value=0.1, max_value=10.0, value=1.2)
        t1_target = col_t1.number_input("Track 1 Target Benchmark", min_value=0.0, max_value=1000.0, value=100.0)

        t2_name = col_t2.text_input("Track 2 Name", value="AI_ML")
        t2_hrs = col_t2.number_input("Track 2 Weekly Hours", min_value=0.0, max_value=active_dec.max_weekly_hours, value=5.0)
        t2_vel = col_t2.number_input("Track 2 Velocity (units/hr)", min_value=0.1, max_value=10.0, value=0.9)
        t2_target = col_t2.number_input("Track 2 Target Benchmark", min_value=0.0, max_value=1000.0, value=50.0)

        submitted = st.form_submit_button("Add Scenario")
        if submitted:
            allocs = {}
            configs = {}
            thresholds = {}

            if t1_name.strip():
                allocs[t1_name] = float(t1_hrs)
                configs[t1_name] = TrackConfig(name=t1_name, velocity_mean=float(t1_vel))
                if t1_target > 0:
                    thresholds[t1_name] = float(t1_target)

            if t2_name.strip():
                allocs[t2_name] = float(t2_hrs)
                configs[t2_name] = TrackConfig(name=t2_name, velocity_mean=float(t2_vel))
                if t2_target > 0:
                    thresholds[t2_name] = float(t2_target)

            new_scenario = Scenario(
                decision_id=active_dec.id,
                name=sc_name,
                description=sc_desc,
                allocations=allocs,
                track_configs=configs,
                target_thresholds=thresholds,
            )

            try:
                active_dec.scenarios.append(new_scenario)
                validate_decision(active_dec)
                db.save_decision(active_dec)
                st.success(f"Added scenario '{sc_name}'!")
                st.rerun()
            except ValidationError as e:
                active_dec.scenarios.pop()
                st.error(str(e))


# -----------------------------------------------------------------------------
# TAB 3: MONTE CARLO SIMULATION
# -----------------------------------------------------------------------------
with tab_simulate:
    st.subheader("Monte Carlo Simulation Engine")
    st.markdown(
        "Runs stochastic forward simulations under schedule execution volatility and parameter uncertainty."
    )

    col_sim1, col_sim2, col_sim3 = st.columns([2, 2, 2])
    iterations = col_sim1.select_slider(
        "Iterations (N)",
        options=[500, 1000, 2000, 5000, 10000],
        value=1000,
    )
    seed = col_sim2.number_input("Random Seed (Reproducibility)", min_value=0, max_value=999999, value=42)
    run_btn = col_sim3.button("🚀 Run Simulation", type="primary", use_container_width=True)

    if run_btn:
        try:
            with st.spinner("Simulating alternative futures..."):
                run_res = run_simulation(
                    decision=active_dec,
                    iterations=iterations,
                    random_seed=seed,
                )
                db.save_run(run_res)
                st.session_state["last_simulation_run"] = run_res
                st.success("Simulation completed and snapshot saved to database!")
        except (ValidationError, InfeasibleScenarioError) as e:
            st.error(f"Cannot run simulation: {e}")

    # Display Results if available
    run = st.session_state.get("last_simulation_run")
    if run is not None:
        st.markdown("---")
        st.markdown(f"### Simulation Results (Run ID: `{run.id[:8]}`) — Seed `{run.random_seed}`")

        # Export Run CSV
        csv_data = export_simulation_run_to_csv(run)
        st.download_button(
            label="📥 Download Run Results (CSV)",
            data=csv_data,
            file_name=f"simulation_run_{run.id[:8]}.csv",
            mime="text/csv",
        )

        # Tabular Summary
        table_rows = []
        chart_data = []

        for sc_id, res in run.results.items():
            for track, metric in res.track_summaries.items():
                table_rows.append(
                    {
                        "Scenario": res.scenario_name,
                        "Track": track,
                        "Median (P50)": metric.median,
                        "10th-90th Range": f"[{metric.p10:.1f} – {metric.p90:.1f}]",
                        "Mean ± Std": f"{metric.mean:.1f} ± {metric.std:.1f}",
                        "P(Target Attained)": f"{metric.threshold_prob * 100:.1f}%"
                        if metric.threshold_prob is not None
                        else "N/A",
                    }
                )
                chart_data.append(
                    {
                        "Scenario": res.scenario_name,
                        "Track": track,
                        "Median": metric.median,
                        "P10": metric.p10,
                        "P90": metric.p90,
                    }
                )

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        # Visualization: Percentile Outcome Ranges
        st.markdown("#### Simulated Outcome Ranges ($P_{10}$ to $P_{90}$ with Median)")
        cdf = pd.DataFrame(chart_data)
        if not cdf.empty:
            fig = go.Figure()
            for sc_name in cdf["Scenario"].unique():
                sc_df = cdf[cdf["Scenario"] == sc_name]
                for _, row in sc_df.iterrows():
                    fig.add_trace(
                        go.Bar(
                            name=f"{sc_name} ({row['Track']})",
                            x=[f"{row['Track']} - {sc_name}"],
                            y=[row["Median"]],
                            error_y=dict(
                                type="data",
                                symmetric=False,
                                array=[row["P90"] - row["Median"]],
                                arrayminus=[row["Median"] - row["P10"]],
                            ),
                        )
                    )
            fig.update_layout(
                title="Mastery Levels: Median with 80% Simulated Spread",
                yaxis_title="Units Mastered",
                showlegend=True,
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 4: SENSITIVITY ANALYSIS
# -----------------------------------------------------------------------------
with tab_sensitivity:
    st.subheader("Assumption Fragility & Sensitivity Analysis")
    st.markdown(
        "Identifies whether small perturbations in productivity assumptions reverse scenario rankings."
    )

    if len(active_dec.scenarios) < 2:
        st.warning("Sensitivity ranking analysis requires at least 2 scenarios.")
    else:
        # Determine available tracks
        all_tracks = set()
        for sc in active_dec.scenarios:
            all_tracks.update(sc.allocations.keys())

        if not all_tracks:
            st.info("No skill tracks configured in current scenarios.")
        else:
            col_s1, col_s2, col_s3 = st.columns(3)
            selected_track = col_s1.selectbox("Target Skill Track", options=list(all_tracks))
            param_choice = col_s2.selectbox(
                "Parameter to Perturb",
                options=["velocity_mean", "diminishing_returns", "retention_decay"],
            )
            perturbation = col_s3.slider("Perturbation Range (±%)", min_value=5, max_value=50, value=20)

            if st.button("Run Fragility Check"):
                with st.spinner("Analyzing assumption sensitivity..."):
                    fragility = check_scenario_ranking_fragility(
                        decision=active_dec,
                        scenarios=active_dec.scenarios,
                        target_track=selected_track,
                        param_name=param_choice,
                        perturbation_pct=perturbation / 100.0,
                        iterations=500,
                        random_seed=42,
                    )

                    if fragility["is_fragile"]:
                        st.error(
                            f"⚠️ **Fragile Recommendation:** Varying `{param_choice}` by ±{perturbation}% reverses the ranking of scenarios for '{selected_track}'!"
                        )
                    else:
                        st.success(
                            f"✅ **Robust Recommendation:** The scenario ranking for '{selected_track}' remains stable under ±{perturbation}% variation of `{param_choice}`."
                        )

                    # Show ranking comparison
                    col_r1, col_r2, col_r3 = st.columns(3)
                    col_r1.markdown(f"**Low ({100 - perturbation}%)**")
                    col_r1.json(fragility["low_ranking"])

                    col_r2.markdown("**Baseline (100%)**")
                    col_r2.json(fragility["baseline_ranking"])

                    col_r3.markdown(f"**High ({100 + perturbation}%)**")
                    col_r3.json(fragility["high_ranking"])


# -----------------------------------------------------------------------------
# TAB 5: EMPIRICAL OBSERVATIONS
# -----------------------------------------------------------------------------
with tab_observations:
    st.subheader("Empirical Observation Logging")
    st.markdown(
        "Log weekly hours spent and milestones achieved during real-world execution. Compare reality against the simulated envelope."
    )

    observations = db.list_observations(active_dec.id)

    # Logging Form
    with st.expander("📝 Log Weekly Progress", expanded=(len(observations) == 0)):
        if not active_dec.scenarios:
            st.warning("Define at least one scenario before logging observations.")
        else:
            with st.form("log_observation_form"):
                sc_choices = {s.id: s.name for s in active_dec.scenarios}
                obs_sc_id = st.selectbox(
                    "Executing Scenario",
                    options=list(sc_choices.keys()),
                    format_func=lambda sid: sc_choices[sid],
                )
                obs_week = st.number_input(
                    "Week Number",
                    min_value=1,
                    max_value=active_dec.time_horizon_weeks,
                    value=min(len(observations) + 1, active_dec.time_horizon_weeks),
                )

                # Active tracks
                exec_scenario = next(s for s in active_dec.scenarios if s.id == obs_sc_id)
                actual_hrs_input = {}
                actual_units_input = {}

                st.markdown("**Actual Results for the Week:**")
                for t in exec_scenario.allocations.keys():
                    c_h, c_u = st.columns(2)
                    actual_hrs_input[t] = c_h.number_input(
                        f"{t} Actual Hours", min_value=0.0, max_value=168.0, value=0.0
                    )
                    actual_units_input[t] = c_u.number_input(
                        f"{t} Actual Units Mastered", min_value=0.0, max_value=1000.0, value=0.0
                    )

                obs_notes = st.text_input("Qualitative Notes", placeholder="e.g. Flu on Wednesday; completed 4 medium problems")

                if st.form_submit_button("Save Observation"):
                    new_obs = Observation(
                        decision_id=active_dec.id,
                        scenario_id=obs_sc_id,
                        week_number=int(obs_week),
                        actual_hours=actual_hrs_input,
                        actual_units=actual_units_input,
                        notes=obs_notes,
                    )
                    db.save_observation(new_obs)
                    st.success(f"Saved observation for Week {obs_week}!")
                    st.rerun()

    # Observations Display
    if observations:
        st.markdown(f"### Recorded Observations ({len(observations)} total)")
        obs_df_rows = []
        for o in observations:
            obs_df_rows.append(
                {
                    "Week": o.week_number,
                    "Scenario": next((s.name for s in active_dec.scenarios if s.id == o.scenario_id), "Unknown"),
                    "Actual Hours": json.dumps(o.actual_hours),
                    "Actual Units": json.dumps(o.actual_units),
                    "Notes": o.notes,
                    "Timestamp": o.logged_at[:10],
                }
            )
        st.dataframe(pd.DataFrame(obs_df_rows), use_container_width=True)

        # Download Observations CSV
        obs_csv = export_observations_to_csv(observations)
        st.download_button(
            label="📥 Download Observations (CSV)",
            data=obs_csv,
            file_name=f"observations_{active_dec.id[:8]}.csv",
            mime="text/csv",
        )

        # Sample Size Guardrail Alert
        if len(observations) < 30:
            st.info(
                f"ℹ️ **Observation Sample Size: {len(observations)} / 30.** "
                "Per ParallelMe principles, statistical recalibration and ML model updates remain disabled "
                "until at least 30 consistent observations are recorded to prevent overfitting on transient noise."
            )
