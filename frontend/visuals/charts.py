import plotly.graph_objects as go

def create_neon_gauge(value, title):
    """Creates a futuristic neon gauge chart for risk assessment."""
    if value <= 30:
        bar_color = "#00f3ff"  # Neon cyan
    elif value <= 70:
        bar_color = "#ff9d00"  # Neon orange
    else:
        bar_color = "#ff003c"  # Neon red

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={
            'text': f"<span style='color:#8ab4f8; font-family:JetBrains Mono; font-size:14px; text-transform:uppercase; letter-spacing:2px;'>{title}</span>"
        },
        number={
            'suffix': "%",
            'font': {'size': 60, 'color': '#ffffff', 'family': 'Outfit, sans-serif', 'weight': 'bold'},
            'valueformat': '.1f'
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': 'rgba(0, 243, 255, 0.3)',
                'tickfont': {'size': 12, 'color': '#8ab4f8', 'family': 'JetBrains Mono'}
            },
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': 'rgba(6, 9, 19, 0.5)',
            'borderwidth': 2,
            'bordercolor': 'rgba(0, 243, 255, 0.1)',
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0, 243, 255, 0.05)'},
                {'range': [30, 70], 'color': 'rgba(255, 157, 0, 0.05)'},
                {'range': [70, 100], 'color': 'rgba(255, 0, 60, 0.05)'},
            ],
            'threshold': {
                'line': {'color': '#ffffff', 'width': 4},
                'thickness': 0.85,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        height=320,
        font={'family': 'Outfit, sans-serif'}
    )
    return fig

def create_biomarker_radar(features):
    """Creates a futuristic radar chart representing clinical biomarkers."""
    categories = ['Glucose', 'BMI', 'Age', 'Blood Pressure', 'Insulin']
    
    # Normalize features to a 0-100 scale for visual representation on radar
    normalized_values = [
        min(100, (features['Glucose'] / 200) * 100),
        min(100, (features['BMI'] / 50) * 100),
        min(100, (features['Age'] / 80) * 100),
        min(100, (features['BloodPressure'] / 140) * 100),
        min(100, (features['Insulin'] / 300) * 100)
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
        name='Patient Biomarkers'
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

def create_feature_importance_chart(shap_values):
    """Creates a horizontal bar chart simulating SHAP feature importance."""
    sorted_features = sorted(shap_values.items(), key=lambda x: abs(x[1]))
    features = [k for k, v in sorted_features]
    values = [v for k, v in sorted_features]
    
    colors = ['#ff003c' if v > 0 else '#00f3ff' for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=[f"{v:+.2f}" for v in values],
        textposition='outside',
        textfont=dict(color='#ffffff', family='JetBrains Mono')
    ))
    
    fig.update_layout(
        xaxis=dict(
            title="<span style='color:#8ab4f8; font-size:12px'>SHAP Impact on Risk Output</span>",
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.2)',
            tickfont=dict(color='#8ab4f8')
        ),
        yaxis=dict(
            tickfont=dict(color='#e0f4f4', family='JetBrains Mono', size=11)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=30, t=10, b=40),
        height=300,
        showlegend=False
    )
    return fig
