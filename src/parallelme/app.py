"""Streamlit Interactive Application for ParallelMe Decision Simulator.

Supports multi-language (English, Hindi, Hinglish), human-friendly decision scorecards,
plain-language executive summaries, and guided scenario assistants.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import parallelme.templates_and_i18n
importlib.reload(parallelme.templates_and_i18n)

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

# Custom Styling for polished, friendly human visual scorecards
st.markdown(
    """
    <style>
    .winner-card {
        background: linear-gradient(135deg, #1e3a2f 0%, #15231c 100%);
        border: 2px solid #2ea043;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .scorecard {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .badge-rank-1 {
        background-color: #f1e05a;
        color: #121212;
        padding: 3px 10px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 13px;
    }
    .badge-rank-2 {
        background-color: #e4e4e4;
        color: #121212;
        padding: 3px 10px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 13px;
    }
    .badge-rank-3 {
        background-color: #cd7f32;
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 13px;
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


# Safe translation helper function
def tr(key: str, default: str = "") -> str:
    lang = st.session_state.get("lang", "EN")
    dict_for_lang = TRANSLATIONS.get(lang, TRANSLATIONS.get("EN", {}))
    if key in dict_for_lang:
        return dict_for_lang[key]
    fallback_en = TRANSLATIONS.get("EN", {})
    return fallback_en.get(key, default or key)


# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"## ⚖️ **ParallelMe**")
st.sidebar.caption(tr("app_tagline", "Explore different paths for any real-life decision under uncertainty"))

# Language Selector
lang_choice = st.sidebar.radio(
    "🌐 Language / भाषा",
    options=["English", "हिन्दी (Hindi)", "Hinglish"],
    index=0 if st.session_state["lang"] == "EN" else (1 if st.session_state["lang"] == "HI" else 2),
    horizontal=True,
)
mapped_lang = "EN" if "English" in lang_choice else ("HI" if "हिन्दी" in lang_choice else "HING")
if mapped_lang != st.session_state["lang"]:
    st.session_state["lang"] = mapped_lang
    st.rerun()

st.sidebar.markdown("---")

# Decision Selection Dropdown
st.sidebar.subheader(f"📌 {tr('active_decision', 'Active Decision')}")
dec_titles = {d.id: d.title for d in all_decisions}

current_id = st.session_state["active_decision"].id
options_keys = list(dec_titles.keys())
safe_index = options_keys.index(current_id) if current_id in options_keys else 0

selected_id = st.sidebar.selectbox(
    tr("choose_decision", "Choose Decision"),
    options=options_keys,
    format_func=lambda did: dec_titles.get(did, "Untitled"),
    index=safe_index,
)

if selected_id and selected_id != st.session_state["active_decision"].id:
    st.session_state["active_decision"] = db.get_decision(selected_id)
    st.session_state["last_simulation_run"] = None
    st.rerun()


# CREATE NEW DECISION WIZARD
with st.sidebar.expander(tr("create_new_decision", "➕ Create New Decision"), expanded=False):
    st.markdown("### 🎯 Quick Start with Template")
    template_choices = {
        "trip_planning": "🏖️ Trip & Vacation Plan (Goa / Roadtrip / Flights)",
        "fitness_health": "🏋️ Fitness & Body Transformation (Gym vs Home)",
        "career_study": "🎓 Career / Placement Prep (Coding vs Projects)",
        "purchase_finance": "💰 Commute / Purchase (Bike vs Metro vs Cabs)",
        "custom": "✍️ Custom Decision (Blank with 2 starter scenarios)",
    }

    selected_tpl_key = st.selectbox(
        tr("template_label", "Choose a Ready-Made Template"),
        options=list(template_choices.keys()),
        format_func=lambda k: template_choices[k],
    )

    custom_name = st.text_input(tr("decision_title", "Decision Title"), placeholder="e.g. My Goa Trip Plan")

    if st.button(tr("btn_create", "Create Decision with Scenarios"), type="primary"):
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
    label=tr("export_json", "📥 Export Plan (JSON)"),
    data=export_decision_to_json(active_dec),
    file_name=f"{active_dec.title.replace(' ', '_').lower()}.json",
    mime="application/json",
)

uploaded_file = st.sidebar.file_uploader(tr("upload_json", "Upload Saved Plan"), type=["json"])
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
        tr("tab_overview", "📋 Summary & Feasibility"),
        tr("tab_scenarios", "🎛️ Alternative Choices"),
        tr("tab_simulate", "🎲 Simulate Futures"),
        tr("tab_sensitivity", "🔍 Risk & Fragility"),
        tr("tab_observations", "📈 Real Progress Log"),
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
    st.subheader(f"🛡️ {tr('resource_audit', 'Resource Feasibility Check')}")
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
        if st.button(tr("btn_delete", "Delete Decision"), type="primary"):
            db.delete_decision(active_dec.id)
            remaining = db.list_decisions()
            st.session_state["active_decision"] = remaining[0] if remaining else None
            st.session_state["last_simulation_run"] = None
            st.rerun()


# -----------------------------------------------------------------------------
# TAB 2: ALTERNATIVE SCENARIOS (CONVERSATIONAL Q&A)
# -----------------------------------------------------------------------------
with tab_scenarios:
    st.subheader(f"🔀 {tr('tab_scenarios', 'Alternative Choices')}")
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

                with st.container(border=True):
                    st.markdown(f"#### 🏷️ Option {idx+1}: **{sc.name}**")
                    if sc.description:
                        st.caption(sc.description)

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

    # 2. CONVERSATIONAL Q&A WIZARD
    st.markdown(f"### {tr('wizard_title', '💬 Guided Assistant: Add a New Alternative')}")
    st.caption(tr("wizard_subtitle", "Answer 3 simple questions. We'll automatically build the scenario for you!"))

    with st.container(border=True):
        # Question 1: Name
        sc_q1 = st.text_input(
            tr("q1_name", "1. What do you want to call this option?"),
            placeholder=tr("q1_placeholder", "e.g. Flight + Luxury Resort, or Intensive DSA Practice"),
            key="wizard_sc_name",
        )

        col_q2, col_q3 = st.columns([1, 1])
        # Question 2: Primary Activity
        with col_q2:
            sc_q2_act1 = st.text_input(
                tr("q2_main_activity", "2. What is the primary activity or expense?"),
                value="Main_Focus",
                placeholder=tr("q2_main_placeholder", "e.g. Sightseeing, LeetCode, Gym Workouts, Rent"),
                key="wizard_act1_name",
            )
        # Question 3: Hours on Primary Activity (Slider)
        with col_q3:
            max_cap = float(active_dec.max_weekly_hours)
            default_h1 = min(12.0, max_cap)
            sc_q3_h1 = st.slider(
                tr("q3_hours", "3. How much weekly time/resource will you give to this main activity?"),
                min_value=1.0,
                max_value=max_cap,
                value=default_h1,
                step=0.5,
                key="wizard_act1_hours",
            )

        # Question 4: Optional Secondary Activity
        has_second = st.checkbox(
            tr("q4_second_activity", "4. Do you have a secondary activity or backup task?"),
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
                    placeholder=tr("q4_second_placeholder", "e.g. Relaxation, Project Work, Cardio, Reading"),
                    key="wizard_act2_name",
                )
            with col_q5:
                remaining_budget = max(0.0, max_cap - sc_q3_h1)
                sc_q5_h2 = st.slider(
                    tr("q5_second_hours", "How much time/resource for this secondary activity?"),
                    min_value=0.5,
                    max_value=max_cap,
                    value=min(4.0, max(0.5, remaining_budget)),
                    step=0.5,
                    key="wizard_act2_hours",
                )

        # Question 5: Goal Benchmark
        sc_q6_goal = st.number_input(
            tr("q6_goal", "5. What is your overall target goal benchmark? (e.g. 50 units/problems/places)"),
            min_value=0.0,
            max_value=10000.0,
            value=50.0,
            step=10.0,
            key="wizard_goal",
        )

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

        if st.button(tr("btn_add_scenario", "✨ Create This Option"), type="primary", use_container_width=True):
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
    st.markdown(f"### {tr('quick_presets_title', '⚡ Quick Presets (1-Click)')}")
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
# TAB 3: MONTE CARLO SIMULATION (HUMAN EXECUTIVE SUMMARY & SCORECARDS)
# -----------------------------------------------------------------------------
with tab_simulate:
    st.subheader(tr("tab_simulate", "🎲 Simulate Futures"))
    st.markdown(
        "Instead of guessing what will happen, ParallelMe runs **1,000 parallel simulations** "
        "incorporating real-world schedule volatility (fatigue, busy days, sickness, and variations)."
    )

    if len(active_dec.scenarios) < 2:
        st.warning("⚠️ You need at least 2 scenarios to run a comparison simulation. Add another option in the 'Alternative Choices' tab!")
    else:
        col_c1, col_c2, col_c3 = st.columns([2, 2, 2])
        sim_iterations = col_c1.select_slider(
            "Futures Count (N)",
            options=[500, 1000, 2000, 5000],
            value=1000,
            help="Higher iterations produce smoother, more reliable distributions.",
        )
        sim_seed = col_c2.number_input("Random Seed (for identical reproduction)", min_value=0, max_value=999999, value=42)
        trigger_sim = col_c3.button(tr("btn_run_sim", "🚀 Simulate Possible Futures"), type="primary", use_container_width=True)

        if trigger_sim:
            try:
                with st.spinner(tr("sim_explainer", "Running 1,000 parallel futures...")):
                    run_snapshot = run_simulation(
                        decision=active_dec,
                        iterations=sim_iterations,
                        random_seed=sim_seed,
                    )
                    db.save_run(run_snapshot)
                    st.session_state["last_simulation_run"] = run_snapshot
                    st.success("✅ Simulation completed!")
            except (ValidationError, InfeasibleScenarioError) as e:
                st.error(f"Validation Error: {e}")

        # Display Results
        run = st.session_state.get("last_simulation_run")
        if run is not None:
            st.markdown("---")

            # -----------------------------------------------------------------
            # 1. PLAIN-LANGUAGE EXECUTIVE TAKEAWAYS (WHAT THIS DATA MEANS)
            # -----------------------------------------------------------------
            scenario_scores = []
            for sc_id, sc_res in run.results.items():
                total_median = sum(m.median for m in sc_res.track_summaries.values())
                min_spread = sum(m.p10 for m in sc_res.track_summaries.values())
                max_spread = sum(m.p90 for m in sc_res.track_summaries.values())
                risk_width = max_spread - min_spread

                # Calculate avg threshold success
                probs = [m.threshold_prob for m in sc_res.track_summaries.values() if m.threshold_prob is not None]
                avg_prob = (sum(probs) / len(probs)) if probs else None

                scenario_scores.append(
                    {
                        "id": sc_id,
                        "name": sc_res.scenario_name,
                        "total_median": total_median,
                        "worst_case": min_spread,
                        "best_case": max_spread,
                        "risk_width": risk_width,
                        "avg_prob": avg_prob,
                        "summaries": sc_res.track_summaries,
                    }
                )

            # Sort descending by total median progress
            scenario_scores.sort(key=lambda s: s["total_median"], reverse=True)
            top_winner = scenario_scores[0]
            safest_option = min(scenario_scores, key=lambda s: s["risk_width"])

            # WINNER HERO CARD (EXPLAINED IN PLAIN LANGUAGE)
            st.markdown("### 💡 Plain-Language Summary & Takeaways")
            lang_current = st.session_state.get("lang", "EN")

            if lang_current == "HI":
                winner_title = f"🏆 सबसे ज्यादा नतीजा देने वाला विकल्प: **{top_winner['name']}**"
                winner_desc = (
                    f"इस रास्ते पर चलने से आपको कुल लगभग **{top_winner['total_median']:.1f} यूनिट्स/प्रगति** मिलने की उम्मीद है। "
                    f"खराब से खराब स्थिति में भी कम से कम **{top_winner['worst_case']:.1f}** और बेहतरीन स्थिति में **{top_winner['best_case']:.1f}** तक पहुंच सकते हैं।"
                )
                safe_note = (
                    f"🛡️ **सबसे कम जोखिम वाला विकल्प:** यदि आप तनावमुक्त और स्थिर प्रगति चाहते हैं, तो **'{safest_option['name']}'** सबसे सुरक्षित है "
                    f"क्योंकि इसमें उतार-चढ़ाव (Uncertainty) सबसे कम है।"
                )
            elif lang_current == "HING":
                winner_title = f"🏆 Top Output Option: **{top_winner['name']}**"
                winner_desc = (
                    f"Is path par chalne se aapko sabse zyada output (**~{top_winner['total_median']:.1f} units**) milne ki high probability hai. "
                    f"Worst case mein bhi aap kam se kam **{top_winner['worst_case']:.1f}** achieve karenge aur best case mein **{top_winner['best_case']:.1f}**."
                )
                safe_note = (
                    f"🛡️ **Safest / Lowest Risk Pick:** Agar aap bina stress ke consistent progress chahte hain, toh **'{safest_option['name']}'** best hai "
                    f"kyunki isme unpredictable fluctuations sabse kam hain."
                )
            else:
                winner_title = f"🏆 Top Progress Recommendation: **{top_winner['name']}**"
                winner_desc = (
                    f"Choosing this path produces the highest expected total outcome (**~{top_winner['total_median']:.1f} units**). "
                    f"Even under adverse disruptions (sickness/delays), you are estimated to reach at least **{top_winner['worst_case']:.1f}**, "
                    f"and up to **{top_winner['best_case']:.1f}** in favorable conditions."
                )
                safe_note = (
                    f"🛡️ **Safest & Most Consistent Option:** If your primary concern is reliability and low burnout, **'{safest_option['name']}'** has the lowest "
                    f"outcome volatility across simulated futures."
                )

            with st.container(border=True):
                st.markdown(f"#### {winner_title}")
                st.write(winner_desc)
                st.info(safe_note)

            # -----------------------------------------------------------------
            # 2. COMPARISON SCORECARDS FOR EACH ALTERNATIVE
            # -----------------------------------------------------------------
            st.markdown("### 🎴 Side-by-Side Plain Scorecards")
            cols_cards = st.columns(min(len(scenario_scores), 3))

            for rank_idx, sc_info in enumerate(scenario_scores):
                card_col = cols_cards[rank_idx % len(cols_cards)]
                badge_class = "badge-rank-1" if rank_idx == 0 else ("badge-rank-2" if rank_idx == 1 else "badge-rank-3")
                medal = "🥇 Rank 1" if rank_idx == 0 else ("🥈 Rank 2" if rank_idx == 1 else f"🥉 Rank {rank_idx+1}")

                with card_col:
                    with st.container(border=True):
                        st.markdown(f"<span class='{badge_class}'>{medal}</span>", unsafe_allow_html=True)
                        st.markdown(f"#### **{sc_info['name']}**")

                        st.metric(
                            label="Expected Typical Progress",
                            value=f"{sc_info['total_median']:.1f} units",
                            delta=f"{sc_info['best_case'] - sc_info['total_median']:+.1f} best case",
                        )

                        st.write(f"• **Realistic Range:** {sc_info['worst_case']:.1f} to {sc_info['best_case']:.1f} units")

                        if sc_info["avg_prob"] is not None:
                            st.write(f"• **Target Goal Chance:** `{sc_info['avg_prob'] * 100:.0f}%` likelihood")
                        else:
                            st.write(f"• **Target Goal:** Open / Milestone tracking")

                        # Activity Breakdown
                        st.caption("Activities Breakdown:")
                        for act_name, m_sum in sc_info["summaries"].items():
                            st.write(f"  └ *{act_name}:* ~{m_sum.median:.1f} units (range: {m_sum.p10:.1f} - {m_sum.p90:.1f})")

            # -----------------------------------------------------------------
            # 3. VISUAL DISTRIBUTION CHART
            # -----------------------------------------------------------------
            st.markdown("---")
            st.markdown("### 📈 Visual Progress Envelopes")
            st.caption("The colored bars show what you can typically expect. The error bars represent the realistic spread from bad weeks to good weeks.")

            plot_records = []
            for sc_id, sc_res in run.results.items():
                for track, metric in sc_res.track_summaries.items():
                    plot_records.append(
                        {
                            "Alternative": sc_res.scenario_name,
                            "Activity": track,
                            "Expected (Median)": metric.median,
                            "Worst Case (P10)": metric.p10,
                            "Best Case (P90)": metric.p90,
                        }
                    )

            df_plot = pd.DataFrame(plot_records)
            if not df_plot.empty:
                fig = px.bar(
                    df_plot,
                    x="Alternative",
                    y="Expected (Median)",
                    color="Activity",
                    barmode="group",
                    title="Expected Progress by Option & Activity",
                    labels={"Expected (Median)": "Units Mastered / Achieved"},
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

            # -----------------------------------------------------------------
            # 4. OPTIONAL ADVANCED STATISTICAL TABLE (FOR ENGINEERS)
            # -----------------------------------------------------------------
            with st.expander("🔬 Show Advanced Statistical Table (P10, P90, Std Dev for Engineers & Data Science)"):
                st.caption("This detailed table contains the exact mathematical percentiles generated by the Monte Carlo sampling engine.")
                summary_table = []
                for sc_id, sc_res in run.results.items():
                    for track, metric in sc_res.track_summaries.items():
                        summary_table.append(
                            {
                                "Alternative": sc_res.scenario_name,
                                "Activity": track,
                                "Median (P50)": f"{metric.median:.2f}",
                                "Worst Case (P10)": f"{metric.p10:.2f}",
                                "Best Case (P90)": f"{metric.p90:.2f}",
                                "Mean ± Std": f"{metric.mean:.2f} ± {metric.std:.2f}",
                                "P(Target Attained)": f"{metric.threshold_prob * 100:.1f}%" if metric.threshold_prob is not None else "N/A",
                            }
                        )
                st.dataframe(pd.DataFrame(summary_table), use_container_width=True)

                st.download_button(
                    label=tr("export_csv", "📥 Download Simulation Data (CSV)"),
                    data=export_simulation_run_to_csv(run),
                    file_name=f"sim_results_{run.id[:8]}.csv",
                    mime="text/csv",
                )


# -----------------------------------------------------------------------------
# TAB 4: SENSITIVITY & FRAGILITY
# -----------------------------------------------------------------------------
with tab_sensitivity:
    st.subheader(tr("fragility_title", "Assumption Fragility Test"))
    st.markdown(tr("fragility_desc", "Checks if your preferred choice remains best even if things go 20% slower or faster."))

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
    st.subheader(tr("tab_observations", "📈 Real Progress Log"))
    st.markdown(
        "Simulation is only the first half of ParallelMe. As you execute your decision in real life, "
        "log your actual hours and results weekly to see whether reality falls inside the simulated envelope."
    )

    observations = db.list_observations(active_dec.id)

    # Logging Form
    with st.expander(f"📝 {tr('log_progress_title', 'Log Real Life Progress')}", expanded=(len(observations) == 0)):
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
