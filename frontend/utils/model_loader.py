"""
model_loader.py
===============
Centralised, cached ML model loader for Streamlit Cloud.

All models are loaded ONCE per server process using @st.cache_resource
and shared across all user sessions. This avoids repeated disk I/O and
reduces cold-start latency significantly.

Usage:
    from utils.model_loader import get_diabetes_model, get_heart_model, get_symptom_engine
"""

import os
import streamlit as st

# ── Path resolution ───────────────────────────────────────────────────────────
# Supports both: running from frontend/ and running from repo root (Streamlit Cloud)
_HERE      = os.path.dirname(os.path.abspath(__file__))          # frontend/utils/
_FRONTEND  = os.path.dirname(_HERE)                               # frontend/
_ROOT      = os.path.dirname(_FRONTEND)                           # repo root
_MODELS    = os.path.join(_ROOT, "src", "models")

def _model_path(filename: str) -> str:
    return os.path.join(_MODELS, filename)


# ── Diabetes Model ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading Diabetes Intelligence Engine…")
def get_diabetes_model():
    """Returns (model, scaler, threshold) — loaded once."""
    import joblib
    model     = joblib.load(_model_path("elite_diabetes_model.pkl"))
    scaler    = joblib.load(_model_path("scaler.pkl"))
    threshold = joblib.load(_model_path("threshold.pkl"))
    return model, scaler, threshold


# ── Heart Model ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading Cardiovascular Intelligence Engine…")
def get_heart_model():
    """Returns (model, scaler, model_columns) — loaded once."""
    import joblib
    model         = joblib.load(_model_path("elite_heart_model.pkl"))
    scaler        = joblib.load(_model_path("heart_scaler.pkl"))
    model_columns = joblib.load(_model_path("heart_model_columns.pkl"))
    return model, scaler, model_columns


# ── Symptom / Differential Engine ────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading Clinical NLP Engine…")
def get_differential_engine():
    """Returns a DifferentialEngine instance — loaded once."""
    import sys
    # Ensure src package is importable
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from src.symptom_engine.differential_model import DifferentialEngine
    return DifferentialEngine()


# ── Symptom Model (for direct vectorizer access) ──────────────────────────────
@st.cache_resource(show_spinner="Loading Symptom NLP Model…")
def get_symptom_model():
    """Returns (model, vectorizer) — loaded once."""
    import joblib
    model      = joblib.load(_model_path("symptom_model.pkl"))
    vectorizer = joblib.load(_model_path("symptom_vectorizer.pkl"))
    return model, vectorizer


# ── NLP Clinical Parser ───────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising Clinical NLP Parser…")
def get_clinical_parser():
    """Returns the ClinicalParser singleton — loaded once."""
    import sys
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from src.nlp.clinical_parser import clinical_parser
    return clinical_parser
