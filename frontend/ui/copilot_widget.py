"""
Clinical AI Copilot UI Widget.
Renders the floating chatbot toggle button and the glassmorphic assistant container.

ARCHITECTURE NOTE
─────────────────
Streamlit's st.markdown(unsafe_allow_html=True) STRIPS <script> tags but shows
their raw text content, producing visible garbage like "}});".

The visual floating action button (FAB) is therefore injected via
  st.components.v1.html(FAB_HTML, height=0, scrolling=False)
which runs inside its own sandboxed iframe and CAN execute JavaScript.
From that iframe, window.parent.document refers to the Streamlit app frame,
so we manipulate the parent DOM to create/update the FAB element.

The hidden st.button() drives Streamlit session state; its container is
completely removed from layout by CSS (display:none + position:absolute offscreen).
"""
import streamlit as st
import streamlit.components.v1 as components
import datetime
from ui.chatbot_theme import CHATBOT_THEME_CSS
from ai.clinical_copilot import process_copilot_query


# ── Widget init ───────────────────────────────────────────────────────────────

def init_copilot_state():
    """Initializes session state variables for the copilot."""
    if "copilot_open" not in st.session_state:
        st.session_state.copilot_open = False
    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = [
            {
                "role": "assistant",
                "content": (
                    "**Hello! I am your AI Clinical Copilot.** ⚕️  \n"
                    "I can perform health calculations, explain diagnostics, analyze lab reports, and navigate the platform.  \n"
                    "How can I assist you with clinical intelligence today?"
                ),
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            }
        ]
    if "copilot_autofill_pending" not in st.session_state:
        st.session_state.copilot_autofill_pending = None
    if "copilot_show_summary" not in st.session_state:
        st.session_state.copilot_show_summary = False
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = ""
    if "guided_assessment" not in st.session_state:
        st.session_state.guided_assessment = {
            "active": False,
            "module": None,
            "current_step": 0,
            "answers": {}
        }


# ── Main render ───────────────────────────────────────────────────────────────

def render_copilot():
    """Renders the copilot chatbot floating button and panel on the page."""
    init_copilot_state()

    # ── Step 1: Inject chat-panel CSS (st.markdown is fine for CSS-only) ──
    st.markdown(CHATBOT_THEME_CSS, unsafe_allow_html=True)

    # ── Step 2: Native Streamlit toggle button (styled as FAB via CSS) ──
    # The CSS in chatbot_theme.py selects the element immediately following this marker
    # and fixes it to the bottom right corner.
    st.markdown('<div class="copilot-fab-marker"></div>', unsafe_allow_html=True)
    btn_text = "✖" if st.session_state.copilot_open else "🤖"
    if st.button(btn_text, key="copilot_toggle_btn"):
        st.session_state.copilot_open = not st.session_state.copilot_open
        st.rerun()

    # ── Step 3: Render chat panel when open ───────────────────────────────────
    if st.session_state.copilot_open:
        # Position marker — the CSS selects the element-container containing this div
        st.markdown('<div class="copilot-marker"></div>', unsafe_allow_html=True)

        # Header block
        st.markdown(
            '<div class="copilot-header">'
            '<div class="copilot-header-title">⚕️ ClinicalAI Copilot</div>'
            '<div class="copilot-header-status"><span class="copilot-status-dot"></span>Online</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Chat Messages Box
        chat_box = st.container(height=360)
        with chat_box:
            for msg in st.session_state.copilot_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    st.caption(f"Time: {msg.get('timestamp', '')}")

            # Handle summary rendering inside the chat box if requested
            if st.session_state.copilot_show_summary:
                from ai.patient_summary_engine import render_summary_interface
                st.divider()
                render_summary_interface()
                if st.button("Close Summary Preview", use_container_width=True, key="close_summary_panel"):
                    st.session_state.copilot_show_summary = False
                    st.rerun()

            # Handle pending autofills
            if st.session_state.copilot_autofill_pending:
                autofill_data = st.session_state.copilot_autofill_pending
                st.divider()
                st.markdown("<p style='color:#00f2ff; font-weight:600; font-size:0.85rem;'>💡 Telemetry Autofill Available</p>", unsafe_allow_html=True)

                fill_desc = ", ".join([f"{k.replace('adv_', '').replace('h_', '').title()}: {v}" for k, v in autofill_data.items()])
                st.caption(f"Applies: {fill_desc}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Apply Autofill", use_container_width=True, key="confirm_autofill"):
                        st.session_state.copilot_autofill_queue = autofill_data
                        st.session_state.copilot_autofill_pending = None
                        st.success("Autofill queued! Appending telemetry...")
                        st.rerun()
                with col2:
                    if st.button("Dismiss", use_container_width=True, key="dismiss_autofill"):
                        st.session_state.copilot_autofill_pending = None
                        st.rerun()

        # Quick Action Suggestion Chips
        st.markdown('<div class="copilot-chips-container">', unsafe_allow_html=True)
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        col_c5, col_c6, col_c7 = st.columns(3)

        chips = [
            ("Explain BMI",    col_c1, "Explain BMI"),
            ("Calculate BMI",  col_c2, "Calculate BMI"),
            ("Explain BP",     col_c3, "Explain Blood Pressure"),
            ("Explain Sugar",  col_c4, "Explain Glucose"),
            ("Explain Chol",   col_c5, "Explain Cholesterol"),
            ("Health Tips",    col_c6, "Show Health Tips"),
            ("Explain Pred",   col_c7, "Explain Prediction"),
        ]

        for label, col, query_text in chips:
            with col:
                if st.button(label, key=f"chip_{label.lower().replace(' ', '_')}", use_container_width=True):
                    st.session_state.copilot_messages.append({
                        "role": "user",
                        "content": query_text,
                        "timestamp": datetime.datetime.now().strftime("%H:%M")
                    })
                    api_key = st.session_state.get("gemini_api_key", "")
                    result = process_copilot_query(query_text, api_key=api_key)
                    st.session_state.copilot_messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "timestamp": datetime.datetime.now().strftime("%H:%M")
                    })
                    if result["autofill"]:
                        st.session_state.copilot_autofill_pending = result["autofill"]
                    if result["show_summary"]:
                        st.session_state.copilot_show_summary = True
                    if result["navigation"]:
                        from ai.navigation_assistant import perform_navigation
                        st.session_state.copilot_open = False
                        perform_navigation(result["navigation"])
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Chat Input Form
        st.markdown('<div class="copilot-input-area">', unsafe_allow_html=True)
        with st.form("copilot_chat_form", clear_on_submit=True):
            col_input, col_send = st.columns([5, 1])
            with col_input:
                user_message = st.text_input(
                    "Ask a clinical question...",
                    placeholder="e.g. My height is 180cm, weight is 80kg",
                    label_visibility="collapsed",
                    key="copilot_user_text_input"
                )
            with col_send:
                submitted = st.form_submit_button("➔")

            if submitted and user_message.strip():
                st.session_state.copilot_messages.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                })
                api_key = st.session_state.get("gemini_api_key", "")
                result = process_copilot_query(user_message, api_key=api_key)
                st.session_state.copilot_messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                })
                if result["autofill"]:
                    st.session_state.copilot_autofill_pending = result["autofill"]
                if result["show_summary"]:
                    st.session_state.copilot_show_summary = True
                if result["navigation"]:
                    from ai.navigation_assistant import perform_navigation
                    st.session_state.copilot_open = False
                    perform_navigation(result["navigation"])
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Clear chat history
        if st.button("🗑️ Clear Copilot Chat History", use_container_width=True, key="clear_copilot_chat"):
            st.session_state.copilot_messages = [
                {
                    "role": "assistant",
                    "content": "Chat history cleared. How can I assist you with clinical intelligence today?",
                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                }
            ]
            st.session_state.copilot_autofill_pending = None
            st.session_state.copilot_show_summary = False
            st.session_state.guided_assessment = {
                "active": False,
                "module": None,
                "current_step": 0,
                "answers": {}
            }
            st.rerun()

        st.divider()
        with st.expander("⚙️ ClinicalAI Settings", expanded=False):
            api_key = st.text_input(
                "Gemini API Key (Optional)",
                value=st.session_state.get("gemini_api_key", ""),
                type="password",
                placeholder="AIzaSy...",
                help="Enter a free Gemini API Key to enable advanced health education, predictor explanations, and conversational support."
            )
            if api_key != st.session_state.get("gemini_api_key", ""):
                st.session_state.gemini_api_key = api_key
                st.success("API Key updated!")
                st.rerun()
