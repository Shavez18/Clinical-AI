import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

def render_shap_waterfall(features, importances, title="SHAP Feature Importance"):
    """
    Renders a Plotly waterfall chart mimicking SHAP value visualization.
    """
    fig = go.Figure(go.Waterfall(
        name="SHAP",
        orientation="h",
        measure=["relative"] * len(features) + ["total"],
        y=features + ["Prediction"],
        x=importances + [sum(importances)],
        connector={"line": {"color": "rgba(255,255,255,0.1)", "width": 1}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#0dfddb"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))
    
    fig.update_layout(
        title={"text": title, "font": {"color": "#a5b4fc", "size": 14}},
        waterfallgap=0.3,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='DM Sans'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="SHAP Value (impact on model output)"),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        margin=dict(l=80, r=20, t=50, b=40),
        height=300
    )
    return fig

def get_nlp_token_importance(text):
    """
    Mocks token importance visualization for the NLP engine.
    Returns HTML with highlighted tokens.
    """
    time.sleep(0.5)
    tokens = text.split()
    html_out = []
    
    # Simple mockup logic to assign colors based on word length or random
    for t in tokens:
        clean_t = t.lower().strip(".,?!:")
        if clean_t in ["pain", "severe", "fever", "hypertension", "diabetic", "headache"]:
            # High importance (red/orange)
            html_out.append(f'<span style="background-color:rgba(239, 68, 68, 0.4); padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid #ef4444;">{t}</span>')
        elif clean_t in ["no", "denies", "without"]:
            # Negation (blue/teal)
            html_out.append(f'<span style="background-color:rgba(14, 140, 140, 0.4); padding: 2px 4px; border-radius: 4px; border-bottom: 2px solid #0dfddb;">{t}</span>')
        elif len(clean_t) > 6:
            # Medium importance
            html_out.append(f'<span style="background-color:rgba(245, 158, 11, 0.3); padding: 2px 4px; border-radius: 4px;">{t}</span>')
        else:
            # Low/no importance
            html_out.append(f'<span style="color:rgba(255,255,255,0.8);">{t}</span>')
            
    return "<div style='line-height: 2; font-family: \"DM Mono\", monospace; font-size: 0.9rem;'>" + " ".join(html_out) + "</div>"
