RUBRICS = {
    "problem_clarity": {
        "name": "Problem Clarity",
        "description": "Is the customer, pain, and frequency specific and real?",
        "weight": 1.0,
        "icon": "🎯"
    },
    "market_size": {
        "name": "Market Size",
        "description": "Is the market large enough to build a venture-scale business?",
        "weight": 1.2,
        "icon": "📊"
    },
    "demand_signals": {
        "name": "Demand Signals",
        "description": "Are people already searching for / complaining about this problem?",
        "weight": 1.0,
        "icon": "📡"
    },
    "competitive_landscape": {
        "name": "Competitive Landscape",
        "description": "How saturated is the market? Is there a real wedge?",
        "weight": 1.0,
        "icon": "⚔️"
    },
    "yc_rfs_alignment": {
        "name": "Market Timing & Tailwinds",
        "description": "Is now the right time? What macro/tech shifts make this viable today?",
        "weight": 0.8,
        "icon": "🏹"
    },
    "ai_era_moat": {
        "name": "AI-Era Moat",
        "description": "Can OpenAI/Google replicate this overnight? What's the defensibility?",
        "weight": 1.5,
        "icon": "🏰"
    }
}

# (threshold /100, label, color_hint, description)
VERDICT_THRESHOLDS = [
    (80, "🚀 Strong Signal — Worth Building",   "green",  "This idea has strong fundamentals. Start validating with real customers now."),
    (60, "🟡 Promising — Validate More",         "orange", "Solid foundation but key uncertainties remain. Run small experiments before going all-in."),
    (40, "🔴 Needs Pivoting",                    "red",    "Core issues detected. Consider pivoting the customer, problem, or approach."),
    (0,  "❌ Pass — Move to Next Idea",           "red",    "Fundamental gaps across multiple dimensions. Your time is better spent on the next idea."),
]
