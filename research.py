try:
    from ddgs import DDGS
except ImportError:  # fallback to legacy package name
    from duckduckgo_search import DDGS


def _search(query: str, max_results: int = 5) -> list[dict]:
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception:
        return []


def format_results(results: list[dict]) -> str:
    if not results:
        return "No results found."
    lines = []
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")[:250]
        lines.append(f"- {title}: {body}")
    return "\n".join(lines)


def research_idea(idea: str, customer: str) -> dict:
    """Run all web research for a startup idea and return formatted strings."""
    competitors_raw   = _search(f"{idea} startup competitors alternatives {customer}")
    market_size_raw   = _search(f"market size TAM {idea} industry 2024 2025 billion")
    demand_raw        = _search(f"{customer} {idea} problem pain point reddit forum complaints")
    yc_funding_raw    = _search(f"{idea} startup YC Y Combinator funded 2024 2025", max_results=3)

    return {
        "competitors":    format_results(competitors_raw),
        "market_size":    format_results(market_size_raw),
        "demand_signals": format_results(demand_raw),
        "yc_alignment":   format_results(yc_funding_raw),
    }
