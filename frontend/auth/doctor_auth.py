"""doctor_auth.py — Doctor Portal login form renderer."""

import streamlit as st
import time
import uuid
from auth.auth_handler import authenticate, register_doctor
from auth.session_manager import set_user_session


def render_doctor_login():
    """Renders the Doctor Portal login form inside the auth card."""
    # Sub-tab state
    if "doctor_tab" not in st.session_state:
        st.session_state.doctor_tab = "login"

    st.markdown("""
    <div class="auth-card-header">
        <div class="auth-card-title">Doctor Portal</div>
        <div class="auth-card-sub">Clinical access &amp; Hospital network</div>
    </div>
    """, unsafe_allow_html=True)

    # Inline tab switcher
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button("🔑  Sign In", use_container_width=True, key="doc_tab_login", 
                     type="primary" if st.session_state.doctor_tab == "login" else "secondary"):
            st.session_state.doctor_tab = "login"
            # No st.rerun() — instant switch
    with col_r:
        if st.button("🏥  Create Clinic", use_container_width=True, key="doc_tab_signup",
                     type="primary" if st.session_state.doctor_tab == "signup" else "secondary"):
            st.session_state.doctor_tab = "signup"
            # No st.rerun() — instant switch

    st.markdown('<div style="height:.5rem;"></div>', unsafe_allow_html=True)

    if st.session_state.doctor_tab == "login":
        if "doctor_success_msg" in st.session_state:
            st.success(st.session_state.doctor_success_msg)
            del st.session_state.doctor_success_msg

        with st.form("doctor_login_form", clear_on_submit=False):
            clinical_id = st.text_input(
                "Clinical ID / Email",
                placeholder="e.g. dr.smith@hospital.org",
                key="doctor_id_input"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
                key="doctor_pass_input"
            )

            st.markdown('<div style="height:0.3rem;"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "🔐  Authenticate Access",
                use_container_width=True
            )

            if submitted:
                if not clinical_id or not password:
                    st.error("⚠️  Please enter your Clinical ID and Password.")
                else:
                    with st.spinner("Verifying credentials…"):
                        success, token, display_name = authenticate(
                            clinical_id, password, "doctor"
                        )
                    if success:
                        set_user_session(display_name, token, "doctor")
                        st.rerun()
                    else:
                        st.error("❌  Invalid credentials. Check your Clinical ID and Password.")

    else:
        with st.form("doctor_signup_form", clear_on_submit=True):
            if "generated_clinical_id" not in st.session_state:
                st.session_state.generated_clinical_id = f"CLINIC-{str(uuid.uuid4())[:8].upper()}"
            
            st.text_input("Generated Clinical ID (Save this!)", value=st.session_state.generated_clinical_id, disabled=True)
            
            hospital_name = st.text_input("Hospital / Clinic Name", placeholder="e.g. General Hospital")
            doctor_name = st.text_input("Lead Doctor Name", placeholder="Dr. Jane Doe")
            email = st.text_input("Contact Email", placeholder="admin@hospital.org")
            password = st.text_input("Admin Password", type="password", placeholder="Min 8 chars")

            submitted = st.form_submit_button("🏥  Register Clinical Network", use_container_width=True)

            if submitted:
                if not hospital_name or not doctor_name or not email or not password:
                    st.error("⚠️  All fields are required.")
                elif len(password) < 8:
                    st.error("⚠️  Password must be at least 8 characters.")
                else:
                    with st.spinner("Provisioning clinical network…"):
                        ok, msg = register_doctor(
                            clinical_id=st.session_state.generated_clinical_id,
                            hospital_name=hospital_name,
                            doctor_name=doctor_name,
                            email=email,
                            password=password
                        )
                    if ok:
                        st.session_state.doctor_success_msg = f"✅  Network created successfully! Your Clinical ID is: **{st.session_state.generated_clinical_id}**\n\n💡 You can log in using either this Clinical ID or your Contact Email."
                        st.session_state.doctor_tab = "login"
                        del st.session_state.generated_clinical_id
                        st.rerun()
                    else:
                        st.error(f"❌  {msg}")

    # Demo hint
    if st.session_state.doctor_tab == "login":
        st.markdown("""
        <div style="text-align:center;margin-top:.8rem;font-family:'DM Mono',monospace;
                    font-size:.65rem;letter-spacing:.08em;color:rgba(150,190,210,.4);">
            DEMO &nbsp;·&nbsp; ID: admin &nbsp;/&nbsp; PW: password
        </div>
        """, unsafe_allow_html=True)

    # Security footer
    st.markdown("""
    <div class="auth-security-bar">
        <span>TLS 1.3</span>
        <span class="auth-security-dot"></span>
        <span>JWT Bearer</span>
        <span class="auth-security-dot"></span>
        <span>AES-256</span>
        <span class="auth-security-dot"></span>
        <span>HIPAA-Ready</span>
    </div>
    """, unsafe_allow_html=True)
