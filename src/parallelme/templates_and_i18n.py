"""Templates, Daily Routine Calculator, and Multi-language localization dictionary for ParallelMe.

Supports:
- English (EN)
- हिन्दी (Hindi - HI)
- Hinglish (Conversational Roman Hindi - HING)
"""

from typing import Any, Dict, List
from parallelme.models import Decision, Scenario, TrackConfig


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "EN": {
        "app_title": "ParallelMe — Real-Life Decision Simulator",
        "app_tagline": "Compare competing life choices using your real daily routine — no guesswork, no tech jargon.",
        "select_language": "Language / भाषा",
        "active_decision": "Active Decision",
        "choose_decision": "Choose Decision",
        "create_new_decision": "➕ Create New Decision",
        "step1_title": "1️⃣ What are you deciding & what's your routine?",
        "step2_title": "2️⃣ The Choices You're Weighing",
        "step3_title": "3️⃣ Real-World Reality Check (Simulation)",
        "daily_routine_title": "⏰ Calculate from Your Daily Routine",
        "weekday_hours": "Hours available per weekday (Mon – Fri)",
        "weekend_hours": "Hours available per weekend day (Sat – Sun)",
        "total_calculated_budget": "Total Available Time:",
        "wizard_title": "💬 Add a New Option in Plain Words",
        "q1_name": "What is this option called?",
        "q1_placeholder": "e.g. Flight + Resort Stay, or Heavy DSA Preparation",
        "q2_main_activity": "What is the primary activity or achievement?",
        "q2_main_placeholder": "e.g. LeetCode Problems, Places Visited, Gym Sessions",
        "q3_hours": "How many hours/week will you dedicate to this?",
        "q4_second_activity": "Do you also want a second activity alongside it?",
        "q4_second_placeholder": "e.g. Relaxation Hours, Project Work, Cardio",
        "q5_second_hours": "How many hours/week for this second activity?",
        "q6_goal": "What is your target goal? (e.g. 100 problems, 20 places, 40 sessions)",
        "btn_add_scenario": "✨ Add This Choice",
        "btn_run_sim": "🔮 Compare These Futures",
        "tab_simulate": "3️⃣ Real-World Reality Check",
    },
    "HI": {
        "app_title": "पैरेलल-मी (ParallelMe) — जीवन के फैसलों का सिम्युलेटर",
        "app_tagline": "अपनी असली दिनचर्या के आधार पर विकल्पों की तुलना करें — बिना किसी जटिल तकनीक के।",
        "select_language": "Language / भाषा",
        "active_decision": "वर्तमान फैसला",
        "choose_decision": "फैसला चुनें",
        "create_new_decision": "➕ नया फैसला बनाएं",
        "step1_title": "1️⃣ आप क्या फैसला लेना चाहते हैं और दिनचर्या क्या है?",
        "step2_title": "2️⃣ आपके दिमाग में कौन-से विकल्प हैं?",
        "step3_title": "3️⃣ वास्तविक नतीजों की तुलना (सिमुलेशन)",
        "daily_routine_title": "⏰ अपनी दिनचर्या से समय निकालें",
        "weekday_hours": "सोमवार से शुक्रवार: प्रतिदिन कितने घंटे दे सकते हैं?",
        "weekend_hours": "शनिवार-रविवार: प्रतिदिन कितने घंटे दे सकते हैं?",
        "total_calculated_budget": "कुल उपलब्ध साप्ताहिक समय:",
        "wizard_title": "💬 आसान शब्दों में नया विकल्प जोड़ें",
        "q1_name": "इस विकल्प का क्या नाम रखेंगे?",
        "q1_placeholder": "जैसे: फ्लाइट से रिसॉर्ट में ठहरना, या रोज़ 4 घंटे कोडिंग",
        "q2_main_activity": "सबसे मुख्य काम क्या होगा?",
        "q2_main_placeholder": "जैसे: LeetCode सवाल, घूमने की जगहें, जिम वर्कआउट",
        "q3_hours": "इसके लिए हर हफ्ते कितने घंटे देंगे?",
        "q4_second_activity": "क्या साथ में कोई दूसरा काम भी करेंगे?",
        "q4_second_placeholder": "जैसे: आराम का समय, प्रोजेक्ट बनाना, कार्डियो",
        "q5_second_hours": "इस दूसरे काम के लिए प्रति हफ्ते कितने घंटे देंगे?",
        "q6_goal": "आपका लक्ष्य क्या है? (जैसे: 100 सवाल, 20 जगहें, 45 जिम सेशन)",
        "btn_add_scenario": "✨ यह विकल्प जोड़ें",
        "btn_run_sim": "🔮 नतीजों की तुलना करें",
        "tab_simulate": "3️⃣ वास्तविक नतीजों की तुलना",
    },
    "HING": {
        "app_title": "ParallelMe — Real Decision Simulator",
        "app_tagline": "Apne daily routine ke hisaab se options compare karein bina kisi confusion ke.",
        "select_language": "Language / भाषा",
        "active_decision": "Active Decision",
        "choose_decision": "Decision Select Karein",
        "create_new_decision": "➕ Naya Decision Banayein",
        "step1_title": "1️⃣ Kya decide karna hai aur aapka daily routine kaisa hai?",
        "step2_title": "2️⃣ Aapke Options (Choices)",
        "step3_title": "3️⃣ Real-World Comparison (Simulation)",
        "daily_routine_title": "⏰ Daily Routine se Total Time Calculate Karein",
        "weekday_hours": "Mon-Fri: Roz kitne hours nikaal sakte hain?",
        "weekend_hours": "Sat-Sun: Roz kitne hours de sakte hain?",
        "total_calculated_budget": "Total Available Weekly Time:",
        "wizard_title": "💬 Simple Words Mein Naya Option Banayein",
        "q1_name": "Is option ka kya naam rakhna chahenge?",
        "q1_placeholder": "jaise: Flight + Resort Stay, ya Heavy Coding Routine",
        "q2_main_activity": "Main activity ya output kya hoga?",
        "q2_main_placeholder": "jaise: LeetCode Problems, Places Visited, Gym Sessions",
        "q3_hours": "Iske liye weekly kitne hours allocate karenge?",
        "q4_second_activity": "Kya koi second activity bhi sath mein karni hai?",
        "q4_second_placeholder": "jaise: Chill / Rest Time, Projects, Cardio",
        "q5_second_hours": "Is second activity ke liye weekly kitne hours?",
        "q6_goal": "Aapka target goal kya hai? (jaise: 100 problems, 20 places, 40 workouts)",
        "btn_add_scenario": "✨ Ye Option Add Karein",
        "btn_run_sim": "🔮 Futures Compare Karein",
        "tab_simulate": "3️⃣ Real-World Comparison",
    },
}


def get_prebuilt_templates() -> Dict[str, Dict[str, Any]]:
    """Returns human-relatable decision templates with realistic names and physical units."""
    return {
        "trip_planning": {
            "title": "🏖️ Goa Vacation: Flight + Resort vs Budget Train vs Road Trip",
            "description": "Planning a 2-week vacation comparing luxury flight travel, budget train backpacking, and roadtrip under a 35-hour energy/outing budget.",
            "time_horizon_weeks": 2,
            "max_weekly_hours": 35.0,
            "scenarios": [
                {
                    "name": "Option A: Flight + Resort Stay",
                    "description": "Fast flight travel, premium beachside stay, high energy for exploring top spots with minimal exhaustion.",
                    "allocations": {"🏖️ Tourist Spots Explored": 22.0, "🌴 Relax & Chill Hours": 10.0},
                    "track_configs": {
                        "🏖️ Tourist Spots Explored": TrackConfig(name="🏖️ Tourist Spots Explored", baseline_skill=0.0, velocity_mean=0.8, velocity_sd=0.15),
                        "🌴 Relax & Chill Hours": TrackConfig(name="🌴 Relax & Chill Hours", baseline_skill=0.0, velocity_mean=1.0, velocity_sd=0.1),
                    },
                    "target_thresholds": {"🏖️ Tourist Spots Explored": 15.0},
                },
                {
                    "name": "Option B: Budget Train & Hostels",
                    "description": "Saves money, longer train journey, exploring authentic local cafes and offbeat beaches at a relaxed pace.",
                    "allocations": {"🏖️ Tourist Spots Explored": 14.0, "🌴 Relax & Chill Hours": 18.0},
                    "track_configs": {
                        "🏖️ Tourist Spots Explored": TrackConfig(name="🏖️ Tourist Spots Explored", baseline_skill=0.0, velocity_mean=0.6, velocity_sd=0.15),
                        "🌴 Relax & Chill Hours": TrackConfig(name="🌴 Relax & Chill Hours", baseline_skill=0.0, velocity_mean=1.0, velocity_sd=0.1),
                    },
                    "target_thresholds": {"🏖️ Tourist Spots Explored": 10.0},
                },
                {
                    "name": "Option C: Road Trip with Friends",
                    "description": "Drive yourself, visit viewpoints on the way, maximum road adventure but higher driving fatigue.",
                    "allocations": {"🏖️ Tourist Spots Explored": 24.0, "🌴 Relax & Chill Hours": 8.0},
                    "track_configs": {
                        "🏖️ Tourist Spots Explored": TrackConfig(name="🏖️ Tourist Spots Explored", baseline_skill=0.0, velocity_mean=0.75, velocity_sd=0.2),
                        "🌴 Relax & Chill Hours": TrackConfig(name="🌴 Relax & Chill Hours", baseline_skill=0.0, velocity_mean=0.8, velocity_sd=0.2),
                    },
                    "target_thresholds": {"🏖️ Tourist Spots Explored": 16.0},
                },
            ],
        },
        "career_study": {
            "title": "🎓 Campus Placement: LeetCode vs Full-Stack Projects",
            "description": "12-week preparation strategy balancing algorithmic problem-solving with building deployable portfolio web applications.",
            "time_horizon_weeks": 12,
            "max_weekly_hours": 20.0,
            "scenarios": [
                {
                    "name": "Option A: Heavy LeetCode Focus",
                    "description": "16 hrs/week on algorithmic coding problems, 2 hrs/week maintaining projects.",
                    "allocations": {"💻 LeetCode Problems Solved": 16.0, "🚀 Projects Built": 2.0},
                    "track_configs": {
                        "💻 LeetCode Problems Solved": TrackConfig(name="💻 LeetCode Problems Solved", baseline_skill=15.0, velocity_mean=1.1, velocity_sd=0.18),
                        "🚀 Projects Built": TrackConfig(name="🚀 Projects Built", baseline_skill=1.0, velocity_mean=0.15, velocity_sd=0.05),
                    },
                    "target_thresholds": {"💻 LeetCode Problems Solved": 120.0},
                },
                {
                    "name": "Option B: Balanced Coding + Projects",
                    "description": "10 hrs/week on DSA problems and 8 hrs/week actively building full-stack web projects.",
                    "allocations": {"💻 LeetCode Problems Solved": 10.0, "🚀 Projects Built": 8.0},
                    "track_configs": {
                        "💻 LeetCode Problems Solved": TrackConfig(name="💻 LeetCode Problems Solved", baseline_skill=15.0, velocity_mean=1.0, velocity_sd=0.18),
                        "🚀 Projects Built": TrackConfig(name="🚀 Projects Built", baseline_skill=1.0, velocity_mean=0.35, velocity_sd=0.1),
                    },
                    "target_thresholds": {"💻 LeetCode Problems Solved": 80.0, "🚀 Projects Built": 3.0},
                },
            ],
        },
        "fitness_health": {
            "title": "🏋️ 90-Day Transformation: Gym Workouts vs Home HIIT",
            "description": "Comparing gym weightlifting vs home calisthenics & outdoor running based on your realistic weekly free time.",
            "time_horizon_weeks": 12,
            "max_weekly_hours": 10.0,
            "scenarios": [
                {
                    "name": "Option A: 5-Day Gym Weightlifting",
                    "description": "Dedicated gym sessions with weights, focusing on muscle hypertrophy and progressive overload.",
                    "allocations": {"💪 Gym Workouts Completed": 7.5, "🏃 Cardio / Running (Km)": 2.0},
                    "track_configs": {
                        "💪 Gym Workouts Completed": TrackConfig(name="💪 Gym Workouts Completed", baseline_skill=0.0, velocity_mean=0.8, velocity_sd=0.1),
                        "🏃 Cardio / Running (Km)": TrackConfig(name="🏃 Cardio / Running (Km)", baseline_skill=0.0, velocity_mean=4.0, velocity_sd=0.5),
                    },
                    "target_thresholds": {"💪 Gym Workouts Completed": 45.0},
                },
                {
                    "name": "Option B: Home HIIT & Outdoor Running",
                    "description": "Zero travel time to gym; flexible morning home workouts with park running sessions.",
                    "allocations": {"💪 Gym Workouts Completed": 3.5, "🏃 Cardio / Running (Km)": 5.5},
                    "track_configs": {
                        "💪 Gym Workouts Completed": TrackConfig(name="💪 Gym Workouts Completed", baseline_skill=0.0, velocity_mean=0.8, velocity_sd=0.1),
                        "🏃 Cardio / Running (Km)": TrackConfig(name="🏃 Cardio / Running (Km)", baseline_skill=0.0, velocity_mean=5.0, velocity_sd=0.5),
                    },
                    "target_thresholds": {"🏃 Cardio / Running (Km)": 150.0},
                },
            ],
        },
        "purchase_finance": {
            "title": "💰 Commute Decision: Buy Used Bike vs Metro vs Cabs",
            "description": "Evaluating a daily commute plan balancing travel time with reading/rest time.",
            "time_horizon_weeks": 16,
            "max_weekly_hours": 18.0,
            "scenarios": [
                {
                    "name": "Option A: Metro + Walking",
                    "description": "Low cost, predictable transit time with reading time available.",
                    "allocations": {"⏱️ Travel Hours": 12.0, "📖 Reading / Audiobooks": 5.0},
                    "track_configs": {
                        "⏱️ Travel Hours": TrackConfig(name="⏱️ Travel Hours", baseline_skill=0.0, velocity_mean=1.0),
                        "📖 Reading / Audiobooks": TrackConfig(name="📖 Reading / Audiobooks", baseline_skill=0.0, velocity_mean=1.2),
                    },
                    "target_thresholds": {"📖 Reading / Audiobooks": 50.0},
                },
                {
                    "name": "Option B: Buy Motorbike",
                    "description": "Door to door convenience, zero waiting, but higher traffic fatigue.",
                    "allocations": {"⏱️ Travel Hours": 7.0, "📖 Reading / Audiobooks": 1.0},
                    "track_configs": {
                        "⏱️ Travel Hours": TrackConfig(name="⏱️ Travel Hours", baseline_skill=0.0, velocity_mean=1.0),
                        "📖 Reading / Audiobooks": TrackConfig(name="📖 Reading / Audiobooks", baseline_skill=0.0, velocity_mean=0.5),
                    },
                    "target_thresholds": {"⏱️ Travel Hours": 50.0},
                },
            ],
        },
    }


def create_decision_from_template(template_key: str, custom_title: str = "") -> Decision:
    """Helper to instantiate a fully configured Decision object from a prebuilt template."""
    templates = get_prebuilt_templates()
    if template_key not in templates:
        template_key = "trip_planning"

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

    for s in decision.scenarios:
        s.decision_id = decision.id

    return decision
