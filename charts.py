import plotly.graph_objects as go
from rubrics import RUBRICS

# Shared dark layout applied to every chart
_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", family="sans-serif"),
    margin=dict(l=20, r=20, t=48, b=20),
)

_GRID = dict(gridcolor="rgba(255,255,255,0.08)", showgrid=True)


def radar_chart(scores: dict) -> go.Figure:
    """Spider/radar chart of the 6 rubric scores."""
    names = [RUBRICS[k]["name"] for k in RUBRICS]
    vals  = [scores[k]["score"] for k in RUBRICS]
    # Close the polygon
    names_c = names + [names[0]]
    vals_c  = vals  + [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_c, theta=names_c,
        fill="toself",
        fillcolor="rgba(124,58,237,0.25)",
        line=dict(color="#a78bfa", width=2),
        name="Your idea",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[7] * len(names_c), theta=names_c,
        fill="toself",
        fillcolor="rgba(96,165,250,0.06)",
        line=dict(color="#60a5fa", width=1, dash="dash"),
        name="Target (7/10)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 10],
                tickfont=dict(size=9, color="#94a3b8"),
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
                tickfont=dict(size=11),
            ),
        ),
        title=dict(text="Rubric Scores Overview", font=dict(size=15, color="#c4b5fd")),
        legend=dict(x=0.82, y=1.12, font=dict(size=11)),
        **_DARK,
    )
    return fig


def market_opportunity_chart(tam: float, sam: float, som: float) -> go.Figure:
    """Horizontal bars for TAM → SAM → SOM."""
    def fmt(v: float) -> str:
        return f"${v:.1f}B" if v >= 1 else f"${v * 1000:.0f}M"

    labels  = ["TAM — Total Market", "SAM — Serviceable", "SOM — Your Target"]
    values  = [tam, sam, som]
    colors  = ["#4f46e5", "#7c3aed", "#a855f7"]
    texts   = [fmt(v) for v in values]

    fig = go.Figure()
    for label, val, color, text in zip(labels, values, colors, texts):
        fig.add_trace(go.Bar(
            y=[label], x=[val],
            orientation="h",
            marker=dict(color=color, opacity=0.85,
                        line=dict(color="rgba(255,255,255,0.15)", width=1)),
            text=[text], textposition="outside",
            textfont=dict(color="#e2e8f0"),
            showlegend=False,
        ))

    fig.update_layout(
        title=dict(text="Market Opportunity", font=dict(size=15, color="#c4b5fd")),
        xaxis=dict(title="USD Billions", **_GRID),
        yaxis=dict(**_GRID),
        barmode="overlay",
        **_DARK,
    )
    return fig


def industry_chart(chart_data: dict) -> go.Figure:
    """Dynamic industry-specific trend chart returned by the LLM."""
    xs = [str(d["x"]) for d in chart_data["data"]]
    ys = [float(d["y"]) for d in chart_data["data"]]
    chart_type = chart_data.get("type", "line")

    fig = go.Figure()
    if chart_type == "bar":
        fig.add_trace(go.Bar(
            x=xs, y=ys,
            marker=dict(
                color=ys,
                colorscale=[[0, "#4f46e5"], [0.5, "#7c3aed"], [1, "#c084fc"]],
                showscale=False,
                line=dict(color="rgba(255,255,255,0.1)", width=1),
            ),
            text=[str(y) for y in ys],
            textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
    else:  # line (default)
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines+markers",
            line=dict(color="#a78bfa", width=3, shape="spline"),
            marker=dict(size=8, color="#c084fc",
                        line=dict(color="#e2e8f0", width=1)),
            fill="tozeroy",
            fillcolor="rgba(124,58,237,0.12)",
        ))

    fig.update_layout(
        title=dict(
            text=chart_data.get("title", "Industry Trend"),
            font=dict(size=15, color="#c4b5fd"),
        ),
        xaxis=dict(title=chart_data.get("x_label", ""), **_GRID),
        yaxis=dict(title=chart_data.get("y_label", ""), **_GRID),
        **_DARK,
    )
    return fig
