"""
Chatbot Theme CSS.
NOTE: JavaScript is NOT placed here anymore — Streamlit strips <script> tags from
st.markdown(unsafe_allow_html=True) and shows the text content as raw visible text.
All JS is injected via st.components.v1.html() in copilot_widget.py instead.
"""

CHATBOT_THEME_CSS = """
<style>
/* ══════════════════════════════════════════════════════════════════
   FLOATING ACTION BUTTON (Native Streamlit Button styled as FAB)
   ══════════════════════════════════════════════════════════════════ */
/* Hide the marker itself */
div[data-testid="stElementContainer"]:has(div.copilot-fab-marker),
div[data-testid="element-container"]:has(div.copilot-fab-marker) {
    display: none !important;
    height: 0 !important;
    width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    position: absolute !important;
}

/* Make the button's container fixed at the bottom right */
div[data-testid="stElementContainer"]:has(div.copilot-fab-marker) + div[data-testid="stElementContainer"],
div[data-testid="element-container"]:has(div.copilot-fab-marker) + div[data-testid="element-container"] {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 2147483647 !important;
    width: 56px !important;
    height: 56px !important;
}

/* Style the button to look like a circular FAB */
div[data-testid="stElementContainer"]:has(div.copilot-fab-marker) + div[data-testid="stElementContainer"] button,
div[data-testid="element-container"]:has(div.copilot-fab-marker) + div[data-testid="element-container"] button {
    width: 56px !important;
    height: 56px !important;
    min-height: 56px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #7b2cbf 0%, #00f2ff 100%) !important;
    color: #fff !important;
    font-size: 24px !important;
    border: 1.5px solid rgba(255,255,255,0.30) !important;
    box-shadow: 0 4px 20px rgba(0,242,255,0.45), 0 0 15px rgba(123,44,191,0.35) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    animation: copilot-pulse 3s infinite ease-in-out !important;
}

/* Ensure the text inside the button inherits the correct size and removes padding */
div[data-testid="stElementContainer"]:has(div.copilot-fab-marker) + div[data-testid="stElementContainer"] button p,
div[data-testid="element-container"]:has(div.copilot-fab-marker) + div[data-testid="element-container"] button p,
div[data-testid="stElementContainer"]:has(div.copilot-fab-marker) + div[data-testid="stElementContainer"] button span,
div[data-testid="element-container"]:has(div.copilot-fab-marker) + div[data-testid="element-container"] button span {
    font-size: 24px !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stElementContainer"]:has(div.copilot-fab-marker) + div[data-testid="stElementContainer"] button:hover,
div[data-testid="element-container"]:has(div.copilot-fab-marker) + div[data-testid="element-container"] button:hover {
    transform: scale(1.12) !important;
    box-shadow: 0 0 32px rgba(0,242,255,0.75), 0 0 20px rgba(123,44,191,0.55) !important;
}

@keyframes copilot-pulse {
    0%,100% { box-shadow: 0 4px 20px rgba(0,242,255,0.40), 0 0 15px rgba(123,44,191,0.30); }
    50%      { box-shadow: 0 4px 28px rgba(0,242,255,0.65), 0 0 25px rgba(123,44,191,0.50); }
}

/* ══════════════════════════════════════════════════════════════════
   FLOATING CHAT WINDOW (slides in from right)
   ══════════════════════════════════════════════════════════════════ */
div[data-testid="element-container"]:has(div.copilot-marker) {
    position: fixed !important;
    top: 5vh !important;
    right: 24px !important;
    width: 420px !important;
    height: 85vh !important;
    background: rgba(5,11,22,0.94) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border: 1px solid rgba(0,242,255,0.25) !important;
    border-radius: 24px !important;
    padding: 0 !important;
    box-shadow: 0 20px 80px rgba(0,0,0,0.8), 0 0 40px rgba(123,44,191,0.2) !important;
    z-index: 999995 !important;
    overflow: hidden !important;
    animation: slide-in-right 0.35s cubic-bezier(0.16,1,0.3,1) forwards;
}
@keyframes slide-in-right {
    from { opacity:0; transform:translateX(50px) scale(0.98); }
    to   { opacity:1; transform:translateX(0) scale(1); }
}
@media (max-width:768px) {
    div[data-testid="element-container"]:has(div.copilot-marker) {
        top:0!important; right:0!important;
        width:100%!important; height:100vh!important;
        border-radius:0!important; border:none!important;
    }
}

/* Chat Header */
.copilot-header {
    background: linear-gradient(90deg,rgba(123,44,191,0.15) 0%,rgba(5,11,22,0) 100%);
    border-bottom: 1px solid rgba(0,242,255,0.15);
    padding: 1.1rem 1.4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.copilot-header-title {
    font-family:'Fraunces',serif; font-size:1.25rem; font-weight:700;
    color:#fff; text-shadow:0 0 10px rgba(0,242,255,0.3);
    display:flex; align-items:center; gap:0.6rem;
}
.copilot-header-status {
    font-family:'DM Mono',monospace; font-size:0.65rem;
    letter-spacing:0.1em; color:#00f2ff; text-transform:uppercase;
    display:flex; align-items:center; gap:0.3rem;
}
.copilot-status-dot {
    width:6px; height:6px; background:#00f2ff;
    border-radius:50%; box-shadow:0 0 8px #00f2ff;
}

/* Messages */
.copilot-messages-box {
    height:400px; overflow-y:auto; padding:1.25rem;
    display:flex; flex-direction:column; gap:1rem;
}
.copilot-messages-box::-webkit-scrollbar { width:5px; }
.copilot-messages-box::-webkit-scrollbar-track { background:transparent; }
.copilot-messages-box::-webkit-scrollbar-thumb {
    background:rgba(0,242,255,0.15); border-radius:4px;
}
.copilot-messages-box::-webkit-scrollbar-thumb:hover { background:rgba(0,242,255,0.3); }

.copilot-msg {
    display:flex; flex-direction:column; max-width:85%;
    border-radius:16px; padding:0.8rem 1.1rem;
    font-size:0.9rem; line-height:1.4;
}
.copilot-msg-user {
    align-self:flex-end;
    background:linear-gradient(135deg,rgba(123,44,191,0.25) 0%,rgba(0,242,255,0.1) 100%);
    border:1px solid rgba(0,242,255,0.25); color:#fff; border-bottom-right-radius:4px;
}
.copilot-msg-assistant {
    align-self:flex-start;
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.05); color:#edf2f7; border-bottom-left-radius:4px;
}
.copilot-msg-meta {
    font-family:'DM Mono',monospace; font-size:0.65rem;
    color:#6b8aab; margin-top:0.3rem; align-self:flex-end;
}
.copilot-msg-assistant .copilot-msg-meta { align-self:flex-start; }

/* Quick Action Chips */
.copilot-chips-container {
    padding:0.2rem 1.25rem; background:transparent;
    display:flex; flex-wrap:wrap; gap:0.4rem;
}
.copilot-chips-container button {
    background:rgba(255,255,255,0.04)!important;
    border:1px solid rgba(0,242,255,0.2)!important; color:#00f2ff!important;
    border-radius:16px!important; font-size:0.72rem!important;
    padding:3px 10px!important; font-weight:600!important;
    text-transform:none!important; box-shadow:none!important;
    height:auto!important; min-height:0px!important; line-height:1.2!important;
    transition:all 0.2s ease!important;
}
.copilot-chips-container button:hover {
    background:rgba(0,242,255,0.12)!important; border-color:#00f2ff!important;
    color:#fff!important; transform:translateY(-1px)!important;
}

/* Chat Input Bar */
.copilot-input-area {
    padding:0.5rem 1.25rem 1.25rem;
    border-top:1px solid rgba(255,255,255,0.05);
    background:rgba(5,11,22,0.98);
}

/* Autofill button */
.autofill-btn-container { margin-top:0.75rem; display:flex; justify-content:flex-end; }
</style>
"""
