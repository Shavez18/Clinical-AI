import streamlit as st
import requests

import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

def render_portal_selector():
    st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"], header { display:none !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        
        .portal-container {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #f0f4f8;
            font-family: 'DM Sans', sans-serif;
        }
        
        .portal-card {
            background: white;
            padding: 3rem;
            border-radius: 24px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
            text-align: center;
            width: 100%;
            max-width: 450px;
        }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.portal:
        st.markdown('<div class="portal-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Doctor Portal", use_container_width=True):
                st.session_state.portal = "doctor"
                st.rerun()
        
        with col2:
            if st.button("Patient Portal", use_container_width=True):
                st.session_state.portal = "patient"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        render_login_screen(st.session_state.portal)

def render_login_screen(role):
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem;">
        <h2>{role.capitalize()} Login</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button(f"Login as {role.capitalize()}", use_container_width=True)
        
        if submit:
            # For demo purposes, check hardcoded credentials if API fails
            success = False
            try:
                res = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.session_state.username = username
                    st.session_state.role = role
                    success = True
            except:
                pass
            
            if not success:
                if username == "admin" and password == "password":
                    st.session_state.token = "demo_token"
                    st.session_state.username = "Dr. Admin" if role == "doctor" else "John Doe"
                    st.session_state.role = role
                    success = True
                else:
                    st.error("Invalid credentials")
            
            if success:
                st.rerun()

    if st.button("Back to selection"):
        st.session_state.portal = None
        st.rerun()
