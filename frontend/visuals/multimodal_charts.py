import plotly.graph_objects as go
import pandas as pd

def plot_cbc_abnormality(biomarkers, abnormalities):
    """
    Plots a bar chart showing CBC values vs normal ranges.
    """
    # Define generic normal ranges
    ranges = {
        'RBC': [4.5, 5.9],
        'HCT': [41.0, 50.0],
        'Hemoglobin': [13.5, 17.5],
        'WBC': [4.5, 11.0]
    }
    
    categories = list(biomarkers.keys())
    values = list(biomarkers.values())
    
    colors = ['#ff003c' if f"Low {k}" in abnormalities or f"High {k}" in abnormalities else '#00f3ff' for k in categories]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=values,
        textposition='auto',
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8ab4f8', family='Outfit'),
        margin=dict(l=20, r=20, t=30, b=20),
        height=250,
        yaxis=dict(gridcolor='rgba(0, 243, 255, 0.1)', title="Value"),
        xaxis=dict(gridcolor='rgba(0,0,0,0)')
    )
    return fig

def plot_anemia_risk_radar(anemia_risk):
    """
    Plots a specialized radar for anemia indicators.
    """
    categories = ['Iron Deficiency', 'B12 Deficiency', 'Folate Deficiency', 'Chronic Disease', 'Hemolytic']
    
    if anemia_risk == "High":
        values = [80, 40, 30, 60, 20]
        color = 'rgba(255, 0, 60, 0.5)'
        line_color = '#ff003c'
    else:
        values = [20, 15, 10, 25, 5]
        color = 'rgba(0, 243, 255, 0.4)'
        line_color = '#00f3ff'
        
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor=color,
        line=dict(color=line_color, width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='#8ab4f8', gridcolor='rgba(138, 180, 248, 0.2)'),
            angularaxis=dict(color='#e0f4f4', gridcolor='rgba(138, 180, 248, 0.2)')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Outfit', size=12),
        margin=dict(l=30, r=30, t=30, b=30),
        height=250
    )
    return fig
