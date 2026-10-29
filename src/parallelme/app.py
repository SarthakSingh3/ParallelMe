"""Streamlit Interactive Application for ParallelMe Decision Simulator.

Supports multi-language (English, Hindi, Hinglish), multi-domain decisions
(travel, fitness, career, financial, custom), and a conversational Q&A wizard
for effortlessly adding alternative scenarios.
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

# Custom Styling for polished, friendly visual cards
st.markdown(
    """
    <style>
    .scenario-card {
        background-color: #1e222b;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .badge-feasible {
        background-color: #238636;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: bold;
    }
    .badge-infeasible {
        background-color: #da3633;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
        st.warning("⚠️ No scenarios found for this decision. Use the guided assistant in the 'Alternative Choices' tab to add options!")
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
# TAB 2: ALTERNATIVE SCENARIOS (SIMPLIFIED & CONVERSATIONAL Q&A)
# -----------------------------------------------------------------------------
with tab_scenarios:
    st.subheader(f"🔀 {T['tab_scenarios']}")
    st.markdown("Compare different paths side-by-side. Each option allocates your weekly budget differently.")

    # 1. Existing Scenarios Display (Clean Visual Cards)
    if not active_dec.scenarios:
        st.warning("⚠️ No options added yet. Answer the simple questions below to add your first option!")
    else:
        st.markdown(f"### Current Alternatives ({len(active_dec.scenarios)} options)")
        cols_sc = st.columns(min(len(active_dec.scenarios), 3))
        for idx, sc in enumerate(active_dec.scenarios):
            col_target = cols_sc[idx % len(cols_sc)]
            with col_target:
                is_ok = sc.total_planned_hours <= active_dec.max_weekly_hours + 1e-9
                status_color = "green" if is_ok else "red"
                status_text = "Within Budget" if is_ok else "Over Budget"

                with st.container(border=True):
                    st.markdown(f"#### 🏷️ Option {idx+1}: **{sc.name}**")
                    if sc.description:
                        st.caption(sc.description)

                    # Show allocation breakdown
                    st.markdown(f"**Weekly Resource Used:** `{sc.total_planned_hours:.1f}` / `{active_dec.max_weekly_hours:.1f}`")
                    for act, hrs in sc.allocations.items():
                        st.write(f"• **{act}:** {hrs:.1f} hrs/units")
                        if act in sc.target_thresholds:
                            st.caption(f"  🎯 Target Goal: {sc.target_thresholds[act]:.0f} units")

                    if st.button(f"❌ Remove Option {idx+1}", key=f"del_opt_{sc.id}", use_container_width=True):
                        active_dec.scenarios = [s for s in active_dec.scenarios if s.id != sc.id]
                        db.save_decision(active_dec)
                        st.rerun()

    st.markdown("---")

    # 2. CONVERSATIONAL Q&A WIZARD TO ADD A NEW SCENARIO
    st.markdown(f"### {T['wizard_title']}")
    st.caption(T["wizard_subtitle"])

    with st.container(border=True):
        # Question 1: Name
        sc_q1 = st.text_input(
            T["q1_name"],
            placeholder=T["q1_placeholder"],
            key="wizard_sc_name",
        )

        col_q2, col_q3 = st.columns([1, 1])
        # Question 2: Primary Activity
        with col_q2:
            sc_q2_act1 = st.text_input(
                T["q2_main_activity"],
                value="Main_Focus",
                placeholder=T["q2_main_placeholder"],
                key="wizard_act1_name",
            )
        # Question 3: Hours on Primary Activity (Slider)
        with col_q3:
            max_cap = float(active_dec.max_weekly_hours)
            default_h1 = min(12.0, max_cap)
            sc_q3_h1 = st.slider(
                T["q3_hours"],
                min_value=1.0,
                max_value=max_cap,
                value=default_h1,
                step=0.5,
                key="wizard_act1_hours",
            )

        # Question 4: Optional Secondary Activity
        has_second = st.checkbox(
            T["q4_second_activity"],
            value=(max_cap - sc_q3_h1 >= 2.0),
            key="wizard_has_second",
        )

        sc_q4_act2 = ""
        sc_q5_h2 = 0.0
        if has_second:
            col_q4, col_q5 = st.columns([1, 1])
            with col_q4:
                sc_q4_act2 = st.text_input(
                    "Secondary Activity Name",
                    value="Secondary_Task",
                    placeholder=T["q4_second_placeholder"],
                    key="wizard_act2_name",
                )
            with col_q5:
                remaining_budget = max(0.0, max_cap - sc_q3_h1)
                sc_q5_h2 = st.slider(
                    T["q5_second_hours"],
                    min_value=0.5,
                    max_value=max_cap,
                    value=min(4.0, max(0.5, remaining_budget)),
                    step=0.5,
                    key="wizard_act2_hours",
                )

        # Question 5: Goal Benchmark
        sc_q6_goal = st.number_input(
            T["q6_goal"],
            min_value=0.0,
            max_value=10000.0,
            value=50.0,
            step=10.0,
            key="wizard_goal",
        )

        # Live calculation preview badge
        total_wizard_hours = sc_q3_h1 + sc_q5_h2
        if total_wizard_hours <= max_cap:
            st.success(
                f"✅ **Total Allocation:** {total_wizard_hours:.1f} / {max_cap:.1f} units per week "
                f"({max_cap - total_wizard_hours:.1f} buffer left for breaks/rest)"
            )
        else:
            st.error(
                f"⚠️ **Total Allocation:** {total_wizard_hours:.1f} / {max_cap:.1f} units "
                f"(Exceeds capacity by {total_wizard_hours - max_cap:.1f} units! Please reduce hours on the slider.)"
            )

        if st.button(T["btn_add_scenario"], type="primary", use_container_width=True):
            if not sc_q1.strip():
                st.error("Please enter a name for this option in Question 1.")
            elif total_wizard_hours > max_cap + 1e-9:
                st.error(f"Cannot save: Total hours ({total_wizard_hours:.1f}) exceed weekly budget ({max_cap:.1f}).")
            else:
                allocations_dict = {sc_q2_act1.strip(): float(sc_q3_h1)}
                configs_dict = {sc_q2_act1.strip(): TrackConfig(name=sc_q2_act1.strip(), velocity_mean=1.2)}
                thresholds_dict = {sc_q2_act1.strip(): float(sc_q6_goal)} if sc_q6_goal > 0 else {}

                if has_second and sc_q4_act2.strip() and sc_q5_h2 > 0:
                    allocations_dict[sc_q4_act2.strip()] = float(sc_q5_h2)
                    configs_dict[sc_q4_act2.strip()] = TrackConfig(name=sc_q4_act2.strip(), velocity_mean=1.0)

                new_sc = Scenario(
                    decision_id=active_dec.id,
                    name=sc_q1.strip(),
                    description=f"Allocates {sc_q3_h1:.1f} hrs to {sc_q2_act1}" + (f" and {sc_q5_h2:.1f} hrs to {sc_q4_act2}" if has_second else ""),
                    allocations=allocations_dict,
                    track_configs=configs_dict,
                    target_thresholds=thresholds_dict,
                )

                try:
                    active_dec.scenarios.append(new_sc)
                    validate_decision(active_dec)
                    db.save_decision(active_dec)
                    st.success(f"Added option '{sc_q1}' successfully!")
                    st.rerun()
                except ValidationError as err:
                    active_dec.scenarios.pop()
                    st.error(f"Error: {err}")

    # 3. 1-CLICK PRESET BUTTONS
    st.markdown(f"### {T['quick_presets_title']}")
    st.caption("Need ideas? Click any button to add a pre-configured balanced alternative instantly:")
    col_p1, col_p2, col_p3 = st.columns(3)

    cap = float(active_dec.max_weekly_hours)
    if col_p1.button("⚡ Add 'High Focus' (85% on Main Focus)", use_container_width=True):
        opt = Scenario(
            decision_id=active_dec.id,
            name=f"High Focus Strategy ({len(active_dec.scenarios)+1})",
            description="Focuses 85% of time on primary goal with minimal distractions.",
            allocations={"Core_Objective": round(cap * 0.85, 1)},
            track_configs={"Core_Objective": TrackConfig(name="Core_Objective", velocity_mean=1.3)},
            target_thresholds={"Core_Objective": 75.0},
        )
        active_dec.scenarios.append(opt)
        db.save_decision(active_dec)
        st.rerun()

    if col_p2.button("⚡ Add 'Balanced 50/50' (Even Split)", use_container_width=True):
        half = round((cap * 0.9) / 2.0, 1)
        opt = Scenario(
            decision_id=active_dec.id,
            name=f"Balanced Strategy ({len(active_dec.scenarios)+1})",
            description="Splits effort equally across two complementary activities.",
            allocations={"Activity_A": half, "Activity_B": half},
            track_configs={
                "Activity_A": TrackConfig(name="Activity_A", velocity_mean=1.1),
                "Activity_B": TrackConfig(name="Activity_B", velocity_mean=1.1),
            },
            target_thresholds={"Activity_A": 40.0, "Activity_B": 40.0},
        )
        active_dec.scenarios.append(opt)
        db.save_decision(active_dec)
        st.rerun()

    if col_p3.button("⚡ Add 'Flexible Plan' (Low Burnout)", use_container_width=True):
        light = round(cap * 0.65, 1)
        opt = Scenario(
            decision_id=active_dec.id,
            name=f"Flexible Buffer Plan ({len(active_dec.scenarios)+1})",
            description="Moderate pace with large buffer hours to prevent fatigue or disruptions.",
            allocations={"Sustainable_Pace": light},
            track_configs={"Sustainable_Pace": TrackConfig(name="Sustainable_Pace", velocity_mean=1.0)},
            target_thresholds={"Sustainable_Pace": 45.0},
        )
        active_dec.scenarios.append(opt)
        db.save_decision(active_dec)
        st.rerun()


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
        st.warning("⚠️ You need at least 2 scenarios to run a comparison simulation. Add another option in the 'Alternative Choices' tab!")
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
