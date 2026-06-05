import streamlit as st

def apply_advanced_theme():
    st.markdown("""
    <style>
    /* ── Advanced Futuristic Healthcare AI Theme ──────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* OVERRIDE GLOBAL APP.PY LIGHT THEME */
    .stApp {
        background-color: #060913 !important;
        background-image: radial-gradient(circle at 50% 0%, #0b1121 0%, #060913 70%) !important;
    }
    
    .block-container {
        color: #e0f4f4 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Override any global text colors from app.py */
    .block-container p, 
    .block-container span, 
    .block-container div {
        color: inherit;
    }

    /* ── Headers & Typography ──────────────────────────────────────────────── */
    .adv-title {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        font-size: 2.8rem !important;
        background: linear-gradient(90deg, #00f3ff, #0066ff, #9d00ff) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        line-height: 1.2 !important;
    }

    .adv-subtitle {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
        color: #00f3ff !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5) !important;
    }

    .adv-header {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        color: #ffffff !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid rgba(0, 243, 255, 0.2) !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }

    /* ── Metrics & KPIs ────────────────────────────────────────────────────── */
    .kpi-container {
        background: rgba(11, 17, 33, 0.65);
        border: 1px solid rgba(0, 243, 255, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .kpi-value {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        margin: 0.5rem 0 !important;
        text-shadow: 0 0 20px currentColor !important;
    }

    .kpi-label {
        font-size: 0.85rem !important;
        color: #8ab4f8 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 600 !important;
    }

    /* ── AI Recommendation Items ───────────────────────────────────────────── */
    .ai-insight {
        background: rgba(0, 243, 255, 0.03) !important;
        border-left: 4px solid #00f3ff !important;
        padding: 1.2rem 1.5rem !important;
        margin-bottom: 1rem !important;
        border-radius: 0 12px 12px 0 !important;
        font-size: 1rem !important;
        color: #e0f4f4 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
        transition: background 0.3s ease !important;
    }
    
    .ai-insight:hover {
        background: rgba(0, 243, 255, 0.08) !important;
        box-shadow: 0 4px 20px rgba(0, 243, 255, 0.1) !important;
    }

    .insight-title {
        font-weight: 700 !important;
        color: #00f3ff !important;
        margin-bottom: 0.4rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
        letter-spacing: 1px !important;
    }

    /* ── Streamlit Inputs Override ─────────────────────────────────────────── */
    /* Comprehensive override for all input types to eliminate white boxes */
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"],
    [data-testid="stMultiSelect"] [data-baseweb="select"] {
        background-color: rgba(11, 17, 33, 0.8) !important;
        color: #00f3ff !important;
        border: 1px solid rgba(0, 243, 255, 0.3) !important;
        border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1rem !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }

    /* Force the inner container of Selectbox and Multiselect to be transparent */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background-color: transparent !important;
    }

    /* Ensure the text inside selectbox is visible */
    [data-testid="stSelectbox"] [data-baseweb="select"] div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] div {
        color: #00f3ff !important;
    }

    /* SVG icons in select/multiselect (like clear and dropdown arrow) */
    [data-baseweb="select"] svg {
        fill: #00f3ff !important;
        color: #00f3ff !important;
    }

    /* Dropdown menu panels (popovers) - Global Fix for White Backgrounds */
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul {
        background-color: rgba(11, 17, 33, 0.95) !important;
        border: 1px solid rgba(0, 243, 255, 0.5) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 10px rgba(0, 243, 255, 0.2) !important;
    }
    div[data-baseweb="popover"] li {
        color: #e0f4f4 !important;
        background-color: transparent !important;
        font-family: 'JetBrains Mono', monospace !important;
        transition: all 0.2s ease !important;
        padding: 10px 15px !important;
    }
    div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] {
        background-color: rgba(0, 243, 255, 0.2) !important;
        color: #00f3ff !important;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.6) !important;
    }

    /* Multiselect tags */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: rgba(0, 243, 255, 0.1) !important;
        border: 1px solid #00f3ff !important;
        color: #00f3ff !important;
    }

    /* Expanders styling */
    [data-testid="stExpander"] {
        background-color: rgba(11, 17, 33, 0.6) !important;
        border: 1px solid rgba(0, 243, 255, 0.3) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] summary {
        background-color: rgba(0, 243, 255, 0.05) !important;
        color: #00f3ff !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] summary:hover {
        background-color: rgba(0, 243, 255, 0.1) !important;
    }
    [data-testid="stExpander"] summary svg {
        fill: #00f3ff !important;
        color: #00f3ff !important;
    }
    [data-testid="stExpanderDetails"] {
        background-color: transparent !important;
        color: #e0f4f4 !important;
    }

    /* Alerts (Info, Success, Warning, Error) */
    [data-testid="stAlert"] {
        background-color: rgba(11, 17, 33, 0.8) !important;
        border: 1px solid rgba(0, 243, 255, 0.3) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.1) !important;
    }
    [data-testid="stAlert"] .stMarkdown p,
    [data-testid="stAlert"] .stMarkdown {
        color: #e0f4f4 !important; /* Soft cyan / light gray */
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stAlert"] svg {
        fill: #00f3ff !important;
    }

    /* Labels styling */
    .stNumberInput label, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label, .stFileUploader label {
        color: #8ab4f8 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        margin-bottom: 0.5rem !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
    }

    /* Placeholder and Focus States */
    [data-testid="stTextArea"] textarea::placeholder, 
    [data-testid="stTextInput"] input::placeholder {
        color: rgba(138, 180, 248, 0.4) !important;
    }

    [data-testid="stTextArea"] textarea:focus, 
    [data-testid="stTextInput"] input:focus, 
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
    [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within {
        border-color: #00f3ff !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2) !important;
        outline: none !important;
    }

    /* ── File Uploader Override ────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background-color: rgba(11, 17, 33, 0.6) !important;
        border: 1px dashed rgba(0, 243, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
        padding: 0 !important;
        color: #00f3ff !important;
    }

    /* ── Buttons ───────────────────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(45deg, #0066ff, #9d00ff) !important;
        border: 1px solid rgba(0, 243, 255, 0.5) !important;
        border-radius: 30px !important;
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        padding: 0.8rem 2rem !important;
        box-shadow: 0 4px 20px rgba(157, 0, 255, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 243, 255, 0.6) !important;
        filter: brightness(1.2) !important;
        border-color: #00f3ff !important;
    }
    
    /* ── Plotly Backgrounds ────────────────────────────────────────────────── */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly bg {
        background: transparent !important;
    }
    
    /* ── Loader ────────────────────────────────────────────────────────────── */
    .cyber-loader {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        background: rgba(11, 17, 33, 0.65);
        border: 1px solid rgba(0, 243, 255, 0.15);
        border-radius: 20px;
        margin: 2rem 0;
    }
    
    .spinner {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(0, 243, 255, 0.1);
        border-radius: 50%;
        border-top-color: #00f3ff;
        animation: spin 1s ease-in-out infinite;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)
