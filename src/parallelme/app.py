"""Streamlit Interactive Application for ParallelMe Decision Simulator.

Supports multi-language (English, Hindi, Hinglish), multi-domain decisions
(travel, fitness, career, financial, custom), and guided scenario wizards.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

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
from parallelme.sensitivity import check_scenario_ranking_fragility
from parallelme.templates_and_i18n import (
    TRANSLATIONS,
    create_decision_from_template,
    get_prebuilt_templates,
)
from parallelme.validation import InfeasibleScenarioError, ValidationError, validate_decision


st.set_page_config(
    page_title="ParallelMe — Decision Simulator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Database
DB_PATH = Path("parallelme.db")
db = Database(str(DB_PATH))

# Populate pre-built multi-domain starter decisions if database is nearly empty
existing_decisions = db.list_decisions()
if len(existing_decisions) < 2:
    templates = get_prebuilt_templates()
    for tkey in ["trip_planning", "fitness_health", "career_study"]:
        init_dec = create_decision_from_template(tkey)
        # Check if already in db by title to avoid duplicate
        if not any(d.title == init_dec.title for d in existing_decisions):
            db.save_decision(init_dec)

# Refresh decisions list
all_decisions = db.list_decisions()

# Session State Initialization
if "lang" not in st.session_state:
    st.session_state["lang"] = "EN"

if "active_decision" not in st.session_state or st.session_state["active_decision"] is None:
    st.session_state["active_decision"] = all_decisions[0] if all_decisions else Decision(title="My First Decision")

if "last_simulation_run" not in st.session_state:
    st.session_state["last_simulation_run"] = None


# Language Helper
lang_key = st.session_state["lang"]
T = TRANSLATIONS.get(lang_key, TRANSLATIONS["EN"])


# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"## ⚖️ **ParallelMe**")
st.sidebar.caption(T["app_tagline"])

# Language Selector
lang_choice = st.sidebar.radio(
    "🌐 Language / भाषा",
    options=["English", "हिन्दी (Hindi)", "Hinglish"],
    index=0 if lang_key == "EN" else (1 if lang_key == "HI" else 2),
    horizontal=True,
)
mapped_lang = "EN" if "English" in lang_choice else ("HI" if "हिन्दी" in lang_choice else "HING")
if mapped_lang != st.session_state["lang"]:
    st.session_state["lang"] = mapped_lang
    st.rerun()

st.sidebar.markdown("---")

# Decision Selection Dropdown
st.sidebar.subheader(f"📌 {T['active_decision']}")
dec_titles = {d.id: d.title for d in all_decisions}

# Safe index resolution
current_id = st.session_state["active_decision"].id
options_keys = list(dec_titles.keys())
safe_index = options_keys.index(current_id) if current_id in options_keys else 0

selected_id = st.sidebar.selectbox(
    T["choose_decision"],
    options=options_keys,
    format_func=lambda did: dec_titles.get(did, "Untitled"),
    index=safe_index,
)

if selected_id and selected_id != st.session_state["active_decision"].id:
    st.session_state["active_decision"] = db.get_decision(selected_id)
    st.session_state["last_simulation_run"] = None
    st.rerun()


# CREATE NEW DECISION WIZARD
with st.sidebar.expander(T["create_new_decision"], expanded=False):
    st.markdown("### 🎯 Quick Start with Template")
    template_choices = {
        "trip_planning": "🏖️ Trip & Vacation Plan (Goa / Roadtrip / Flights)",
        "fitness_health": "🏋️ Fitness & Body Transformation (Gym vs Home)",
        "career_study": "🎓 Career / Placement Prep (Coding vs Projects)",
        "purchase_finance": "💰 Commute / Purchase (Bike vs Metro vs Cabs)",
        "custom": "✍️ Custom Decision (Blank with 2 starter scenarios)",
    }

    selected_tpl_key = st.selectbox(
        T["template_label"],
        options=list(template_choices.keys()),
        format_func=lambda k: template_choices[k],
    )

    custom_name = st.text_input(T["decision_title"], placeholder="e.g. My Goa Trip Plan")

    if st.button(T["btn_create"], type="primary"):
        if selected_tpl_key == "custom":
            # Generate clean starter custom decision with 2 balanced options so it never starts empty!
            starter_d = Decision(
                title=custom_name.strip() if custom_name.strip() else "My Custom Decision",
                description="Explore alternative plans under real uncertainty.",
                time_horizon_weeks=8,
                max_weekly_hours=20.0,
                scenarios=[
                    Scenario(
                        name="Plan A: Focused Effort",
                        description="Concentrated effort on primary activity.",
                        allocations={"Activity_1": 15.0, "Activity_2": 3.0},
                        track_configs={
                            "Activity_1": TrackConfig(name="Activity_1", velocity_mean=1.2),
                            "Activity_2": TrackConfig(name="Activity_2", velocity_mean=0.8),
                        },
                        target_thresholds={"Activity_1": 80.0},
                    ),
                    Scenario(
                        name="Plan B: Balanced Effort",
                        description="Split effort evenly across both activities.",
                        allocations={"Activity_1": 9.0, "Activity_2": 9.0},
                        track_configs={
                            "Activity_1": TrackConfig(name="Activity_1", velocity_mean=1.0),
                            "Activity_2": TrackConfig(name="Activity_2", velocity_mean=1.0),
                        },
                        target_thresholds={"Activity_1": 50.0, "Activity_2": 50.0},
                    ),
                ],
            )
            for s in starter_d.scenarios:
                s.decision_id = starter_d.id
            db.save_decision(starter_d)
            st.session_state["active_decision"] = starter_d
        else:
            new_from_tpl = create_decision_from_template(selected_tpl_key, custom_title=custom_name)
            db.save_decision(new_from_tpl)
            st.session_state["active_decision"] = new_from_tpl

        st.session_state["last_simulation_run"] = None
        st.success("Decision created with alternative scenarios ready!")
        st.rerun()


# Export & Import
st.sidebar.markdown("---")
st.sidebar.caption("Data Portability")
active_dec: Decision = st.session_state["active_decision"]

st.sidebar.download_button(
    label=T["export_json"],
    data=export_decision_to_json(active_dec),
    file_name=f"{active_dec.title.replace(' ', '_').lower()}.json",
    mime="application/json",
)

uploaded_file = st.sidebar.file_uploader(T["upload_json"], type=["json"])
if uploaded_file is not None:
    try:
        content = uploaded_file.read().decode("utf-8")
        imported_dec = import_decision_from_json(content)
        db.save_decision(imported_dec)
        st.session_state["active_decision"] = imported_dec
        st.sidebar.success("Imported!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {e}")


# -----------------------------------------------------------------------------
# MAIN APP TABS
# -----------------------------------------------------------------------------
tab_overview, tab_scenarios, tab_simulate, tab_sensitivity, tab_observations = st.tabs(
    [
        T["tab_overview"],
        T["tab_scenarios"],
        T["tab_simulate"],
        T["tab_sensitivity"],
        T["tab_observations"],
    ]
)


# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW & BUDGET CHECK
# -----------------------------------------------------------------------------
with tab_overview:
    st.title(active_dec.title)
    if active_dec.description:
        st.info(f"💡 **Context:** {active_dec.description}")

    col1, col2, col3 = st.columns(3)
    col1.metric("⏱️ Planning Duration", f"{active_dec.time_horizon_weeks} Weeks")
    col2.metric("🔋 Weekly Budget Capacity", f"{active_dec.max_weekly_hours:.1f} Units/Hrs")
    col3.metric("🔀 Alternatives Defined", len(active_dec.scenarios))

    st.markdown("---")
    st.subheader(f"🛡️ {T['resource_audit']}")
    st.caption("A fair comparison requires that every alternative scenario respects the same maximum budget capacity.")

    if not active_dec.scenarios:
        st.warning("⚠️ No scenarios found for this decision. Click the 'Alternative Choices' tab to add at least 2 options, or create a decision using a template in the sidebar!")
    else:
        audit_cards = []
        all_feasible = True
        for sc in active_dec.scenarios:
            allocated = sc.total_planned_hours
            feasible = allocated <= (active_dec.max_weekly_hours + 1e-9)
            if not feasible:
                all_feasible = False
            audit_cards.append(
                {
                    "Alternative Scenario": sc.name,
                    "Allocated per Week": f"{allocated:.1f} hrs/units",
                    "Total Capacity": f"{active_dec.max_weekly_hours:.1f} hrs/units",
                    "Status": "✅ Feasible (Ready)" if feasible else "❌ Over Budget!",
                }
            )
        st.dataframe(pd.DataFrame(audit_cards), use_container_width=True)

        if all_feasible:
            st.success("🎉 All scenarios are mathematically feasible and respect your budget constraints!")
        else:
            st.error("⚠️ One or more scenarios allocate more than your weekly capacity. Please adjust allocations in the 'Alternative Choices' tab.")

    with st.expander("🗑️ Delete this Decision"):
        st.caption("Permanently deletes this decision and all associated runs and observations.")
        if st.button(T["btn_delete"], type="primary"):
            db.delete_decision(active_dec.id)
            remaining = db.list_decisions()
            st.session_state["active_decision"] = remaining[0] if remaining else None
            st.session_state["last_simulation_run"] = None
            st.rerun()


# -----------------------------------------------------------------------------
# TAB 2: ALTERNATIVE SCENARIOS
# -----------------------------------------------------------------------------
with tab_scenarios:
    st.subheader(T["tab_scenarios"])
    st.markdown("Each scenario represents a realistic, competing choice (e.g. Flight vs Train, or Gym vs Home Workout).")

    if not active_dec.scenarios:
        st.warning("No scenarios added yet. Add at least two alternatives below to compare them!")

    for idx, sc in enumerate(active_dec.scenarios):
        with st.expander(f"🔹 Option {idx + 1}: **{sc.name}** (Allocates {sc.total_planned_hours:.1f} / {active_dec.max_weekly_hours:.1f} units)", expanded=True):
            st.markdown(f"*{sc.description or 'No description provided.'}*")

            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown("**Weekly Allocation:**")
                alloc_df = pd.DataFrame(
                    [{"Activity / Track": k, "Resource per Week": f"{v} units"} for k, v in sc.allocations.items()]
                )
                st.dataframe(alloc_df, use_container_width=True)

            with col_b:
                st.markdown("**Productivity & Benchmarks:**")
                meta_rows = []
                for k, cfg in sc.track_configs.items():
                    meta_rows.append(
                        {
                            "Activity": k,
                            "Speed (Units/Hr)": cfg.velocity_mean,
                            "Target Goal": sc.target_thresholds.get(k, "Open"),
                        }
                    )
                st.dataframe(pd.DataFrame(meta_rows), use_container_width=True)

            if st.button(f"🗑️ Delete Scenario '{sc.name}'", key=f"del_sc_{sc.id}"):
                active_dec.scenarios = [s for s in active_dec.scenarios if s.id != sc.id]
                db.save_decision(active_dec)
                st.rerun()

    st.markdown("---")
    st.subheader("➕ Add Another Alternative Scenario")

    with st.form("simple_add_scenario"):
        new_sc_name = st.text_input("Scenario Name", placeholder="e.g. Option C: Hybrid Weekend Routine")
        new_sc_desc = st.text_input("Short Description / Premise", placeholder="e.g. Rent a car and split costs with 3 friends")

        col_input1, col_input2 = st.columns(2)
        with col_input1:
            st.markdown("**Activity 1:**")
            act1_name = st.text_input("Activity 1 Name", value="Core_Focus")
            act1_hours = st.number_input("Resource Allocated (per week)", min_value=0.0, max_value=active_dec.max_weekly_hours, value=min(10.0, active_dec.max_weekly_hours))
            act1_speed = st.number_input("Progress Speed (units per hour)", min_value=0.1, max_value=20.0, value=1.0)
            act1_goal = st.number_input("Target Goal Benchmark (optional)", min_value=0.0, max_value=10000.0, value=50.0)

        with col_input2:
            st.markdown("**Activity 2 (Optional):**")
            act2_name = st.text_input("Activity 2 Name", value="Secondary_Focus")
            act2_hours = st.number_input("Resource Allocated (Activity 2)", min_value=0.0, max_value=active_dec.max_weekly_hours, value=0.0)
            act2_speed = st.number_input("Progress Speed (Activity 2)", min_value=0.1, max_value=20.0, value=1.0)
            act2_goal = st.number_input("Target Goal (Activity 2)", min_value=0.0, max_value=10000.0, value=0.0)

        submitted_new_sc = st.form_submit_button("Add Alternative Scenario", type="primary")
        if submitted_new_sc:
            if not new_sc_name.strip():
                st.error("Please enter a scenario name.")
            else:
                allocs = {}
                configs = {}
                thresholds = {}

                if act1_name.strip():
                    allocs[act1_name] = float(act1_hours)
                    configs[act1_name] = TrackConfig(name=act1_name, velocity_mean=float(act1_speed))
                    if act1_goal > 0:
                        thresholds[act1_name] = float(act1_goal)

                if act2_name.strip() and act2_hours > 0:
                    allocs[act2_name] = float(act2_hours)
                    configs[act2_name] = TrackConfig(name=act2_name, velocity_mean=float(act2_speed))
                    if act2_goal > 0:
                        thresholds[act2_name] = float(act2_goal)

                created_scenario = Scenario(
                    decision_id=active_dec.id,
                    name=new_sc_name.strip(),
                    description=new_sc_desc.strip(),
                    allocations=allocs,
                    track_configs=configs,
                    target_thresholds=thresholds,
                )

                try:
                    active_dec.scenarios.append(created_scenario)
                    validate_decision(active_dec)
                    db.save_decision(active_dec)
                    st.success(f"Added scenario '{new_sc_name}'!")
                    st.rerun()
                except ValidationError as e:
                    active_dec.scenarios.pop()
                    st.error(f"Cannot add: {e}")


# -----------------------------------------------------------------------------
# TAB 3: MONTE CARLO SIMULATION
# -----------------------------------------------------------------------------
with tab_simulate:
    st.subheader(T["tab_simulate"])
    st.markdown(
        "Instead of pretending to know the exact future, Monte Carlo runs **thousands of parallel simulations** "
        "accounting for real-life disruptions, sick days, fatigue, and schedule variations."
    )

    if len(active_dec.scenarios) < 2:
        st.warning("⚠️ You need at least 2 scenarios to run a comparison simulation. Add another scenario in the 'Alternative Choices' tab!")
    else:
        col_c1, col_c2, col_c3 = st.columns([2, 2, 2])
        sim_iterations = col_c1.select_slider(
            "Simulated Futures Count (N)",
            options=[500, 1000, 2000, 5000],
            value=1000,
            help="Higher iterations produce smoother, more stable outcome distributions.",
        )
        sim_seed = col_c2.number_input("Random Seed (for reproducibility)", min_value=0, max_value=999999, value=42)
        trigger_sim = col_c3.button(T["btn_run_sim"], type="primary", use_container_width=True)

        if trigger_sim:
            try:
                with st.spinner(T["sim_explainer"]):
                    run_snapshot = run_simulation(
                        decision=active_dec,
                        iterations=sim_iterations,
                        random_seed=sim_seed,
                    )
                    db.save_run(run_snapshot)
                    st.session_state["last_simulation_run"] = run_snapshot
                    st.success("✅ Simulation completed! Outcome envelopes generated below.")
            except (ValidationError, InfeasibleScenarioError) as e:
                st.error(f"Validation Error: {e}")

        # Display Results
        run = st.session_state.get("last_simulation_run")
        if run is not None:
            st.markdown("---")
            st.markdown(f"### 📊 Simulated Outcome Comparison (Run Seed `{run.random_seed}`)")

            # Download CSV
            csv_text = export_simulation_run_to_csv(run)
            st.download_button(
                label=T["export_csv"],
                data=csv_text,
                file_name=f"sim_results_{run.id[:8]}.csv",
                mime="text/csv",
            )

            # Build Comparison Table
            summary_table = []
            plot_records = []

            for sc_id, sc_res in run.results.items():
                for track, metric in sc_res.track_summaries.items():
                    prob_str = f"{metric.threshold_prob * 100:.1f}%" if metric.threshold_prob is not None else "Open"
                    summary_table.append(
                        {
                            "Alternative": sc_res.scenario_name,
                            "Activity": track,
                            "Typical Outcome (Median)": f"{metric.median:.1f}",
                            "Realistic 80% Spread": f"{metric.p10:.1f} – {metric.p90:.1f}",
                            "Worst Case (P10)": f"{metric.p10:.1f}",
                            "Best Case (P90)": f"{metric.p90:.1f}",
                            "Target Attainment Chance": prob_str,
                        }
                    )
                    plot_records.append(
                        {
                            "Alternative": sc_res.scenario_name,
                            "Activity": track,
                            "Median": metric.median,
                            "P10": metric.p10,
                            "P90": metric.p90,
                        }
                    )

            st.dataframe(pd.DataFrame(summary_table), use_container_width=True)

            # Chart Visualization
            st.markdown("#### 📈 Outcome Uncertainty Envelope ($P_{10}$ to $P_{90}$ with Median Bar)")
            df_plot = pd.DataFrame(plot_records)
            if not df_plot.empty:
                fig = px.bar(
                    df_plot,
                    x="Alternative",
                    y="Median",
                    color="Activity",
                    barmode="group",
                    title="Simulated Median Outcomes with 80% Uncertainty Envelopes",
                    labels={"Median": "Expected Cumulative Progress Units"},
                )
                fig.update_layout(height=450)
                st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 4: SENSITIVITY & FRAGILITY
# -----------------------------------------------------------------------------
with tab_sensitivity:
    st.subheader(T["fragility_title"])
    st.markdown(T["fragility_desc"])

    if len(active_dec.scenarios) < 2:
        st.warning("⚠️ Sensitivity ranking analysis requires at least 2 scenarios.")
    else:
        # Collect distinct activity tracks
        distinct_tracks = set()
        for sc in active_dec.scenarios:
            distinct_tracks.update(sc.allocations.keys())

        if not distinct_tracks:
            st.info("No activities configured in current scenarios.")
        else:
            col_f1, col_f2, col_f3 = st.columns(3)
            test_track = col_f1.selectbox("Activity to Test", options=list(distinct_tracks))
            param_perturbed = col_f2.selectbox(
                "Factor to Vary",
                options=["velocity_mean", "diminishing_returns"],
                format_func=lambda p: "Productivity Speed (Units/Hr)" if p == "velocity_mean" else "Fatigue / Diminishing Returns",
            )
            pct_variation = col_f3.slider("Variation Range (±%)", min_value=10, max_value=40, value=20)

            if st.button("Check Decision Fragility", type="primary"):
                with st.spinner("Testing if scenario rankings reverse..."):
                    fragility_report = check_scenario_ranking_fragility(
                        decision=active_dec,
                        scenarios=active_dec.scenarios,
                        target_track=test_track,
                        param_name=param_perturbed,
                        perturbation_pct=pct_variation / 100.0,
                        iterations=500,
                        random_seed=42,
                    )

                    if fragility_report["is_fragile"]:
                        st.error(
                            f"⚠️ **Fragile Decision:** Varying your speed/productivity by ±{pct_variation}% flips the ranking of which scenario is best! "
                            "This means your decision is sensitive to your assumptions."
                        )
                    else:
                        st.success(
                            f"🛡️ **Robust Decision:** Even if your speed is {pct_variation}% slower or faster than estimated, "
                            "the best scenario remains the best scenario. You can proceed with high confidence in this structure."
                        )


# -----------------------------------------------------------------------------
# TAB 5: EMPIRICAL OBSERVATIONS
# -----------------------------------------------------------------------------
with tab_observations:
    st.subheader(T["tab_observations"])
    st.markdown(
        "Simulation is only the first half of ParallelMe. As you execute your decision in real life, "
        "log your actual hours and results weekly to see whether reality falls inside the simulated envelope."
    )

    observations = db.list_observations(active_dec.id)

    # Logging Form
    with st.expander(f"📝 {T['log_progress_title']}", expanded=(len(observations) == 0)):
        if not active_dec.scenarios:
            st.warning("Please define scenarios first.")
        else:
            with st.form("log_obs_form_interactive"):
                sc_map = {s.id: s.name for s in active_dec.scenarios}
                chosen_sc_id = st.selectbox(
                    "Which Scenario are you actively executing?",
                    options=list(sc_map.keys()),
                    format_func=lambda sid: sc_map[sid],
                )
                obs_week_num = st.number_input(
                    "Week Number",
                    min_value=1,
                    max_value=active_dec.time_horizon_weeks,
                    value=min(len(observations) + 1, active_dec.time_horizon_weeks),
                )

                selected_sc = next(s for s in active_dec.scenarios if s.id == chosen_sc_id)
                logged_hours = {}
                logged_units = {}

                st.markdown("**Enter Real Measured Progress:**")
                for act in selected_sc.allocations.keys():
                    c_h, c_u = st.columns(2)
                    logged_hours[act] = c_h.number_input(f"{act} Actual Hours / Resources", min_value=0.0, max_value=168.0, value=selected_sc.allocations[act])
                    logged_units[act] = c_u.number_input(f"{act} Milestones / Units Achieved", min_value=0.0, max_value=10000.0, value=0.0)

                obs_reflection = st.text_input("Notes & Reflections", placeholder="e.g. Travel delay on Tuesday; great progress on Thursday")

                if st.form_submit_button("Save Weekly Observation", type="primary"):
                    new_obs = Observation(
                        decision_id=active_dec.id,
                        scenario_id=chosen_sc_id,
                        week_number=int(obs_week_num),
                        actual_hours=logged_hours,
                        actual_units=logged_units,
                        notes=obs_reflection,
                    )
                    db.save_observation(new_obs)
                    st.success(f"Recorded Week {obs_week_num} progress!")
                    st.rerun()

    # Observation Display
    if observations:
        st.markdown(f"### Recorded Observations ({len(observations)} total)")
        obs_rows = []
        for o in observations:
            sc_name = next((s.name for s in active_dec.scenarios if s.id == o.scenario_id), "Unknown")
            obs_rows.append(
                {
                    "Week": f"Week {o.week_number}",
                    "Scenario Executing": sc_name,
                    "Actual Hours Spent": json.dumps(o.actual_hours),
                    "Actual Progress Units": json.dumps(o.actual_units),
                    "Notes": o.notes,
                    "Date Logged": o.logged_at[:10],
                }
            )
        st.dataframe(pd.DataFrame(obs_rows), use_container_width=True)

        st.download_button(
            label="📥 Download Observations CSV",
            data=export_observations_to_csv(observations),
            file_name=f"observations_{active_dec.id[:8]}.csv",
            mime="text/csv",
        )

        if len(observations) < 30:
            st.info(
                f"ℹ️ **Current Observation Count: {len(observations)} / 30.** "
                "In accordance with ParallelMe scientific principles, automatic model recalibration is disabled until "
                "at least 30 observations are recorded to protect you against spurious overfitting on noisy short-term data."
            )
