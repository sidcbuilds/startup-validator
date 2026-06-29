import json
import os

from openai import OpenAI, RateLimitError, AuthenticationError, BadRequestError
from rubrics import RUBRICS, VERDICT_THRESHOLDS
from research import research_idea

def _provider() -> str:
    return os.getenv("LLM_PROVIDER", "openai").lower()


def _get_client():
    global client
    if client is None:
        if _provider() == "anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client

YC_RFS_2026 = """
1. AI for Product Management — AI that decides WHAT to build, not just how
2. AI-Native Hedge Funds — agents parsing 10-Ks, earnings calls, discovering alpha
3. AI-Native Agencies — service businesses rebuilt with AI margins (design, legal, ads)
4. Stablecoin Financial Services — compliant crypto-native financial products
5. AI for Government — back-office automation for public agencies
6. Modern Metal Mills — software-driven manufacturing with shorter lead times
7. AI Guidance for Physical Work — real-time coaching for field/factory/healthcare workers
8. Large Spatial Models — AI that reasons about 2D/3D space and physical environments
9. Infra for Government Fraud Hunters — tools to accelerate False Claims Act cases
10. Make LLMs Easy to Train — datasets, GPU infra, tooling for fine-tuning
"""


def _build_prompt(inputs: dict, research: dict) -> str:
    def _opt(v):
        v = (v or "").strip()
        return v if v else "(not provided — infer the most reasonable assumption yourself)"

    return f"""You are a senior startup advisor and investor evaluating a startup idea.
Use the founder's inputs as the foundation, but EXPAND on them: enrich the customer,
deepen the problem, infer plausible competitors, and assess fit and timing. Don't penalize
the idea for brevity — fill gaps with reasonable assumptions. Use the web research to ground
your reasoning. Score across 6 rubrics.

## FOUNDER INPUTS
- Idea: {inputs['idea']}
- Target Customer: {_opt(inputs.get('customer'))}
- Problem & Evidence: {_opt(inputs.get('problem'))}
- Unfair Advantage: {_opt(inputs.get('advantage'))}
- Why Now: {_opt(inputs.get('why_now'))}

## WEB RESEARCH

Competitors found online:
{research['competitors']}

Market size data:
{research['market_size']}

Demand signals (forums, discussions, complaints):
{research['demand_signals']}

YC / investor activity in this space:
{research['yc_alignment']}

## MARKET TIMING CONTEXT (current high-conviction startup themes — directional, not a checklist)
{YC_RFS_2026}

## SCORING INSTRUCTIONS

Score each rubric 1–10. Return ONLY valid JSON in this exact structure:

{{
  "interpreted_idea": "<2-3 sentence expansion: the customer, problem, and solution you inferred from the one-liner>",
  "scores": {{
    "problem_clarity": {{
      "score": <int 1-10>,
      "grade": "<A/B/C/D/F>",
      "finding": "<one sentence key finding>",
      "evidence": "<what specific evidence supports this score>",
      "recommendation": "<one concrete action to improve this score>"
    }},
    "market_size": {{ <same structure> }},
    "demand_signals": {{ <same structure> }},
    "competitive_landscape": {{ <same structure> }},
    "yc_rfs_alignment": {{ <same structure> }},
    "ai_era_moat": {{ <same structure> }}
  }},
  "overall_summary": "<2-3 sentence overall assessment>",
  "top_risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
  "top_opportunities": ["<opportunity 1>", "<opportunity 2>"],
  "next_steps": ["<concrete next step 1>", "<concrete next step 2>", "<concrete next step 3>"],
  "coaching_questions": ["<probing question 1>", "<probing question 2>", "<probing question 3>", "<probing question 4>"],
  "pivot_ideas": ["<sharper variation of this idea in the same theme>", "<another stronger angle in the same theme>"],
  "idea_shaping": "<3-4 sentence closing summary: how to shape this idea into a stronger, more fundable version — the sharpest customer, the tightest wedge, and the moat to build>",
  "industry": "<primary industry slug, e.g. healthcare, fintech, edtech, saas, legaltech, proptech, manufacturing, climatetech, ai-infra, govtech>",
  "market_numbers": {{
    "tam_billion": <estimated TAM in USD billions as a decimal number, e.g. 45.2>,
    "sam_billion": <estimated SAM in USD billions as a decimal number, e.g. 8.0>,
    "som_billion": <realistic first 3-year achievable market in USD billions, e.g. 0.05 for $50M>
  }},
  "industry_chart": {{
    "title": "<specific descriptive title e.g. 'US Healthcare AI Market Growth ($B)'>",
    "type": "<line or bar>",
    "x_label": "<x axis label e.g. Year or Category>",
    "y_label": "<y axis label with unit e.g. Market Size ($B) or % Adoption>",
    "data": [{{"x": "<label>", "y": <number>}}, ...],
    "insight": "<1 sentence specific insight from this data relevant to the startup idea>"
  }}
}}

INDUSTRY CHART GUIDELINES:
- Show 6-8 data points of a real and relevant trend for the industry (e.g. market growth by year, adoption rates, problem severity stats)
- Use realistic, research-backed numbers (not made up)
- For healthcare: show healthcare AI market growth by year, nurse shortage trend, or documentation burden stats
- For fintech: show digital payments volume, fraud loss rates, or neobank adoption
- For SaaS/AI: show AI tool adoption rates, compute cost trends, or developer tool market growth
- Use "line" type for time-series trends, "bar" for category comparisons

SCORING RUBRICS:
- problem_clarity:       9-10=crystal clear customer+pain+frequency with evidence; 1-3=vague idea, no real insight
- market_size:           9-10=>$10B TAM with clear path to $1B+ revenue; 1-3=tiny niche or unclear market
- demand_signals:        9-10=active Reddit threads, high search volume, vocal complaints; 1-3=no evidence anyone cares
- competitive_landscape: 9-10=clear gap, weak/absent direct competitors; 1-3=saturated with entrenched players
- yc_rfs_alignment:      9-10=directly maps to a YC RFS 2026 theme with great timing; 1-3=no alignment, bad timing
- ai_era_moat:           9-10=data moat + network effects + high switching costs; 1-3=pure GPT wrapper, replaced overnight

Be honest and critical. A mediocre idea should score 4-6, not 7-8.

COACHING GUIDELINES:
- coaching_questions: 4 sharp, Socratic questions that push the founder to think harder about the weakest dimensions. Make them specific to THIS idea, not generic. They should help the founder uncover a stronger, more defensible version.
- pivot_ideas: 2 concrete sharper variations within the SAME theme/industry that would likely score higher (narrower customer, stronger moat, clearer wedge)."""


def _weighted_score(scores: dict) -> int:
    """Weighted average of rubric scores (1-10) scaled to a 0-100 result."""
    total_weight = sum(r["weight"] for r in RUBRICS.values())
    weighted_sum = sum(
        scores[key]["score"] * RUBRICS[key]["weight"]
        for key in RUBRICS
    )
    return round((weighted_sum / total_weight) * 10)


def _verdict(score: float) -> tuple[str, str, str]:
    for threshold, label, color, description in VERDICT_THRESHOLDS:
        if score >= threshold:
            return label, color, description
    last = VERDICT_THRESHOLDS[-1]
    return last[1], last[2], last[3]


client = None


def _call_llm(prompt: str) -> str:
    """Call the configured provider and return raw JSON text."""
    if _provider() == "anthropic":
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        msg = _get_client().messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt + "\n\nReturn ONLY the JSON object, no prose."}],
        )
        text = msg.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1].lstrip("json").strip()
        return text

    model = os.getenv("OPENAI_MODEL", "gpt-5")

    def _call(**extra):
        return _get_client().chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            **extra,
        )
    try:
        response = _call(temperature=0.3)
    except BadRequestError:  # GPT-5 reasoning models only allow default temperature
        response = _call()
    return response.choices[0].message.content


def validate_idea(inputs: dict) -> dict:
    """Full validation pipeline: research → LLM scoring → weighted verdict."""
    research = research_idea(inputs["idea"], inputs["customer"])
    prompt = _build_prompt(inputs, research)

    try:
        raw = _call_llm(prompt)
    except RateLimitError:
        raise RuntimeError(
            "Your OpenAI account has no remaining quota. Add billing/credits at "
            "https://platform.openai.com/account/billing then try again."
        )
    except AuthenticationError:
        raise RuntimeError(
            "Invalid API key. Check OPENAI_API_KEY / ANTHROPIC_API_KEY in your .env file."
        )
    except Exception as e:
        name = type(e).__name__
        if "Authentication" in name:
            raise RuntimeError("Invalid API key. Check OPENAI_API_KEY / ANTHROPIC_API_KEY in your .env file.")
        if "RateLimit" in name:
            raise RuntimeError("Provider quota/credits exhausted. Add credits and try again.")
        raise RuntimeError(f"LLM call failed ({name}): {e}")

    result = json.loads(raw)

    weighted = _weighted_score(result["scores"])
    label, color, description = _verdict(weighted)

    result["weighted_score"] = weighted
    result["verdict_label"] = label
    result["verdict_color"] = color
    result["verdict_description"] = description
    result["research"] = research

    return result
