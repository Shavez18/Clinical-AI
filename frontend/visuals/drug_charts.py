import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def render_risk_gauge(value, title):
    """Renders an advanced animated risk gauge."""
    if value <= 30:
        bar_color = "#00f3ff"
        band_colors = ["rgba(0,243,255,0.15)", "rgba(255,157,0,0.05)", "rgba(255,0,60,0.05)"]
    elif value <= 70:
        bar_color = "#ff9d00"
        band_colors = ["rgba(0,243,255,0.05)", "rgba(255,157,0,0.15)", "rgba(255,0,60,0.05)"]
    else:
        bar_color = "#ff003c"
        band_colors = ["rgba(0,243,255,0.05)", "rgba(255,157,0,0.05)", "rgba(255,0,60,0.15)"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={
            'text': f"<b>{title}</b>",
            'font': {'size': 15, 'color': '#e0f4f4', 'family': 'Outfit, sans-serif'}
        },
        number={
            'suffix': "%",
            'font': {'size': 52, 'color': bar_color, 'family': 'JetBrains Mono, monospace'},
            'valueformat': '.1f'
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': 'rgba(0,243,255,0.3)',
                'tickfont': {'size': 10, 'color': '#8ab4f8', 'family': 'JetBrains Mono, monospace'}
            },
            'bar': {'color': bar_color, 'thickness': 0.68},
            'bgcolor': 'rgba(11,17,33,0.8)',
            'borderwidth': 1,
            'bordercolor': 'rgba(0,243,255,0.15)',
            'steps': [
                {'range': [0,  30], 'color': band_colors[0]},
                {'range': [30, 70], 'color': band_colors[1]},
                {'range': [70,100], 'color': band_colors[2]},
            ],
            'threshold': {
                'line': {'color': bar_color, 'width': 3},
                'thickness': 0.8,
                'value': value
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e0f4f4', 'family': 'Outfit, sans-serif'},
        margin=dict(l=30, r=30, t=60, b=10),
        height=280,
    )
    return fig

def render_organ_impact_radar(organ_data):
    """Renders a radar chart showing estimated toxicity per organ system."""
    categories = list(organ_data.keys())
    values = list(organ_data.values())
    
    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 243, 255, 0.15)',
        line=dict(color='#00f3ff', width=2),
        name='Organ Impact'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=8, color="#8ab4f8"),
                gridcolor="rgba(0,243,255,0.15)",
                linecolor="rgba(0,243,255,0.15)"
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#e0f4f4", family="Outfit, sans-serif"),
                gridcolor="rgba(0,243,255,0.15)",
                linecolor="rgba(0,243,255,0.15)"
            ),
            bgcolor="rgba(11, 17, 33, 0.5)"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        height=320,
        showlegend=False
    )
    return fig

def render_interaction_network(drug_list, interactions):
    """Renders a mock interaction network graph using scatter plot."""
    import networkx as nx
    
    G = nx.Graph()
    for drug in drug_list:
        G.add_node(drug)
        
    edges = []
    for i in interactions:
        pair = i.get("drug_pair", [])
        if len(pair) == 2:
            sev = i.get("severity", "Minor")
            weight = 3 if sev == "Major" else 2 if sev == "Moderate" else 1
            color = "#ff003c" if sev == "Major" else "#ff9d00" if sev == "Moderate" else "#00f3ff"
            G.add_edge(pair[0].title(), pair[1].title(), weight=weight, color=color)
            edges.append((pair[0].title(), pair[1].title(), color, weight))
            
    pos = nx.spring_layout(G, seed=42)
    
    edge_x = []
    edge_y = []
    edge_colors = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_colors.append(edge[2].get("color", "#00f3ff"))
        
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        
    fig = go.Figure()
    
    # We add edges individually to color them by severity
    for e in edges:
        n1, n2, c, w = e
        x0, y0 = pos[n1]
        x1, y1 = pos[n2]
        fig.add_trace(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=w*1.5, color=c),
            hoverinfo='none',
            mode='lines'
        ))
        
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="bottom center",
        marker=dict(
            showscale=False,
            color='#0b1121',
            size=20,
            line_width=2,
            line_color='#00f3ff'
        ),
        textfont=dict(family="Outfit, sans-serif", size=12, color="#e0f4f4")
    ))
    
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=20,r=20,t=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350
    )
    return fig

def render_compatibility_heatmap(df):
    """Renders a heatmap of drug-drug interactions risk."""
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=[[0, 'rgba(0,243,255,0.1)'], [0.5, 'rgba(255,157,0,0.6)'], [1, 'rgba(255,0,60,0.8)']],
        showscale=False,
        hoverongaps=False,
        hovertemplate="Risk Level: %{z:.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Outfit, sans-serif', 'size': 11, 'color': '#e0f4f4'},
        margin=dict(l=40, r=20, t=20, b=40),
        height=300
    )
    return fig
