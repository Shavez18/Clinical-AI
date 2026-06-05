import plotly.graph_objects as go
import numpy as np

def plot_diagnosis_radar(probabilities):
    """
    Creates a neon-styled radar chart for disease probabilities.
    """
    categories = list(probabilities.keys())
    values = list(probabilities.values())
    
    # Close the radar chart
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(13, 253, 219, 0.2)',
        line=dict(color='#0dfddb', width=2),
        marker=dict(color='#0dfddb', size=8, symbol='circle'),
        hoverinfo='text',
        text=[f"{v}%" for v in values]
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(color='rgba(255, 255, 255, 0.5)')
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(color='#a5b4fc', size=12, family='DM Sans')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        height=350,
        font=dict(family='DM Sans')
    )
    return fig

def plot_symptom_heatmap(symptoms, severity_scores):
    """
    Creates a heatmap visualization for symptom severity and relevance.
    """
    z_data = np.array([severity_scores])
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=symptoms,
        y=['Severity'],
        colorscale=[[0, 'rgba(11, 37, 69, 0)'], [0.5, '#0e8c8c'], [1, '#0dfddb']],
        showscale=True,
        hoverongaps=False,
        xgap=2,
        ygap=2,
        colorbar=dict(
            title='Score',
            tickfont=dict(color='rgba(255,255,255,0.7)'),
            titlefont=dict(color='rgba(255,255,255,0.7)')
        )
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            tickfont=dict(color='#a5b4fc', size=11),
            gridcolor='rgba(255,255,255,0)'
        ),
        yaxis=dict(
            tickfont=dict(color='#a5b4fc', size=12),
            gridcolor='rgba(255,255,255,0)'
        ),
        margin=dict(l=20, r=20, t=30, b=30),
        height=180
    )
    return fig

def plot_health_score_gauge(score):
    """
    Creates a futuristic health score gauge.
    """
    color = "#0dfddb" if score > 70 else ("#f59e0b" if score > 40 else "#ef4444")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Wellness Index", 'font': {'size': 16, 'color': '#a5b4fc'}},
        number={'font': {'size': 48, 'color': color, 'family': 'Fraunces'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': 'rgba(255,255,255,0.2)'},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': 'rgba(255,255,255,0.05)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [40, 70], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(13, 253, 219, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white', 'family': 'DM Sans'},
        margin=dict(l=20, r=20, t=50, b=20),
        height=250
    )
    return fig
