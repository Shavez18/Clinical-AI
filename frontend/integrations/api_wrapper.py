"""
api_wrapper.py
==============
Drug interaction fetcher — no longer calls the FastAPI backend.
Routes directly to the local openfda_engine for offline/Streamlit Cloud use.
Falls back to the live backend only when API_URL is explicitly set.
"""

import os
import sys
import streamlit as st

# Ensure repo root is importable
_HERE = os.path.dirname(os.path.abspath(__file__))        # frontend/integrations/
_ROOT = os.path.dirname(os.path.dirname(_HERE))           # repo root
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


@st.cache_resource(show_spinner=False)
def _get_drug_engine():
    """Load the drug interaction engine once."""
    from src.drug_checker.openfda_engine import analyze_drug_interactions
    return analyze_drug_interactions


def fetch_drug_interactions(api_url, headers, drug_list):
    """
    Fetch drug interactions.
    - If api_url is empty/unset: use local engine (Streamlit Cloud mode).
    - If api_url is set: try live backend, fall back to local on failure.
    """
    # Try live backend only when URL is properly configured
    if api_url:
        try:
            import requests
            res = requests.post(
                f"{api_url}/check/drug-interaction",
                json={"drugs": drug_list},
                headers=headers,
                timeout=5,
            )
            if res.ok:
                return res.json()
        except Exception:
            pass  # fall through to local engine

    # Local engine (always works — no HTTP needed)
    try:
        analyze = _get_drug_engine()
        result  = analyze(drug_list)
        return {"analysis": result}
    except Exception as e:
        return {"error": str(e)}
