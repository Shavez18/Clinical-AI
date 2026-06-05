"""patient_auth.py — Patient Health Portal login + signup form renderer."""

import streamlit as st
import time
from auth.auth_handler import authenticate, register_patient
from auth.session_manager import set_user_session


def render_patient_login():
    """Renders the Patient Portal with Login and Create Account tabs."""

    # Sub-tab state (Login / Sign Up)
    if "patient_tab" not in st.session_state:
        st.session_state.patient_tab = "login"

    st.markdown("""
    <div class="auth-card-header">
        <div class="auth-card-title">Patient Portal</div>
        <div class="auth-card-sub">Personal health management &amp; AI analysis</div>
    </div>
    """, unsafe_allow_html=True)

    # Inline tab switcher
    col_l, col_r = st.columns(2)
    with col_l:
        if st.button(
            "🔑  Sign In",
            use_container_width=True,
            key="tab_login_btn",
            type="primary" if st.session_state.patient_tab == "login" else "secondary"
        ):
            st.session_state.patient_tab = "login"
            # No st.rerun() — instant switch
    with col_r:
        if st.button(
            "✨  Create Account",
            use_container_width=True,
            key="tab_signup_btn",
            type="primary" if st.session_state.patient_tab == "signup" else "secondary"
        ):
            st.session_state.patient_tab = "signup"
            # No st.rerun() — instant switch

    st.markdown('<div style="height:.5rem;"></div>', unsafe_allow_html=True)

    # ── LOGIN TAB ────────────────────────────────────────────────────────
    if st.session_state.patient_tab == "login":
        with st.form("patient_login_form", clear_on_submit=False):
            email = st.text_input(
                "Email Address",
                placeholder="you@example.com",
                key="patient_email_input"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="••••••••",
                key="patient_pass_input"
            )

            # Forgot password inline link
            st.markdown("""
            <div class="forgot-link">
                <span onclick="alert('Password reset link sent! (UI demo)')">Forgot password?</span>
            </div>
            """, unsafe_allow_html=True)

            submitted = st.form_submit_button(
                "🚀  Sign In to Health Portal",
                use_container_width=True
            )

            if submitted:
                if not email or not password:
                    st.error("⚠️  Please enter your email and password.")
                else:
                    with st.spinner("Authenticating…"):
                        success, token, display_name = authenticate(
                            email, password, "patient"
                        )
                    if success:
                        set_user_session(display_name, token, "patient")
                        st.rerun()
                    else:
                        st.error("❌  Invalid credentials. Please check your email and password.")

        st.markdown("""
        <div style="text-align:center;margin-top:.8rem;font-family:'DM Mono',monospace;
                    font-size:.65rem;letter-spacing:.08em;color:rgba(150,190,210,.4);">
            DEMO &nbsp;·&nbsp; Email: admin &nbsp;/&nbsp; PW: password
        </div>
        """, unsafe_allow_html=True)

    # ── SIGN UP TAB ──────────────────────────────────────────────────────
    else:
        with st.form("patient_signup_form", clear_on_submit=True):
            full_name = st.text_input(
                "Full Name",
                placeholder="Jane Doe",
                key="signup_name_input"
            )
            email = st.text_input(
                "Email Address",
                placeholder="you@example.com",
                key="signup_email_input"
            )
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Min 8 chars",
                    key="signup_pass_input"
                )
            with col_p2:
                confirm = st.text_input(
                    "Confirm",
                    type="password",
                    placeholder="Repeat",
                    key="signup_confirm_input"
                )

            submitted = st.form_submit_button(
                "🎉  Create My Health Account",
                use_container_width=True
            )

            if submitted:
                if not full_name or not email or not password or not confirm:
                    st.error("⚠️  All fields are required.")
                elif password != confirm:
                    st.error("❌  Passwords do not match.")
                elif len(password) < 8:
                    st.error("⚠️  Password must be at least 8 characters.")
                else:
                    with st.spinner("Creating your account…"):
                        ok, msg = register_patient(full_name, email, password)
                    if ok:
                        st.success(f"✅  Account created! Welcome, {full_name}. Please sign in.")
                        st.session_state.patient_tab = "login"
                        st.rerun()
                    else:
                        st.error(f"❌  {msg}")

    # Security footer
    st.markdown("""
    <div class="auth-security-bar">
        <span>TLS 1.3</span>
        <span class="auth-security-dot"></span>
        <span>JWT Bearer</span>
        <span class="auth-security-dot"></span>
        <span>AES-256</span>
        <span class="auth-security-dot"></span>
        <span>End-to-End Encrypted</span>
    </div>
    """, unsafe_allow_html=True)
