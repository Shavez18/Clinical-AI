import plotly.graph_objects as go
import random

def create_heart_biomarker_radar(features):
    """Creates a futuristic radar chart representing cardiovascular biomarkers."""
    categories = ['Blood Pressure', 'Heart Rate', 'Cholesterol', 'Age', 'ST Depression']
    
    # Normalize features to a 0-100 scale
    normalized_values = [
        min(100, (features.get('trestbps', 0) / 200) * 100),
        min(100, (features.get('thalach', 0) / 220) * 100),
        min(100, (features.get('chol', 0) / 500) * 100),
        min(100, (features.get('age', 0) / 100) * 100),
        min(100, (features.get('oldpeak', 0) / 6.0) * 100)
    ]
    
    # Close the radar loop
    normalized_values.append(normalized_values[0])
    categories.append(categories[0])

    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=normalized_values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 243, 255, 0.2)',
        line=dict(color='#00f3ff', width=3),
        marker=dict(size=8, color='#ffffff', line=dict(color='#00f3ff', width=2)),
        name='Cardio Biomarkers'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor='rgba(0, 243, 255, 0.1)',
                linecolor='rgba(0, 243, 255, 0.2)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#8ab4f8', family='JetBrains Mono'),
                gridcolor='rgba(0, 243, 255, 0.1)',
                linecolor='rgba(0, 243, 255, 0.2)'
            ),
            bgcolor='rgba(6, 9, 19, 0.5)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        height=320
    )
    return fig

def create_cholesterol_chart(chol):
    """Creates a futuristic bar chart indicating cholesterol risk."""
    fig = go.Figure(go.Indicator(
        mode = "number+gauge", value = chol,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text' : "<span style='color:#8ab4f8; font-size:12px'>Serum Cholesterol (mg/dL)</span>"},
        number = {'font': {'color': '#00f3ff'}},
        gauge = {
            'shape': "bullet",
            'axis': {'range': [None, 600], 'tickcolor': '#8ab4f8', 'tickfont': {'color': '#8ab4f8'}},
            'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': 200},
            'bgcolor': "rgba(6, 9, 19, 0.5)",
            'steps': [
                {'range': [0, 200], 'color': "rgba(0, 243, 255, 0.1)"},
                {'range': [200, 240], 'color': "rgba(255, 157, 0, 0.1)"},
                {'range': [240, 600], 'color': "rgba(255, 0, 60, 0.1)"}],
            'bar': {'color': '#00f3ff'}
        }
    ))
    fig.update_layout(height=150, margin=dict(t=30, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_vessel_risk_analysis(ca):
    """Creates an interactive pie/donut chart for vessel risk."""
    colors = ['#00f3ff', 'rgba(0, 243, 255, 0.1)']
    
    # Simple donut chart to represent vessel calcification risk based on ca value
    # ca ranges from 0 to 3
    risk_level = (ca / 3) * 100 if ca <= 3 else 100
    
    fig = go.Figure(data=[go.Pie(
        labels=['Affected Vessels', 'Clear Vessels'],
        values=[risk_level, 100 - risk_level],
        hole=.7,
        marker=dict(colors=colors, line=dict(color='#00f3ff', width=1))
    )])
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=10),
        height=150,
        annotations=[dict(text=f"{ca}/3", x=0.5, y=0.5, font_size=20, font_color="#00f3ff", showarrow=False)]
    )
    return fig

def create_blood_pressure_trend(bp):
    """Simulates a smooth BP trend line for visual flair."""
    # Create simulated historical data
    x_vals = list(range(10))
    y_vals = [bp + random.uniform(-5, 5) for _ in range(9)] + [bp]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        mode='lines+markers',
        line=dict(color='#00f3ff', width=3, shape='spline'),
        marker=dict(size=6, color='#ffffff', line=dict(width=2, color='#00f3ff')),
        fill='tozeroy',
        fillcolor='rgba(0, 243, 255, 0.1)'
    ))
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0, 243, 255, 0.1)', tickfont=dict(color='#8ab4f8')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=20, r=10),
        height=150
    )
    return fig
