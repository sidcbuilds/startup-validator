import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# On Streamlit Cloud there is no .env — pull keys from st.secrets into the environment
try:
    for _k in ("LLM_PROVIDER", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "OPENAI_API_KEY", "OPENAI_MODEL"):
        if not os.getenv(_k) and _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

from validator import validate_idea
from rubrics import RUBRICS
from charts import radar_chart, market_opportunity_chart, industry_chart as make_industry_chart
from pdf_export import build_pdf

st.set_page_config(
    page_title="Startup Idea Validator",
    page_icon="🚀",
    layout="wide",
)

st.session_state.setdefault("result", None)
st.session_state.setdefault("inputs", None)

# ── DARK THEME CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #060611 0%, #0d1117 55%, #0a0f1e 100%);
    min-height: 100vh;
}

/* Gradient title text */
h1 {
    background: linear-gradient(90deg, #818cf8 0%, #c084fc 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.4rem !important;
}

/* Subtle glowing caption */
.stCaption { color: #64748b !important; }

/* Form card */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 16px 24px;
}

/* Text inputs & areas */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.28);
    border-radius: 14px;
    padding: 18px !important;
}
[data-testid="metric-container"] label { color: #94a3b8 !important; }

/* Expander header */
details > summary {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
}

/* Progress bar */
[data-testid="stProgressBar"] > div > div > div > div {
    background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
}

/* Submit button */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #7c3aed 0%, #2563eb 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.4px !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.2rem !important;
    transition: opacity 0.2s;
}
[data-testid="stFormSubmitButton"] > button:hover { opacity: 0.88; }

/* Chart containers */
[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 8px;
}

/* Dividers */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Spinner */
[data-testid="stSpinner"] { color: #a78bfa !important; }
</style>
""", unsafe_allow_html=True)


st.title("🚀 Startup Idea Validator")
st.caption(
    "AI-era moat analysis · informed by B-school validation frameworks & YC-style founder questions"
)
st.divider()

# ── FORM (only shown when no result yet) ───────────────────────────────────────
if st.session_state.get("result") is None:
    with st.form("validator_form"):
        col1, col2 = st.columns(2)

        with col1:
            idea = st.text_area(
                "**1. Describe your startup idea** *(required)*",
                placeholder="e.g. An AI tool that helps junior nurses with wound-care.",
                height=110,
            )
            customer = st.text_input(
                "**2. Target customer?** *(required)*",
                placeholder="e.g. Junior nurses at US hospitals",
            )
            problem = st.text_area(
                "**3. What problem & how do you know?** *(required)*",
                placeholder="e.g. Nurses spend 40% of their shift on documentation. I interviewed 12.",
                height=110,
            )

        with col2:
            advantage = st.text_area(
                "**4. Your unfair advantage?** *(optional)*",
                placeholder="e.g. Former ICU nurse with hospital relationships.",
                height=110,
            )
            why_now = st.text_area(
                "**5. Why now?** *(optional)*",
                placeholder="e.g. Multimodal LLMs + record nursing shortages.",
                height=110,
            )

        submitted = st.form_submit_button(
            "🔍 Validate My Idea", use_container_width=True, type="primary"
        )

    if submitted:
        missing = [f for f, v in [("idea", idea), ("customer", customer), ("problem", problem)] if not v.strip()]
        if missing:
            st.error(f"Please fill in: {', '.join(missing)}")
        else:
            inputs = {
                "idea": idea,
                "customer": customer,
                "problem": problem,
                "advantage": advantage,
                "competitors": "Unknown",
                "why_now": why_now,
            }
            with st.spinner("🔬 Researching competitors, market size, demand signals… this takes ~20 seconds"):
                try:
                    result = validate_idea(inputs)
                    st.session_state["result"] = result
                    st.session_state["inputs"] = inputs
                    st.rerun()
                except RuntimeError as e:
                    st.error(f"⚠️ {e}")

# ── RESULTS (shown after validation) ───────────────────────────────────────────
else:
    result = st.session_state["result"]
    inputs = st.session_state["inputs"]
    score = result["weighted_score"]

    # Top action bar
    a1, a2, _ = st.columns([1.4, 1.4, 4])
    with a1:
        if st.button("➕ Validate New Idea", use_container_width=True, type="primary"):
            st.session_state["result"] = None
            st.session_state["inputs"] = None
            st.rerun()
    with a2:
        pdf_bytes = build_pdf(inputs, result)
        st.download_button("📄 Save as PDF", data=pdf_bytes,
                           file_name="startup_validation.pdf", mime="application/pdf",
                           use_container_width=True)

    # ── VERDICT BANNER ────────────────────────────────────────────────────
    st.divider()
    v_col, s_col = st.columns([4, 1])
    with v_col:
        st.markdown(f"## {result['verdict_label']}")
        st.markdown(result["verdict_description"])
        st.markdown(f"*{result['overall_summary']}*")
    with s_col:
        industry_label = result.get("industry", "general").replace("-", " ").title()
        st.metric("Overall Score", f"{score} / 100")
        st.caption(f"📂 Industry: **{industry_label}**")

    if result.get("interpreted_idea"):
        st.info(f"**Here's how I understood your idea:** {result['interpreted_idea']}")

    st.divider()

    # ── CHARTS ────────────────────────────────────────────────────────────
    st.markdown("## 📈 Visual Analysis")
    ch1, ch2, ch3 = st.columns(3)
    with ch1:
        st.plotly_chart(radar_chart(result["scores"]), use_container_width=True)
    with ch2:
        mn = result.get("market_numbers", {})
        st.plotly_chart(market_opportunity_chart(
            float(mn.get("tam_billion", 1)), float(mn.get("sam_billion", 0.2)),
            float(mn.get("som_billion", 0.01))), use_container_width=True)
    with ch3:
        ic = result.get("industry_chart")
        if ic and ic.get("data"):
            st.plotly_chart(make_industry_chart(ic), use_container_width=True)
            st.caption(f"💡 {ic.get('insight', '')}")

    st.divider()

    # ── LOW-SCORE COACHING ────────────────────────────────────────────────
    if score < 60 and result.get("coaching_questions"):
        st.markdown("## 🧭 Let's Sharpen This Idea")
        st.info("Your score suggests room to improve. Reflect on these questions, then validate a stronger version:")
        for q in result["coaching_questions"]:
            st.markdown(f"- ❓ {q}")
        if result.get("pivot_ideas"):
            st.markdown("**💡 Stronger angles in this theme:**")
            for p in result["pivot_ideas"]:
                st.markdown(f"- {p}")
        st.divider()

    # ── RUBRIC BREAKDOWN ──────────────────────────────────────────────────
    st.markdown("## 📊 Rubric Breakdown")
    cols = st.columns(3)
    for i, (key, rubric) in enumerate(RUBRICS.items()):
        sd = result["scores"][key]
        sc = sd["score"]
        dot = "🟢" if sc >= 7 else "🟡" if sc >= 5 else "🔴"
        with cols[i % 3]:
            with st.expander(f"{dot} {rubric['icon']} {rubric['name']} — **{sc}/10** ({sd['grade']})", expanded=True):
                st.progress(sc / 10)
                st.markdown(f"**Finding:** {sd['finding']}")
                st.markdown(f"**Evidence:** {sd['evidence']}")
                st.markdown(f"**To improve:** {sd['recommendation']}")

    st.divider()

    # ── RISKS · OPPORTUNITIES · NEXT STEPS ───────────────────────────────
    r_col, o_col, n_col = st.columns(3)
    with r_col:
        st.markdown("### 🔴 Top Risks")
        for risk in result["top_risks"]:
            st.markdown(f"- {risk}")
    with o_col:
        st.markdown("### 💡 Opportunities")
        for opp in result["top_opportunities"]:
            st.markdown(f"- {opp}")
    with n_col:
        st.markdown("### ✅ Next Steps")
        for step in result["next_steps"]:
            st.markdown(f"- {step}")

    # ── HOW TO SHAPE THIS IDEA ─────────────────────────────────────────────
    if result.get("idea_shaping"):
        st.divider()
        st.markdown("## ✨ How to Shape This Idea")
        st.success(result["idea_shaping"])

    # ── RAW RESEARCH (collapsed) ──────────────────────────────────────────
    with st.expander("🔎 View raw research data"):
        for label, content in [
            ("Competitors found online", result["research"]["competitors"]),
            ("Market size data", result["research"]["market_size"]),
            ("Demand signals", result["research"]["demand_signals"]),
            ("YC / investor activity", result["research"]["yc_alignment"]),
        ]:
            st.markdown(f"**{label}**")
            st.text(content)
            st.markdown("---")
