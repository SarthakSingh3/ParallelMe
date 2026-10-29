"""Streamlit Interactive Application for ParallelMe Decision Simulator.

A human-first decision simulator that connects your daily routine, competing options,
and realistic future simulation in tangible, concrete life terms (no abstract math jargon).
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
    page_title="ParallelMe — Real Decision Simulator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for modern, human-first decision scorecards
st.markdown(
    """
    <style>
    .step-banner {
        background-color: #1f2937;
        border-left: 5px solid #3b82f6;
        padding: 12px 18px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    .winner-card {
        background: linear-gradient(135deg, #1b382b 0%, #11221a 100%);
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 22px;
    }
    .badge-rank-1 {
        background-color: #eab308;
        color: black;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 13px;
    }
    .badge-rank-2 {
        background-color: #94a3b8;
        color: black;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 13px;
    }
    .badge-rank-3 {
        background-color: #b45309;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Database
DB_PATH = Path("parallelme.db")
db = Database(str(DB_PATH))

# Populate pre-built multi-domain starter decisions if database has fewer than 2
existing_decisions = db.list_decisions()
if len(existing_decisions) < 2:
    templates = get_prebuilt_templates()
    for tkey in ["trip_planning", "career_study", "fitness_health"]:
        init_dec = create_decision_from_template(tkey)
        if not any(d.title == init_dec.title for d in existing_decisions):
            db.save_decision(init_dec)

all_decisions = db.list_decisions()

# Session State Initialization
if "lang" not in st.session_state:
    st.session_state["lang"] = "EN"

if "active_decision" not in st.session_state or st.session_state["active_decision"] is None:
    st.session_state["active_decision"] = all_decisions[0] if all_decisions else Decision(title="My Decision")

if "last_simulation_run" not in st.session_state:
    st.session_state["last_simulation_run"] = None


def tr(key: str, default: str = "") -> str:
    lang = st.session_state.get("lang", "EN")
    dict_for_lang = TRANSLATIONS.get(lang, TRANSLATIONS.get("EN", {}))
    if key in dict_for_lang:
        return dict_for_lang[key]
    fallback_en = TRANSLATIONS.get("EN", {})
    return fallback_en.get(key, default or key)


# -----------------------------------------------------------------------------
# SIDEBAR: DECISION SELECTOR & TEMPLATES
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"## ⚖️ **ParallelMe**")
st.sidebar.caption(tr("app_tagline"))

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

# Active Decision Picker
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

active_dec: Decision = st.session_state["active_decision"]

# New Decision Wizard
with st.sidebar.expander(tr("create_new_decision", "➕ Create New Decision"), expanded=False):
    st.markdown("### 🎯 Start with a Decision Template")
    tpl_map = {
        "trip_planning": "🏖️ Vacation & Trip (Flight vs Train vs Roadtrip)",
        "career_study": "🎓 Career / Placement (LeetCode vs Projects)",
        "fitness_health": "🏋️ Fitness Transformation (Gym vs Home HIIT)",
        "custom": "✍️ Custom Decision (Blank with 2 starter options)",
    }
    chosen_tpl = st.selectbox("Choose Category", options=list(tpl_map.keys()), format_func=lambda k: tpl_map[k])
    custom_title_input = st.text_input("Name Your Decision", placeholder="e.g. My Summer Trip or Placement Strategy")

    if st.button("Create Decision", type="primary"):
        if chosen_tpl == "custom":
            new_custom = Decision(
                title=custom_title_input.strip() if custom_title_input.strip() else "My Custom Decision",
                description="Evaluating alternative choices based on my daily routine.",
                time_horizon_weeks=8,
                max_weekly_hours=20.0,
                scenarios=[
                    Scenario(
                        name="Option 1: Focused Plan",
                        description="Prioritizes core activity with 80% time.",
                        allocations={"Core Task": 16.0, "Secondary Task": 2.0},
                        track_configs={
                            "Core Task": TrackConfig(name="Core Task", velocity_mean=1.2),
                            "Secondary Task": TrackConfig(name="Secondary Task", velocity_mean=0.8),
                        },
                        target_thresholds={"Core Task": 90.0},
                    ),
                    Scenario(
                        name="Option 2: Balanced Plan",
                        description="Even split across both activities.",
                        allocations={"Core Task": 9.0, "Secondary Task": 9.0},
                        track_configs={
                            "Core Task": TrackConfig(name="Core Task", velocity_mean=1.0),
                            "Secondary Task": TrackConfig(name="Secondary Task", velocity_mean=1.0),
                        },
                        target_thresholds={"Core Task": 50.0, "Secondary Task": 50.0},
                    ),
                ],
            )
            for s in new_custom.scenarios:
                s.decision_id = new_custom.id
            db.save_decision(new_custom)
            st.session_state["active_decision"] = new_custom
        else:
            created_from_tpl = create_decision_from_template(chosen_tpl, custom_title=custom_title_input)
            db.save_decision(created_from_tpl)
            st.session_state["active_decision"] = created_from_tpl

        st.session_state["last_simulation_run"] = None
        st.success("Decision ready!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Export Decision (JSON)",
    data=export_decision_to_json(active_dec),
    file_name=f"{active_dec.title.replace(' ', '_').lower()}.json",
    mime="application/json",
)


# -----------------------------------------------------------------------------
# MAIN VIEW: 3-STEP HUMAN DECISION JOURNEY
# -----------------------------------------------------------------------------
st.title(f"{active_dec.title}")
if active_dec.description:
    st.caption(f"💡 {active_dec.description}")

tab_step1, tab_step2, tab_step3, tab_sensitivity, tab_observations = st.tabs(
    [
        "1️⃣ Daily Routine & Budget",
        "2️⃣ Your Competing Choices",
        "3️⃣ Real-World Reality Check",
        "🔍 Risk & Fragility",
        "📈 Real Progress Log",
    ]
)


# -----------------------------------------------------------------------------
# STEP 1: DAILY ROUTINE & TIME REALITY
# -----------------------------------------------------------------------------
with tab_step1:
    st.markdown("### ⏰ Step 1: What is your daily routine & how much time do you actually have?")
    st.markdown(
        "A realistic plan starts with your real life. How many hours can you genuinely spend after classes, work, and sleep?"
    )

    with st.container(border=True):
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("##### 📅 Weekday Routine (Monday to Friday)")
            st.caption("How many hours per day can you give after college/job/daily chores?")
            weekday_hrs = st.slider("Hours per weekday", min_value=0.5, max_value=8.0, value=2.5, step=0.5)
            st.write(f"➡️ **Mon – Fri Total:** `{weekday_hrs * 5:.1f} hours`")

        with col_r2:
            st.markdown("##### 🏖️ Weekend Routine (Saturday & Sunday)")
            st.caption("How many hours per day can you dedicate on your free days?")
            weekend_hrs = st.slider("Hours per weekend day", min_value=0.5, max_value=12.0, value=4.0, step=0.5)
            st.write(f"➡️ **Sat – Sun Total:** `{weekend_hrs * 2:.1f} hours`")

        calc_total_weekly = (weekday_hrs * 5.0) + (weekend_hrs * 2.0)
        st.markdown("---")

        col_tot1, col_tot2, col_tot3 = st.columns([2, 1, 1])
        with col_tot1:
            st.markdown(f"#### 🔋 Total Realistic Weekly Capacity: **`{calc_total_weekly:.1f} hours/week`**")
            st.caption("Every alternative scenario you test will be held strictly to this realistic capacity.")

        with col_tot2:
            st.markdown(f"**Planning Duration:**")
            new_weeks = st.number_input("Weeks", min_value=1, max_value=52, value=active_dec.time_horizon_weeks)

        with col_tot3:
            st.write("")
            st.write("")
            if st.button("💾 Update My Routine", type="primary", use_container_width=True):
                active_dec.max_weekly_hours = float(calc_total_weekly)
                active_dec.time_horizon_weeks = int(new_weeks)
                db.save_decision(active_dec)
                st.success("Updated your routine capacity!")
                st.rerun()

    # Feasibility Check
    st.markdown("#### 🛡️ Feasibility Check on Current Choices")
    audit_rows = []
    for sc in active_dec.scenarios:
        allocated = sc.total_planned_hours
        ok = allocated <= active_dec.max_weekly_hours + 1e-9
        audit_rows.append(
            {
                "Choice Name": sc.name,
                "Hours Demanded": f"{allocated:.1f} hrs/week",
                "Your Routine Budget": f"{active_dec.max_weekly_hours:.1f} hrs/week",
                "Feasible?": "✅ Fits within routine" if ok else "❌ Exceeds your time!",
            }
        )
    st.dataframe(pd.DataFrame(audit_rows), use_container_width=True)


# -----------------------------------------------------------------------------
# STEP 2: THE CHOICES YOU'RE WEIGHING (SCENARIOS)
# -----------------------------------------------------------------------------
with tab_step2:
    st.markdown("### 🔀 Step 2: What are the competing choices in your head?")
    st.markdown(
        "Whether you're deciding between **Flight vs Train**, **LeetCode vs Projects**, or **Gym vs Home HIIT**, "
        "add your options here."
    )

    # Display Current Scenarios as Clean Cards
    if not active_dec.scenarios:
        st.warning("⚠️ No options added yet. Use the quick assistant below to add your first option!")
    else:
        st.markdown(f"#### Currently Comparing ({len(active_dec.scenarios)} options)")
        cols_sc = st.columns(min(len(active_dec.scenarios), 3))
        for idx, sc in enumerate(active_dec.scenarios):
            with cols_sc[idx % len(cols_sc)]:
                with st.container(border=True):
                    is_ok = sc.total_planned_hours <= active_dec.max_weekly_hours + 1e-9
                    st.markdown(f"#### 🏷️ **{sc.name}**")
                    if sc.description:
                        st.caption(sc.description)

                    st.markdown(f"**Weekly Time Used:** `{sc.total_planned_hours:.1f}` / `{active_dec.max_weekly_hours:.1f}` hrs")
                    for act, hrs in sc.allocations.items():
                        st.write(f"• **{act}:** {hrs:.1f} hrs/week")

                    if st.button(f"🗑️ Delete Option", key=f"del_sc_{sc.id}", use_container_width=True):
                        active_dec.scenarios = [s for s in active_dec.scenarios if s.id != sc.id]
                        db.save_decision(active_dec)
                        st.rerun()

    st.markdown("---")

    # Conversational Q&A to add another option
    st.markdown("### 💬 Add a New Option in Plain Words")
    st.caption("Tell us what you plan to do in this option. We'll automatically wire it to your routine.")

    with st.container(border=True):
        new_opt_name = st.text_input(
            "1. What do you want to call this option?",
            placeholder="e.g. Flight + Resort Stay, or Intensive Coding Sprint",
        )

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            main_act_name = st.text_input(
                "2. What is the primary activity or output?",
                value="Primary Activity",
                placeholder="e.g. LeetCode Problems, Tourist Spots, Gym Workouts",
            )
            main_act_hrs = st.slider(
                "3. How many hours/week will you give to this?",
                min_value=1.0,
                max_value=float(active_dec.max_weekly_hours),
                value=min(12.0, float(active_dec.max_weekly_hours)),
                step=0.5,
            )

        with col_q2:
            has_sec = st.checkbox("Include a second activity or rest buffer?", value=True)
            sec_act_name = "Secondary Activity"
            sec_act_hrs = 0.0
            if has_sec:
                sec_act_name = st.text_input("Secondary Activity Name", value="Rest / Maintenance")
                remaining = max(0.0, float(active_dec.max_weekly_hours) - main_act_hrs)
                sec_act_hrs = st.slider(
                    "Hours/week for second activity",
                    min_value=0.5,
                    max_value=float(active_dec.max_weekly_hours),
                    value=min(4.0, max(0.5, remaining)),
                    step=0.5,
                )

        target_goal_num = st.number_input("4. What is your target benchmark or goal number? (optional)", min_value=0.0, value=50.0, step=5.0)

        tot_h = main_act_hrs + sec_act_hrs
        if tot_h <= active_dec.max_weekly_hours:
            st.success(f"✅ Uses {tot_h:.1f} / {active_dec.max_weekly_hours:.1f} hrs/week ({active_dec.max_weekly_hours - tot_h:.1f} hrs buffer remaining)")
        else:
            st.error(f"⚠️ Uses {tot_h:.1f} hrs, which exceeds your weekly routine limit of {active_dec.max_weekly_hours:.1f} hrs!")

        if st.button("✨ Save This Choice", type="primary", use_container_width=True):
            if not new_opt_name.strip():
                st.error("Please enter a name for this option.")
            elif tot_h > active_dec.max_weekly_hours + 1e-9:
                st.error("Total hours exceed your available weekly budget. Adjust the sliders.")
            else:
                allocs = {main_act_name.strip(): float(main_act_hrs)}
                configs = {main_act_name.strip(): TrackConfig(name=main_act_name.strip(), velocity_mean=1.1)}
                thresholds = {main_act_name.strip(): float(target_goal_num)} if target_goal_num > 0 else {}

                if has_sec and sec_act_name.strip() and sec_act_hrs > 0:
                    allocs[sec_act_name.strip()] = float(sec_act_hrs)
                    configs[sec_act_name.strip()] = TrackConfig(name=sec_act_name.strip(), velocity_mean=1.0)

                new_choice = Scenario(
                    decision_id=active_dec.id,
                    name=new_opt_name.strip(),
                    description=f"Allocates {main_act_hrs:.1f} hrs to {main_act_name}" + (f" and {sec_act_hrs:.1f} hrs to {sec_act_name}" if has_sec else ""),
                    allocations=allocs,
                    track_configs=configs,
                    target_thresholds=thresholds,
                )
                active_dec.scenarios.append(new_choice)
                db.save_decision(active_dec)
                st.success(f"Saved choice '{new_opt_name}'!")
                st.rerun()


# -----------------------------------------------------------------------------
# STEP 3: REAL-WORLD REALITY CHECK (SIMULATION IN HUMAN TERMS)
# -----------------------------------------------------------------------------
with tab_step3:
    st.markdown("### 🔮 Step 3: Real-World Reality Check (Simulation)")
    st.markdown(
        "Life isn't a neat spreadsheet. Some days you get sick, traffic delays happen, or work piles up. "
        "ParallelMe runs **1,000 parallel simulations** across your weeks to show what will **actually happen** in reality."
    )

    if len(active_dec.scenarios) < 2:
        st.warning("⚠️ You need at least 2 options to compare. Add another choice in Step 2!")
    else:
        col_btn, col_info = st.columns([2, 4])
        with col_btn:
            trigger_sim = st.button("🚀 Run Reality Check Simulation", type="primary", use_container_width=True)
        with col_info:
            st.caption("Simulates 1,000 possible futures with fatigue, schedule disruptions, and real-world variance.")

        if trigger_sim:
            with st.spinner("Simulating 1,000 real-world futures under schedule volatility..."):
                run_snapshot = run_simulation(decision=active_dec, iterations=1000, random_seed=42)
                db.save_run(run_snapshot)
                st.session_state["last_simulation_run"] = run_snapshot
                st.success("✅ Simulation complete!")

        run = st.session_state.get("last_simulation_run")
        if run is not None:
            st.markdown("---")

            # Collect results
            sc_ranks = []
            for sc_id, sc_res in run.results.items():
                total_progress = sum(m.median for m in sc_res.track_summaries.values())
                worst_case = sum(m.p10 for m in sc_res.track_summaries.values())
                best_case = sum(m.p90 for m in sc_res.track_summaries.values())
                volatility = best_case - worst_case

                sc_ranks.append(
                    {
                        "id": sc_id,
                        "name": sc_res.scenario_name,
                        "total_progress": total_progress,
                        "worst_case": worst_case,
                        "best_case": best_case,
                        "volatility": volatility,
                        "summaries": sc_res.track_summaries,
                    }
                )

            # Sort by total output descending
            sc_ranks.sort(key=lambda x: x["total_progress"], reverse=True)
            winner = sc_ranks[0]
            safest = min(sc_ranks, key=lambda x: x["volatility"])

            # 1. PLAIN-LANGUAGE EXECUTIVE TAKEAWAY
            with st.container(border=True):
                st.markdown(f"### 💡 **Executive Takeaway for You**")
                st.markdown(
                    f"🏆 **Top Choice for Maximum Results:** **{winner['name']}**  \n"
                    f"This option gives you the highest total achievement across your {active_dec.time_horizon_weeks} weeks. "
                    f"Even on tough weeks with disruptions, you will still hit a solid **~{winner['worst_case']:.0f}**, "
                    f"and up to **~{winner['best_case']:.0f}** when things go smoothly."
                )
                if safest['id'] != winner['id']:
                    st.info(
                        f"🛡️ **Alternative for Peace of Mind:** If you hate burnout and want the most predictable routine, "
                        f"**{safest['name']}** has the lowest uncertainty spread."
                    )

            # 2. CONCRETE TANGIBLE SCORECARDS (NO MYSTERIOUS "UNITS")
            st.markdown("### 🎴 Side-by-Side Reality Scorecards")
            cols_c = st.columns(min(len(sc_ranks), 3))

            for rank_i, sc_data in enumerate(sc_ranks):
                col_box = cols_c[rank_i % len(cols_c)]
                badge_class = "badge-rank-1" if rank_i == 0 else ("badge-rank-2" if rank_i == 1 else "badge-rank-3")
                medal = "🥇 Rank 1" if rank_i == 0 else ("🥈 Rank 2" if rank_i == 1 else f"🥉 Rank {rank_i+1}")

                with col_box:
                    with st.container(border=True):
                        st.markdown(f"<span class='{badge_class}'>{medal}</span>", unsafe_allow_html=True)
                        st.markdown(f"### **{sc_data['name']}**")

                        # Concrete, specific breakdown of what they actually get!
                        st.markdown("**What you will realistically achieve:**")
                        for act_name, m_sum in sc_data["summaries"].items():
                            st.write(
                                f"• **{act_name}:**  \n"
                                f"  👉 **~{m_sum.median:.0f} achieved** *(range: {m_sum.p10:.0f} to {m_sum.p90:.0f})*"
                            )
                            if m_sum.threshold_prob is not None:
                                st.caption(f"  🎯 Chance of hitting goal: **{m_sum.threshold_prob * 100:.0f}%**")

            # 3. VISUAL BAR CHART
            st.markdown("---")
            st.markdown("### 📊 Visual Progress Comparison")
            chart_records = []
            for sc_data in sc_ranks:
                for act_name, m_sum in sc_data["summaries"].items():
                    chart_records.append(
                        {
                            "Choice": sc_data["name"],
                            "Activity": act_name,
                            "Expected Progress": m_sum.median,
                        }
                    )
            if chart_records:
                fig = px.bar(
                    pd.DataFrame(chart_records),
                    x="Choice",
                    y="Expected Progress",
                    color="Activity",
                    barmode="group",
                    title="Expected Real Achievements across Alternatives",
                )
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)

            # 4. OPTIONAL ADVANCED DATA (COLLAPSED)
            with st.expander("🔬 View Deep Technical Statistics (For Data Science & QA)"):
                st.caption("Raw percentile distribution tables ($P_{10}$, $P_{50}$, $P_{90}$) from Monte Carlo draws.")
                adv_rows = []
                for sc_data in sc_ranks:
                    for act_name, m_sum in sc_data["summaries"].items():
                        adv_rows.append(
                            {
                                "Choice": sc_data["name"],
                                "Activity": act_name,
                                "Median (P50)": f"{m_sum.median:.2f}",
                                "Worst Case (P10)": f"{m_sum.p10:.2f}",
                                "Best Case (P90)": f"{m_sum.p90:.2f}",
                                "Standard Deviation": f"{m_sum.std:.2f}",
                            }
                        )
                st.dataframe(pd.DataFrame(adv_rows), use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 4: RISK & FRAGILITY ANALYSIS
# -----------------------------------------------------------------------------
with tab_sensitivity:
    st.subheader("🔍 Assumption Fragility & Risk Test")
    st.markdown("Does your best option remain the best even if things go 20% slower or faster than expected?")

    if len(active_dec.scenarios) < 2:
        st.warning("You need at least 2 options to test ranking fragility.")
    else:
        all_acts = set()
        for sc in active_dec.scenarios:
            all_acts.update(sc.allocations.keys())

        if not all_acts:
            st.info("No activities configured.")
        else:
            col_t1, col_t2 = st.columns(2)
            chosen_act = col_t1.selectbox("Activity to test", options=list(all_acts))
            pct = col_t2.slider("Test Variation (±%)", min_value=10, max_value=40, value=20)

            if st.button("Check If My Decision Is Fragile", type="primary"):
                with st.spinner("Checking ranking stability..."):
                    fragility = check_scenario_ranking_fragility(
                        decision=active_dec,
                        scenarios=active_dec.scenarios,
                        target_track=chosen_act,
                        param_name="velocity_mean",
                        perturbation_pct=pct / 100.0,
                        iterations=500,
                        random_seed=42,
                    )
                    if fragility["is_fragile"]:
                        st.error(
                            f"⚠️ **Fragile Decision:** Varying your speed by ±{pct}% flips which choice is number 1! "
                            "This means the decision is delicate; stay disciplined."
                        )
                    else:
                        st.success(
                            f"🛡️ **Robust Decision:** Even if your pace varies by ±{pct}%, "
                            "the winning choice remains the winning choice. You can proceed with high confidence!"
                        )


# -----------------------------------------------------------------------------
# TAB 5: REAL PROGRESS LOG
# -----------------------------------------------------------------------------
with tab_observations:
    st.subheader("📈 Log Real Progress")
    st.markdown("As you live out your decision, log your actual weekly hours and achievements here to see how reality compares to simulation.")

    observations = db.list_observations(active_dec.id)

    with st.expander("📝 Log This Week's Reality", expanded=(len(observations) == 0)):
        if not active_dec.scenarios:
            st.warning("Define options first.")
        else:
            with st.form("log_form_v3"):
                sc_choices = {s.id: s.name for s in active_dec.scenarios}
                chosen_id = st.selectbox("Which option did you follow this week?", options=list(sc_choices.keys()), format_func=lambda sid: sc_choices[sid])
                wk_num = st.number_input("Week #", min_value=1, max_value=active_dec.time_horizon_weeks, value=min(len(observations)+1, active_dec.time_horizon_weeks))

                exec_sc = next(s for s in active_dec.scenarios if s.id == chosen_id)
                actual_h = {}
                actual_u = {}
                for a in exec_sc.allocations.keys():
                    c1, c2 = st.columns(2)
                    actual_h[a] = c1.number_input(f"{a} Actual Hours", min_value=0.0, max_value=168.0, value=exec_sc.allocations[a])
                    actual_u[a] = c2.number_input(f"{a} Units/Output Achieved", min_value=0.0, max_value=10000.0, value=0.0)

                notes = st.text_input("Notes / Life events this week")

                if st.form_submit_button("Save Week's Log", type="primary"):
                    new_ob = Observation(
                        decision_id=active_dec.id,
                        scenario_id=chosen_id,
                        week_number=int(wk_num),
                        actual_hours=actual_h,
                        actual_units=actual_u,
                        notes=notes,
                    )
                    db.save_observation(new_ob)
                    st.success(f"Recorded Week {wk_num} log!")
                    st.rerun()

    if observations:
        st.markdown(f"#### Logged Entries ({len(observations)})")
        obs_tbl = []
        for o in observations:
            sc_n = next((s.name for s in active_dec.scenarios if s.id == o.scenario_id), "Unknown")
            obs_tbl.append(
                {
                    "Week": f"Week {o.week_number}",
                    "Option Executed": sc_n,
                    "Hours Spent": json.dumps(o.actual_hours),
                    "Actual Output": json.dumps(o.actual_units),
                    "Notes": o.notes,
                    "Date": o.logged_at[:10],
                }
            )
        st.dataframe(pd.DataFrame(obs_tbl), use_container_width=True)

        if len(observations) < 30:
            st.info(
                f"ℹ️ **Observations Logged: {len(observations)} / 30.** "
                "Automatic model recalibration remains disabled until at least 30 observations are recorded to protect against overfitting."
            )
