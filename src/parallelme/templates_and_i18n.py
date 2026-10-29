"""Templates and Multi-language localization dictionary for ParallelMe.

Supports:
- English (EN)
- हिन्दी (Hindi - HI)
- Hinglish (Conversational Roman Hindi - HING)
"""

from typing import Any, Dict, List
from parallelme.models import Decision, Scenario, TrackConfig


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "EN": {
        "app_title": "ParallelMe — Alternative Decision Simulator",
        "app_tagline": "Explore different paths for any real-life decision under uncertainty",
        "select_language": "Language / भाषा",
        "active_decision": "Active Decision",
        "choose_decision": "Choose Decision",
        "create_new_decision": "➕ Create New Decision",
        "decision_title": "Decision Title",
        "decision_desc": "What are you trying to decide?",
        "resource_budget": "Total Available Budget per Week (Hours, Money, or Days)",
        "planning_duration": "Duration / Horizon (Weeks)",
        "template_label": "Choose a Ready-Made Template",
        "btn_create": "Create Decision with Scenarios",
        "btn_delete": "Delete Decision",
        "tab_overview": "📋 Summary & Feasibility",
        "tab_scenarios": "🎛️ Alternative Choices",
        "tab_simulate": "🎲 Simulate Futures",
        "tab_sensitivity": "🔍 Risk & Fragility",
        "tab_observations": "📈 Real Progress Log",
        "resource_audit": "Resource Feasibility Check",
        "budget_ok": "✅ Feasible (Within Budget)",
        "budget_over": "❌ Infeasible (Over Budget)",
        "btn_run_sim": "🚀 Simulate Possible Futures",
        "sim_explainer": "Running 1,000 parallel futures modeling real-world disruptions and variations...",
        "fragility_title": "Assumption Fragility Test",
        "fragility_desc": "Checks if your preferred choice remains best even if things go 20% slower or faster.",
        "log_progress_title": "Log Real Life Progress",
        "export_json": "📥 Export Plan (JSON)",
        "export_csv": "📥 Download Simulation Data (CSV)",
        "upload_json": "Upload Saved Plan",
    },
    "HI": {
        "app_title": "पैरेलल-मी (ParallelMe) — फैसला सिम्युलेटर",
        "app_tagline": "अनिश्चितता के बीच अपने किसी भी फैसले के अलग-अलग नतीजों की तुलना करें",
        "select_language": "Language / भाषा",
        "active_decision": "वर्तमान फैसला",
        "choose_decision": "फैसला चुनें",
        "create_new_decision": "➕ नया फैसला बनाएं",
        "decision_title": "फैसले का नाम",
        "decision_desc": "आप किस बारे में निर्णय लेना चाहते हैं?",
        "resource_budget": "प्रति सप्ताह कुल बजट (घंटे, पैसे या दिन)",
        "planning_duration": "योजना की अवधि (सप्ताह)",
        "template_label": "बना-बनाया टेम्पलेट चुनें",
        "btn_create": "विकल्पों के साथ फैसला बनाएं",
        "btn_delete": "फैसला हटाएं",
        "tab_overview": "📋 सारांश और बजट जांच",
        "tab_scenarios": "🎛️ आपके विकल्प (Scenarios)",
        "tab_simulate": "🎲 भविष्य का सिमुलेशन",
        "tab_sensitivity": "🔍 जोखिम और संवेदनशीलता",
        "tab_observations": "📈 असली प्रगति दर्ज करें",
        "resource_audit": "संसाधन बजट जांच",
        "budget_ok": "✅ संभव (बजट के भीतर)",
        "budget_over": "❌ असंभव (बजट से बाहर)",
        "btn_run_sim": "🚀 संभावित भविष्य सिमुलेट करें",
        "sim_explainer": "वास्तविक जीवन की अनिश्चितताओं को जोड़कर 1,000 संभावित भविष्य देखे जा रहे हैं...",
        "fragility_title": "मान्यताओं की संवेदनशीलता जांच",
        "fragility_desc": "यह जांचता है कि अगर काम 20% धीमा या तेज हो, तब भी आपका चुना विकल्प सबसे अच्छा रहेगा या नहीं।",
        "log_progress_title": "हफ्ते की असली प्रगति दर्ज करें",
        "export_json": "📥 योजना डाउनलोड करें (JSON)",
        "export_csv": "📥 सिमुलेशन डेटा डाउनलोड करें (CSV)",
        "upload_json": "पुरानी योजना अपलोड करें",
    },
    "HING": {
        "app_title": "ParallelMe — Decision Simulator",
        "app_tagline": "Real-life decisions ke alag-alag futures compare karein bina kisi guesswork ke",
        "select_language": "Language / भाषा",
        "active_decision": "Active Decision",
        "choose_decision": "Decision select karein",
        "create_new_decision": "➕ Naya Decision Banayein",
        "decision_title": "Decision ka Title",
        "decision_desc": "Aap kya decide karna chahte hain?",
        "resource_budget": "Per week kitna time/budget available hai (Hours/Days)?",
        "planning_duration": "Kitne weeks ka plan hai?",
        "template_label": "Ready-made Template choose karein",
        "btn_create": "Scenarios ke sath Decision banayein",
        "btn_delete": "Decision delete karein",
        "tab_overview": "📋 Summary & Budget Check",
        "tab_scenarios": "🎛️ Alternative Choices",
        "tab_simulate": "🎲 Futures Simulate Karein",
        "tab_sensitivity": "🔍 Risk & Fragility Check",
        "tab_observations": "📈 Real Progress Log",
        "resource_audit": "Budget Feasibility Check",
        "budget_ok": "✅ Feasible (Budget ke andar hai)",
        "budget_over": "❌ Infeasible (Budget se zyada hours/kharcha)",
        "btn_run_sim": "🚀 Simulation Run Karein",
        "sim_explainer": "Real-world ups and downs ke sath 1,000 parallel outcomes calculate ho rahe hain...",
        "fragility_title": "Fragility & Risk Analysis",
        "fragility_desc": "Check karein ki agar progress 20% slow ya fast ho, toh kya scenario ranking badal jaati hai?",
        "log_progress_title": "Real Progress Entry",
        "export_json": "📥 Plan Export Karein (JSON)",
        "export_csv": "📥 CSV Data Download Karein",
        "upload_json": "Saved JSON Plan Load Karein",
    },
}


def get_prebuilt_templates() -> Dict[str, Dict[str, Any]]:
    """Returns ready-to-use, multi-domain decision templates with 2-3 pre-filled scenarios."""
    return {
        "trip_planning": {
            "title": "🏖️ Goa Trip Planning: Luxury vs Budget vs Roadtrip",
            "description": "Planning a 2-week vacation comparing luxury flight travel, budget train backpacking, and rental roadtrip under a 40-hour / energy budget.",
            "time_horizon_weeks": 2,
            "max_weekly_hours": 40.0,
            "scenarios": [
                {
                    "name": "Option A: Flight + Resort Stay",
                    "description": "Fast travel, maximum relaxation, visits top tourist hubs with minimal transit fatigue.",
                    "allocations": {"Sightseeing": 25.0, "Relaxation": 12.0},
                    "track_configs": {
                        "Sightseeing": TrackConfig(name="Sightseeing", baseline_skill=0.0, velocity_mean=1.5, velocity_sd=0.2),
                        "Relaxation": TrackConfig(name="Relaxation", baseline_skill=0.0, velocity_mean=1.2, velocity_sd=0.15),
                    },
                    "target_thresholds": {"Sightseeing": 30.0, "Relaxation": 20.0},
                },
                {
                    "name": "Option B: Train + Budget Exploration",
                    "description": "Lower cost, longer travel time, authentic local experience exploring offbeat spots.",
                    "allocations": {"Sightseeing": 18.0, "Relaxation": 18.0},
                    "track_configs": {
                        "Sightseeing": TrackConfig(name="Sightseeing", baseline_skill=0.0, velocity_mean=1.1, velocity_sd=0.3),
                        "Relaxation": TrackConfig(name="Relaxation", baseline_skill=0.0, velocity_mean=1.0, velocity_sd=0.2),
                    },
                    "target_thresholds": {"Sightseeing": 25.0, "Relaxation": 20.0},
                },
                {
                    "name": "Option C: Road Trip with Friends",
                    "description": "Drive yourself, visit scenic spots along the highway, high adventure but higher physical exhaustion risk.",
                    "allocations": {"Sightseeing": 28.0, "Relaxation": 8.0},
                    "track_configs": {
                        "Sightseeing": TrackConfig(name="Sightseeing", baseline_skill=0.0, velocity_mean=1.3, velocity_sd=0.35),
                        "Relaxation": TrackConfig(name="Relaxation", baseline_skill=0.0, velocity_mean=0.8, velocity_sd=0.25),
                    },
                    "target_thresholds": {"Sightseeing": 30.0, "Relaxation": 15.0},
                },
            ],
        },
        "fitness_health": {
            "title": "🏋️ 90-Day Health & Body Transformation",
            "description": "Comparing gym strength training vs home HIIT & outdoor running under a 12 hr/week fitness budget.",
            "time_horizon_weeks": 12,
            "max_weekly_hours": 12.0,
            "scenarios": [
                {
                    "name": "Option A: Heavy Gym & Strength Focus",
                    "description": "5 days/week gym weightlifting with 1 day light cardio.",
                    "allocations": {"Strength_Training": 9.0, "Cardio_Mobility": 2.5},
                    "track_configs": {
                        "Strength_Training": TrackConfig(name="Strength_Training", baseline_skill=10.0, velocity_mean=1.2, velocity_sd=0.15),
                        "Cardio_Mobility": TrackConfig(name="Cardio_Mobility", baseline_skill=10.0, velocity_mean=0.8, velocity_sd=0.1),
                    },
                    "target_thresholds": {"Strength_Training": 100.0, "Cardio_Mobility": 30.0},
                },
                {
                    "name": "Option B: Home Workouts + Running",
                    "description": "No commute to gym; high flexibility with calisthenics and outdoor morning runs.",
                    "allocations": {"Strength_Training": 4.5, "Cardio_Mobility": 6.5},
                    "track_configs": {
                        "Strength_Training": TrackConfig(name="Strength_Training", baseline_skill=10.0, velocity_mean=0.9, velocity_sd=0.2),
                        "Cardio_Mobility": TrackConfig(name="Cardio_Mobility", baseline_skill=10.0, velocity_mean=1.3, velocity_sd=0.2),
                    },
                    "target_thresholds": {"Strength_Training": 50.0, "Cardio_Mobility": 80.0},
                },
            ],
        },
        "career_study": {
            "title": "🎓 College Placement Prep: Coding vs Projects",
            "description": "12-week preparation strategy balancing LeetCode problem solving with building full-stack portfolio apps.",
            "time_horizon_weeks": 12,
            "max_weekly_hours": 20.0,
            "scenarios": [
                {
                    "name": "Heavy DSA / Coding Focus",
                    "description": "16 hrs DSA prep, 3 hrs project upkeep.",
                    "allocations": {"DSA_Problems": 16.0, "FullStack_Projects": 3.0},
                    "track_configs": {
                        "DSA_Problems": TrackConfig(name="DSA_Problems", baseline_skill=20.0, velocity_mean=1.2, velocity_sd=0.2),
                        "FullStack_Projects": TrackConfig(name="FullStack_Projects", baseline_skill=10.0, velocity_mean=0.8, velocity_sd=0.2),
                    },
                    "target_thresholds": {"DSA_Problems": 150.0, "FullStack_Projects": 40.0},
                },
                {
                    "name": "Balanced Split (DSA + Projects)",
                    "description": "10 hrs DSA prep, 9 hrs project development.",
                    "allocations": {"DSA_Problems": 10.0, "FullStack_Projects": 9.0},
                    "track_configs": {
                        "DSA_Problems": TrackConfig(name="DSA_Problems", baseline_skill=20.0, velocity_mean=1.1, velocity_sd=0.2),
                        "FullStack_Projects": TrackConfig(name="FullStack_Projects", baseline_skill=10.0, velocity_mean=1.1, velocity_sd=0.2),
                    },
                    "target_thresholds": {"DSA_Problems": 100.0, "FullStack_Projects": 80.0},
                },
            ],
        },
        "purchase_finance": {
            "title": "💰 Commute Decision: Buy Used Bike vs Daily Cabs vs Public Metro",
            "description": "Evaluating a 16-week daily commute plan in time spent and stress/comfort units under an 18 hr/week transit budget.",
            "time_horizon_weeks": 16,
            "max_weekly_hours": 18.0,
            "scenarios": [
                {
                    "name": "Option A: Metro + Walking (Cost Effective)",
                    "description": "Low cost, predictable transit time, reading time available during commute.",
                    "allocations": {"Travel_Time": 12.0, "Productive_Reading": 5.0},
                    "track_configs": {
                        "Travel_Time": TrackConfig(name="Travel_Time", baseline_skill=0.0, velocity_mean=1.0, velocity_sd=0.1),
                        "Productive_Reading": TrackConfig(name="Productive_Reading", baseline_skill=0.0, velocity_mean=1.2, velocity_sd=0.15),
                    },
                    "target_thresholds": {"Productive_Reading": 60.0},
                },
                {
                    "name": "Option B: Buy Used Motorbike (Flexibility)",
                    "description": "Fast door-to-door transit, zero waiting for trains, but traffic fatigue and maintenance time.",
                    "allocations": {"Travel_Time": 7.0, "Productive_Reading": 1.0},
                    "track_configs": {
                        "Travel_Time": TrackConfig(name="Travel_Time", baseline_skill=0.0, velocity_mean=1.0, velocity_sd=0.1),
                        "Productive_Reading": TrackConfig(name="Productive_Reading", baseline_skill=0.0, velocity_mean=0.5, velocity_sd=0.2),
                    },
                    "target_thresholds": {"Travel_Time": 50.0},
                },
            ],
        },
    }


def create_decision_from_template(template_key: str, custom_title: str = "") -> Decision:
    """Helper to instantiate a fully configured Decision object from a prebuilt template."""
    templates = get_prebuilt_templates()
    if template_key not in templates:
        template_key = "career_study"

    tpl = templates[template_key]
    title = custom_title.strip() if custom_title.strip() else tpl["title"]

    scenarios = []
    for sc_data in tpl["scenarios"]:
        sc = Scenario(
            name=sc_data["name"],
            description=sc_data["description"],
            allocations=dict(sc_data["allocations"]),
            track_configs=dict(sc_data["track_configs"]),
            target_thresholds=dict(sc_data["target_thresholds"]),
        )
        scenarios.append(sc)

    decision = Decision(
        title=title,
        description=tpl["description"],
        time_horizon_weeks=tpl["time_horizon_weeks"],
        max_weekly_hours=tpl["max_weekly_hours"],
        scenarios=scenarios,
    )

    # Link scenario decision_ids
    for s in decision.scenarios:
        s.decision_id = decision.id

    return decision
