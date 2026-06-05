"""
Navigation Assistant Module.
Maps user intent keywords to pages and provides callbacks to set active pages.
"""
import streamlit as st

PAGE_MAPPING = {
    "dashboard": "🎛️  Dashboard",
    "home": "🎛️  Dashboard",
    "overview": "🎛️  Dashboard",
    "diabetes": "🩸  Diabetes Intelligence",
    "sugar": "🩸  Diabetes Intelligence",
    "cardio": "🫀  Cardiovascular Intelligence",
    "heart": "🫀  Cardiovascular Intelligence",
    "cardiovascular": "🫀  Cardiovascular Intelligence",
    "nlp": "🧠  Clinical NLP Intelligence",
    "symptom": "🧠  Clinical NLP Intelligence",
    "symptoms": "🧠  Clinical NLP Intelligence",
    "diagnosis": "🧠  Clinical NLP Intelligence",
    "differential": "🧠  Clinical NLP Intelligence",
    "triage": "🧠  Clinical NLP Intelligence",
    "drug": "💊  Pharmacovigilance Intelligence",
    "medication": "💊  Pharmacovigilance Intelligence",
    "interaction": "💊  Pharmacovigilance Intelligence",
    "fda": "💊  Pharmacovigilance Intelligence",
    "history": "⏳  History",
    "logs": "⏳  History",
    "about": "ℹ️  About",
    "system": "ℹ️  About"
}

def check_navigation_intent(query: str) -> str:
    """
    Checks if the query contains navigation requests.
    Returns the target page key if found, else None.
    """
    q = query.lower()
    if "go to" in q or "navigate" in q or "take me to" in q or "open" in q or "show me" in q:
        for word, page_key in PAGE_MAPPING.items():
            if word in q:
                return page_key
    return None

def perform_navigation(page_key: str):
    """
    Updates the session state navigation radio key to force a page reload.
    """
    st.session_state.navigation_radio = page_key
    # Force rerun to show the new page
    st.rerun()
