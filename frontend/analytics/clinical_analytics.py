"""
clinical_analytics.py
──────────────────────────────────────────────────────────────────────────────
Plotly chart library for the Clinical Records Analytics dashboard.
All charts use the dark neon palette matching the existing dashboard theme.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime

# ── Shared Palette ────────────────────────────────────────────────────────────
COLORS = {
    "bg":      "rgba(0,0,0,0)",
    "panel":   "rgba(11,17,33,0.0)",
    "text":    "#e0f4f4",
    "muted":   "#8ab4f8",
    "cyan":    "#00f3ff",
    "blue":    "#0066ff",
    "purple":  "#9d00ff",
    "green":   "#00e676",
    "amber":   "#ff9d00",
    "red":     "#ff003c",
    "grid":    "rgba(0,243,255,0.08)",
    "border":  "rgba(0,243,255,0.15)",
}

MODULE_COLORS = [
    "#00f3ff", "#0066ff", "#9d00ff", "#ff9d00",
    "#00e676", "#ff003c", "#8ab4f8", "#00b4cc",
]

SEVERITY_COLORS = {
    "HIGH":     COLORS["red"],
    "MODERATE": COLORS["amber"],
    "LOW":      COLORS["green"],
    "N/A":      COLORS["muted"],
}

_LAYOUT_BASE = dict(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["bg"],
    font=dict(family="JetBrains Mono, monospace", color=COLORS["text"], size=11),
    margin=dict(l=20, r=20, t=50, b=30),
    legend=dict(
        bgcolor="rgba(11,17,33,0.6)",
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(size=10),
    ),
)


def _apply_axis_style(fig, xaxis=True, yaxis=True):
    """Apply consistent dark axis styling."""
    axis_style = dict(
        gridcolor=COLORS["grid"],
        zerolinecolor=COLORS["grid"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["muted"], size=10),
        title_font=dict(color=COLORS["muted"], size=10),
    )
    if xaxis:
        fig.update_xaxes(**axis_style)
    if yaxis:
        fig.update_yaxes(**axis_style)
    return fig


# ── 1. Risk Progression Line Chart ───────────────────────────────────────────
def plot_risk_progression(df: pd.DataFrame) -> go.Figure:
    """Longitudinal risk % trend over time."""
    fig = go.Figure()

    if df.empty or "Risk %" not in df.columns:
        fig.add_annotation(
            text="No risk data available yet.<br>Run a prediction to populate this chart.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Risk Progression Over Time", **_LAYOUT_BASE, height=320)
        return fig

    risk_df = df[df["Risk %"] > 0].copy()
    if risk_df.empty:
        fig.add_annotation(
            text="No risk scores recorded yet.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Risk Progression Over Time", **_LAYOUT_BASE, height=320)
        return fig

    risk_df = risk_df.sort_values("_ts")

    # Gradient fill line
    fig.add_trace(go.Scatter(
        x=risk_df["Timestamp"],
        y=risk_df["Risk %"],
        mode="lines+markers",
        name="Risk %",
        line=dict(color=COLORS["cyan"], width=2.5, shape="spline"),
        marker=dict(
            size=8, color=risk_df["Risk %"],
            colorscale=[[0, COLORS["green"]], [0.5, COLORS["amber"]], [1, COLORS["red"]]],
            cmin=0, cmax=100,
            line=dict(color=COLORS["bg"], width=1.5),
        ),
        fill="tozeroy",
        fillcolor="rgba(0,243,255,0.06)",
        hovertemplate="<b>%{x}</b><br>Risk: %{y:.1f}%<extra></extra>",
        text=risk_df.get("Module", pd.Series([""] * len(risk_df))).values,
    ))

    # High risk threshold line
    fig.add_hline(y=70, line=dict(color=COLORS["red"], width=1, dash="dash"),
                  annotation_text="High Risk Threshold",
                  annotation_font_color=COLORS["red"],
                  annotation_font_size=9)
    fig.add_hline(y=30, line=dict(color=COLORS["amber"], width=1, dash="dot"),
                  annotation_text="Moderate Threshold",
                  annotation_font_color=COLORS["amber"],
                  annotation_font_size=9)

    fig.update_layout(
        title=dict(text="📈 Risk Progression Over Time", font=dict(color=COLORS["cyan"], size=13)),
        xaxis_title="Session Timestamp",
        yaxis_title="Risk Score (%)",
        yaxis=dict(range=[0, 105]),
        **_LAYOUT_BASE, height=320,
    )
    return _apply_axis_style(fig)


# ── 2. Module Frequency Bar Chart ─────────────────────────────────────────────
def plot_module_frequency(df: pd.DataFrame) -> go.Figure:
    """Query count per module as a horizontal bar chart."""
    fig = go.Figure()

    if df.empty or "Module" not in df.columns:
        fig.add_annotation(
            text="No module data available yet.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Module Query Frequency", **_LAYOUT_BASE, height=300)
        return fig

    counts = df["Module"].value_counts().reset_index()
    counts.columns = ["Module", "Queries"]

    colors_list = [MODULE_COLORS[i % len(MODULE_COLORS)] for i in range(len(counts))]

    fig.add_trace(go.Bar(
        x=counts["Queries"],
        y=counts["Module"],
        orientation="h",
        marker=dict(
            color=colors_list,
            line=dict(color="rgba(0,243,255,0.3)", width=0.8),
        ),
        hovertemplate="<b>%{y}</b><br>Queries: %{x}<extra></extra>",
        text=counts["Queries"],
        textposition="outside",
        textfont=dict(color=COLORS["muted"], size=10),
    ))

    fig.update_layout(
        title=dict(text="🏥 Module Query Frequency", font=dict(color=COLORS["cyan"], size=13)),
        xaxis_title="Number of Queries",
        yaxis_title="",
        **_LAYOUT_BASE, height=300,
    )
    return _apply_axis_style(fig)


# ── 3. Risk Distribution Donut ────────────────────────────────────────────────
def plot_risk_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart showing High / Moderate / Low / N/A split."""
    if df.empty or "Severity" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No severity data yet.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Risk Distribution", **_LAYOUT_BASE, height=300)
        return fig

    counts = df["Severity"].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    color_map = [SEVERITY_COLORS.get(l, COLORS["muted"]) for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(
            colors=color_map,
            line=dict(color="rgba(0,0,0,0.4)", width=2),
        ),
        textfont=dict(color=COLORS["text"], size=10),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="🎯 Prediction Risk Distribution", font=dict(color=COLORS["cyan"], size=13)),
        annotations=[dict(
            text=f"<b>{sum(values)}</b><br>total",
            x=0.5, y=0.5, font=dict(size=14, color=COLORS["cyan"]),
            showarrow=False
        )],
        **_LAYOUT_BASE, height=300,
    )
    return fig


# ── 4. Activity Timeline ──────────────────────────────────────────────────────
def plot_activity_timeline(df: pd.DataFrame) -> go.Figure:
    """Scatter timeline of queries positioned by hour of day."""
    fig = go.Figure()

    if df.empty or "_ts" not in df.columns:
        fig.add_annotation(
            text="No activity data yet.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Session Activity Timeline", **_LAYOUT_BASE, height=280)
        return fig

    df2 = df.dropna(subset=["_ts"]).copy()
    if df2.empty:
        fig.add_annotation(
            text="No timestamped records.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Session Activity Timeline", **_LAYOUT_BASE, height=280)
        return fig

    modules = df2["Module"].unique().tolist()
    for i, mod in enumerate(modules):
        mod_df = df2[df2["Module"] == mod]
        color = MODULE_COLORS[i % len(MODULE_COLORS)]
        fig.add_trace(go.Scatter(
            x=mod_df["_ts"],
            y=mod_df["Hour"],
            mode="markers",
            name=mod,
            marker=dict(
                size=12, color=color, opacity=0.85,
                line=dict(color="rgba(0,0,0,0.4)", width=1),
                symbol="circle",
            ),
            hovertemplate=(
                f"<b>{mod}</b><br>"
                "Time: %{x|%H:%M:%S}<br>"
                "Hour: %{y}<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text="⏱ Session Activity Timeline", font=dict(color=COLORS["cyan"], size=13)),
        xaxis_title="Timestamp",
        yaxis_title="Hour of Day",
        yaxis=dict(range=[-0.5, 23.5], dtick=4),
        **_LAYOUT_BASE, height=280,
    )
    return _apply_axis_style(fig)


# ── 5. Prediction Heatmap ─────────────────────────────────────────────────────
def plot_prediction_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap of module × severity counts."""
    fig = go.Figure()

    if df.empty or "Module" not in df.columns or "Severity" not in df.columns:
        fig.add_annotation(
            text="Insufficient data for heatmap.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Module × Severity Heatmap", **_LAYOUT_BASE, height=280)
        return fig

    pivot = pd.crosstab(df["Module"], df["Severity"]).reindex(
        columns=["LOW", "MODERATE", "HIGH", "N/A"], fill_value=0
    )
    # Drop all-zero columns
    pivot = pivot.loc[:, (pivot != 0).any(axis=0)]

    if pivot.empty:
        fig.add_annotation(
            text="No cross-tabulation data.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(color=COLORS["muted"], size=12)
        )
        fig.update_layout(title="Module × Severity Heatmap", **_LAYOUT_BASE, height=280)
        return fig

    fig.add_trace(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0, "rgba(11,17,33,0.4)"],
            [0.3, "rgba(0,102,255,0.5)"],
            [0.7, "rgba(0,243,255,0.7)"],
            [1.0, "rgba(255,0,60,0.9)"],
        ],
        showscale=True,
        colorbar=dict(
            tickfont=dict(color=COLORS["muted"], size=9),
            outlinecolor=COLORS["border"],
            outlinewidth=0.5,
            thickness=12,
            len=0.8,
        ),
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Count: %{z}<extra></extra>",
        text=pivot.values,
        texttemplate="%{text}",
        textfont=dict(color=COLORS["text"], size=11),
    ))

    fig.update_layout(
        title=dict(text="🔥 Module × Severity Heatmap", font=dict(color=COLORS["cyan"], size=13)),
        xaxis_title="Severity Level",
        yaxis_title="",
        **_LAYOUT_BASE, height=max(280, 80 * len(pivot) + 80),
    )
    return _apply_axis_style(fig)


# ── 6. Biomarker / Risk Gauge Mini ───────────────────────────────────────────
def plot_avg_risk_gauge(avg_risk: float) -> go.Figure:
    """Small gauge showing session average risk."""
    if avg_risk <= 30:
        bar_color = COLORS["green"]
    elif avg_risk <= 70:
        bar_color = COLORS["amber"]
    else:
        bar_color = COLORS["red"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_risk,
        title=dict(text="<b>AVG SESSION RISK</b>",
                   font=dict(size=11, color=COLORS["muted"], family="JetBrains Mono")),
        number=dict(suffix="%", font=dict(size=38, color=bar_color, family="JetBrains Mono"),
                    valueformat=".1f"),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1,
                      tickcolor=COLORS["grid"],
                      tickfont=dict(size=8, color=COLORS["muted"])),
            bar=dict(color=bar_color, thickness=0.65),
            bgcolor="rgba(11,17,33,0.5)",
            borderwidth=1,
            bordercolor=COLORS["border"],
            steps=[
                dict(range=[0, 30],  color="rgba(0,230,118,0.08)"),
                dict(range=[30, 70], color="rgba(255,157,0,0.08)"),
                dict(range=[70, 100], color="rgba(255,0,60,0.12)"),
            ],
            threshold=dict(
                line=dict(color=bar_color, width=2),
                thickness=0.78, value=avg_risk
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(family="JetBrains Mono, monospace", color=COLORS["text"]),
        margin=dict(l=20, r=20, t=50, b=10),
        height=240,
    )
    return fig
