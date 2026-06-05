"""
auth_handler.py
===============
Authentication facade.

Tries the live FastAPI backend first (if API_URL env var is set and the
server is reachable). Falls back transparently to embedded_auth — which
reads the local SQLite file directly — so the app always works on
Streamlit Cloud where no backend process can run.
"""

import os
import time
import socket
import streamlit as st

from auth.embedded_auth import (
    authenticate as _embedded_auth,
    register_patient as _embedded_register_patient,
    register_doctor as _embedded_register_doctor,
)

# ── Backend availability ──────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "")          # empty → always use embedded mode

def _backend_reachable() -> bool:
    """Quick TCP probe — avoids hanging requests calls."""
    if not API_URL:
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(API_URL)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8000
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


# ── Public API (same signatures as before) ────────────────────────────────────

def authenticate(username: str, password: str, role: str):
    """
    Returns (success: bool, token: str | None, display_name: str).
    Uses embedded SQLite auth directly — instant, no network.
    """
    if not hasattr(st.session_state, "audit_logs") or "audit_logs" not in st.session_state:
        st.session_state.audit_logs = []

    if _backend_reachable():
        # Optional: try real backend when available (local dev / Docker)
        try:
            import requests
            res = requests.post(
                f"{API_URL}/login",
                data={"username": username, "password": password},
                timeout=3,
            )
            if res.status_code == 200:
                data = res.json()
                token = data.get("access_token")
                display_name = data.get("full_name") or username
                return True, token, display_name
        except Exception:
            pass  # fall through to embedded

    # Embedded mode (Streamlit Cloud / no backend)
    return _embedded_auth(username, password, role)


def register_patient(full_name: str, email: str, password: str):
    """Register a patient. Uses embedded SQLite — always works."""
    return _embedded_register_patient(full_name, email, password)


def register_doctor(clinical_id: str, hospital_name: str, doctor_name: str,
                    email: str, password: str):
    """Register a doctor. Uses embedded SQLite — always works."""
    return _embedded_register_doctor(clinical_id, hospital_name, doctor_name,
                                     email, password)


def verify_session():
    return st.session_state.get("token") is not None
