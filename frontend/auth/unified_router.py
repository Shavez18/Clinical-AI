"""
unified_router.py — Cinematic, full-screen healthcare authentication landing page.
Renders an animated ECG/neural background with a dual-panel layout:
  Left:  Hero panel with trust/security badges
  Right: Glassmorphism auth card with Doctor / Patient role switching
"""

import streamlit as st
from auth.animations import LOGIN_ANIMATIONS_CSS, ANIMATED_BACKGROUND_HTML, get_hero_panel_html
from auth.doctor_auth import render_doctor_login
from auth.patient_auth import render_patient_login


def render_unified_login():
    """Entry point called by app.py when user is not authenticated."""

    # ── Initialise role selection in session ─────────────────────────────
    if "login_role" not in st.session_state:
        st.session_state.login_role = "doctor"

    # ── Inject CSS animations & background ──────────────────────────────
    st.markdown(LOGIN_ANIMATIONS_CSS, unsafe_allow_html=True)
    st.markdown(ANIMATED_BACKGROUND_HTML, unsafe_allow_html=True)

    # ── Two-column layout: hero | auth card ─────────────────────────────
    # We need a thin spacer column on each side for visual breathing room
    _, left_col, gap_col, right_col, _ = st.columns([0.5, 5, 1, 5, 0.5])

    # ── LEFT: Hero Panel ─────────────────────────────────────────────────
    with left_col:
        st.markdown(get_hero_panel_html(), unsafe_allow_html=True)

    # ── RIGHT: Auth Card ─────────────────────────────────────────────────
    with right_col:
        # Open the glass card wrapper
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        # ── Role Switcher ────────────────────────────────────────────────
        role_col_a, role_col_b = st.columns(2)

        with role_col_a:
            doctor_type = "primary" if st.session_state.login_role == "doctor" else "secondary"
            if st.button(
                "🩺  Doctor Portal",
                use_container_width=True,
                key="role_doctor_btn",
                type=doctor_type,
            ):
                st.session_state.login_role = "doctor"
                # Reset patient sub-tab when switching roles
                st.session_state.pop("patient_tab", None)
                st.rerun()

        with role_col_b:
            patient_type = "primary" if st.session_state.login_role == "patient" else "secondary"
            if st.button(
                "🧬  Patient Portal",
                use_container_width=True,
                key="role_patient_btn",
                type=patient_type,
            ):
                st.session_state.login_role = "patient"
                st.rerun()

        # Active role indicator pill
        role_label = "Doctor Access" if st.session_state.login_role == "doctor" else "Patient Access"
        role_color = "#00c8b4" if st.session_state.login_role == "doctor" else "#60a5fa"
        st.markdown(f"""
        <div style="text-align:center;margin:.9rem 0 1.4rem;">
            <span style="display:inline-flex;align-items:center;gap:.45rem;
                         background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
                         border-radius:99px;padding:.3rem .85rem;font-family:'DM Mono',monospace;
                         font-size:.67rem;letter-spacing:.1em;text-transform:uppercase;color:{role_color};">
                <span style="width:6px;height:6px;border-radius:50%;background:{role_color};
                             box-shadow:0 0 6px {role_color};display:inline-block;"></span>
                Secure {role_label}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ── Render correct form ───────────────────────────────────────────
        if st.session_state.login_role == "doctor":
            render_doctor_login()
        else:
            render_patient_login()

        # Close the glass card wrapper
        st.markdown('</div>', unsafe_allow_html=True)
