import streamlit as st
import time

def init_session():
    if "token" not in st.session_state:
        st.session_state.token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
    if "audit_logs" not in st.session_state:
        import json
        import os
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audit_logs.json")
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    st.session_state.audit_logs = json.load(f)
            except Exception:
                st.session_state.audit_logs = []
        else:
            st.session_state.audit_logs = []
    if "portal" not in st.session_state:
        st.session_state.portal = None

def is_authenticated():
    return st.session_state.get("token") is not None

def touch_activity():
    st.session_state.last_activity = time.time()

def check_session_timeout(timeout_seconds=3600):
    if not is_authenticated():
        return False
    
    last_act = st.session_state.get("last_activity")
    if last_act is None:
        st.session_state.last_activity = time.time()
        return False

    elapsed = time.time() - last_act
    if elapsed > timeout_seconds:
        clear_session()
        return True
    return False

def set_user_session(username, token, role):
    st.session_state.username = username
    st.session_state.token = token
    st.session_state.role = role
    st.session_state.last_activity = time.time()
    if "audit_logs" in st.session_state:
        st.session_state.audit_logs.append(f"User {username} logged in as {role} at {time.ctime()}")

def clear_session():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.last_activity = 0
    st.session_state.portal = None
    if "navigation_radio" in st.session_state:
        del st.session_state["navigation_radio"]
    if "sidebar_navigation_radio" in st.session_state:
        del st.session_state["sidebar_navigation_radio"]
