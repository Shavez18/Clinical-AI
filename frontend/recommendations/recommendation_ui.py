"""
recommendation_ui.py
────────────────────────────────────────────────────────────────────────────
Streamlit UI layer for the Risk-Based Care Plan & Specialist Recommendation
System.  Called AFTER existing prediction results are rendered.

All functions are purely additive — they read data and render HTML.
They do NOT modify any upstream prediction, model, or session state.

Public entry points
───────────────────
  render_diabetes_recommendations(risk_percent, features)
  render_heart_recommendations(risk_percent, features)
  render_symptom_recommendations(top_diagnosis, differentials)
  render_drug_recommendations(toxicity_score, interactions, drug_list)
"""

from __future__ import annotations
import streamlit as st
import io
from fpdf import FPDF

from recommendations.risk_interpreter import (
    interpret_risk_score,
    interpret_risk_category,
    interpret_drug_severity,
    classify_symptom_category,
)
from recommendations.specialist_recommender import (
    recommend_diabetes_specialist,
    recommend_heart_specialist,
    recommend_symptom_specialist,
    recommend_drug_specialist,
)
from recommendations.care_plan_engine import (
    get_diabetes_care_plan,
    get_heart_care_plan,
    get_symptom_care_plan,
    get_drug_care_plan,
)
from recommendations.wellness_guidance import get_wellness_guidance


# ── Shared CSS (injected once per page render) ────────────────────────────────
_CSS_INJECTED = False

_RECOMMENDATION_CSS = """
<style>
/* ── Care Plan Container ─── */
.rcp-section-header {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #00f2ff;
    margin: 2.5rem 0 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    text-shadow: 0 0 8px rgba(0,242,255,0.4);
}
.rcp-section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,242,255,0.3), transparent);
}

/* ── Care Plan Card ────── */
.rcp-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,242,255,0.15);
    border-radius: 18px;
    padding: 1.6rem 2rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s, box-shadow 0.3s;
}
.rcp-card:hover {
    border-color: rgba(0,242,255,0.35);
    box-shadow: 0 0 24px rgba(0,242,255,0.10);
}
.rcp-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00f2ff, transparent);
    opacity: 0.6;
}

/* ── Risk Badge ────────── */
.rcp-risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 1rem;
    border-radius: 50px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

/* ── Specialist Card ───── */
.rcp-specialist-card {
    background: rgba(0,242,255,0.04);
    border: 1px solid rgba(0,242,255,0.2);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    display: flex;
    gap: 1.2rem;
    align-items: flex-start;
    margin-bottom: 0.8rem;
}
.rcp-specialist-icon {
    font-size: 2.2rem;
    line-height: 1;
    flex-shrink: 0;
}
.rcp-specialist-title {
    font-family: 'Fraunces', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.2rem;
}
.rcp-specialist-role {
    font-size: 0.85rem;
    color: #b0d2e6;
    line-height: 1.5;
    margin-bottom: 0.6rem;
}
.rcp-specialist-reason {
    font-size: 0.82rem;
    color: #00f2ff;
    font-family: 'DM Mono', monospace;
    border-left: 2px solid rgba(0,242,255,0.4);
    padding-left: 0.7rem;
    line-height: 1.4;
}
.rcp-next-step {
    margin-top: 0.8rem;
    font-size: 0.83rem;
    color: #34d399;
    font-weight: 600;
}

/* ── Action & Risk Factor Lists ── */
.rcp-list-item {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.88rem;
    color: #d0e8f5;
    line-height: 1.4;
}
.rcp-list-item:last-child { border-bottom: none; }
.rcp-list-bullet {
    color: #00f2ff;
    font-size: 0.6rem;
    margin-top: 0.35rem;
    flex-shrink: 0;
}

/* ── Follow-Up Timeline Card ── */
.rcp-timeline-card {
    background: rgba(52,211,153,0.05);
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-top: 0.6rem;
}
.rcp-timeline-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #34d399;
    margin-bottom: 0.6rem;
    font-weight: 700;
}
.rcp-timeline-item {
    font-size: 0.84rem;
    color: #a7f3d0;
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(52,211,153,0.08);
    display: flex;
    gap: 0.5rem;
}

/* ── Wellness Tip Cards ── */
.rcp-wellness-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 0.8rem;
    margin-top: 0.5rem;
}
.rcp-wellness-tip {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    transition: border-color 0.25s, transform 0.25s;
}
.rcp-wellness-tip:hover {
    border-color: rgba(0,242,255,0.3);
    transform: translateY(-3px);
}
.rcp-wellness-icon { font-size: 1.4rem; margin-bottom: 0.4rem; }
.rcp-wellness-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #00f2ff;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.rcp-wellness-detail { font-size: 0.8rem; color: #8ab4c8; line-height: 1.4; }

/* ── Summary Banner ───── */
.rcp-summary-banner {
    background: linear-gradient(135deg, rgba(13,140,140,0.15) 0%, rgba(0,242,255,0.05) 100%);
    border: 1px solid rgba(0,242,255,0.2);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-top: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.rcp-summary-item { text-align: center; }
.rcp-summary-val {
    font-family: 'Fraunces', serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #00f2ff;
}
.rcp-summary-key {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6b8aab;
    margin-top: 0.1rem;
}

/* ── Disclaimer ─────── */
.rcp-disclaimer {
    margin-top: 1.2rem;
    padding: 0.9rem 1.2rem;
    background: rgba(251,191,36,0.05);
    border: 1px solid rgba(251,191,36,0.15);
    border-radius: 10px;
    font-size: 0.76rem;
    color: #92740a;
    font-family: 'DM Mono', monospace;
    line-height: 1.5;
}
</style>
"""


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _inject_css():
    global _CSS_INJECTED
    if not _CSS_INJECTED:
        st.markdown(_RECOMMENDATION_CSS, unsafe_allow_html=True)
        _CSS_INJECTED = True


def _section_header(label: str):
    st.markdown(
        f'<div class="rcp-section-header">⚕ {label}</div>',
        unsafe_allow_html=True
    )


def _render_risk_badge(risk_info: dict):
    st.markdown(f"""
    <div class="rcp-risk-badge"
         style="background:{risk_info['bg_color']}; border:1px solid {risk_info['border']}; color:{risk_info['color']};">
        {risk_info['emoji']}&nbsp; {risk_info['label']}
    </div>
    """, unsafe_allow_html=True)


def _render_specialist_card(specialist: dict):
    st.markdown(f"""
    <div class="rcp-specialist-card">
        <div class="rcp-specialist-icon">{specialist['icon']}</div>
        <div style="flex:1;">
            <div class="rcp-specialist-title">{specialist['specialty']}</div>
            <div class="rcp-specialist-role">{specialist['role']}</div>
            <div class="rcp-specialist-reason">Reason: {specialist['reason']}</div>
            <div class="rcp-next-step">→ {specialist['next_step']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_list(items: list[str], bullet_color: str = "#00f2ff"):
    items_html = "".join(
        f'<div class="rcp-list-item">'
        f'<span class="rcp-list-bullet" style="color:{bullet_color};">●</span>'
        f'<span>{item}</span></div>'
        for item in items
    )
    st.markdown(items_html, unsafe_allow_html=True)


def _render_follow_up(follow_up_items: list[str], timeline: str):
    items_html = "".join(
        f'<div class="rcp-timeline-item"><span style="color:#34d399;">→</span><span>{item}</span></div>'
        for item in follow_up_items
    )
    st.markdown(f"""
    <div class="rcp-timeline-card">
        <div class="rcp-timeline-label">⏱ Follow-Up Timeline · {timeline}</div>
        {items_html}
    </div>
    """, unsafe_allow_html=True)


def _render_wellness_grid(wellness_tips: list[dict]):
    if not wellness_tips:
        return
    tips_html = "".join(
        f'<div class="rcp-wellness-tip">'
        f'<div class="rcp-wellness-icon">{t["icon"]}</div>'
        f'<div class="rcp-wellness-label">{t["tip"]}</div>'
        f'<div class="rcp-wellness-detail">{t["detail"]}</div>'
        f'</div>'
        for t in wellness_tips
    )
    st.markdown(f'<div class="rcp-wellness-grid">{tips_html}</div>', unsafe_allow_html=True)


def _render_summary_banner(specialist_name: str, risk_label: str, timeline: str):
    st.markdown(f"""
    <div class="rcp-summary-banner">
        <div class="rcp-summary-item">
            <div class="rcp-summary-val">{risk_label}</div>
            <div class="rcp-summary-key">Risk Stratification</div>
        </div>
        <div class="rcp-summary-item">
            <div class="rcp-summary-val">{specialist_name}</div>
            <div class="rcp-summary-key">Recommended Specialist</div>
        </div>
        <div class="rcp-summary-item">
            <div class="rcp-summary-val">{timeline}</div>
            <div class="rcp-summary-key">Target Follow-Up</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_disclaimer():
    st.markdown("""
    <div class="rcp-disclaimer">
        ⚠ CLINICAL DISCLAIMER: This care plan and specialist recommendation is generated by an AI system
        for informational and decision-support purposes only. It does not constitute a medical diagnosis or
        prescription. Always consult a licensed healthcare professional before making any clinical decisions.
    </div>
    """, unsafe_allow_html=True)


# ── PDF Report Generator ─────────────────────────────────────────────────────

class _CarePlanPDF(FPDF):
    """Custom FPDF subclass with header/footer branding."""

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 160, 200)
        self.cell(0, 8, "ClinicalAI Enterprise  |  Care Plan Report", align="R", ln=True)
        self.ln(2)
        self.set_draw_color(0, 180, 220)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-18)
        self.set_draw_color(0, 180, 220)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(
            0, 6,
            "DISCLAIMER: AI-generated for decision-support only. "
            "Consult a licensed healthcare professional.  "
            f"Page {self.page_no()}",
            align="C"
        )


def _safe(text: str) -> str:
    """Strip characters outside latin-1 so FPDF core fonts don't raise."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _section_title_pdf(pdf: _CarePlanPDF, title: str):
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 180, 220)
    pdf.cell(0, 7, _safe(title), ln=True)
    pdf.set_draw_color(0, 180, 220)
    pdf.set_line_width(0.3)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(3)
    pdf.set_text_color(40, 40, 40)


def generate_care_plan_pdf_bytes(
    module: str,
    risk_label: str,
    care_plan: dict,
    specialist: dict,
    wellness_tips: list[dict]
) -> bytes:
    """
    Generates a styled PDF care plan and returns the raw bytes.
    Uses fpdf2 (pure Python, no external binaries required).
    """
    pdf = _CarePlanPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Title block ──────────────────────────────────────────────────
    pdf.set_fill_color(10, 30, 50)
    pdf.rect(pdf.l_margin, pdf.get_y(), pdf.w - pdf.l_margin - pdf.r_margin, 22, style="F")
    pdf.set_xy(pdf.l_margin + 4, pdf.get_y() + 3)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(0, 220, 255)
    pdf.cell(0, 8, _safe("RISK-BASED CARE PLAN & SPECIALIST RECOMMENDATION"), ln=True)
    pdf.set_x(pdf.l_margin + 4)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(160, 200, 220)
    pdf.cell(0, 6, _safe(f"Module: {module}"), ln=True)
    pdf.ln(6)

    # ── Risk Category ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(35, 7, "Risk Category:", ln=False)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(200, 80, 30)
    pdf.cell(0, 7, _safe(risk_label), ln=True)
    pdf.ln(4)

    # ── Key Risk Factors ─────────────────────────────────────────────
    if care_plan.get("risk_factors"):
        _section_title_pdf(pdf, "Key Risk Factors")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        for rf in care_plan["risk_factors"]:
            pdf.set_x(pdf.l_margin)
            pdf.cell(6, 6, chr(149), align="R")
            pdf.set_x(pdf.l_margin + 8)
            pdf.multi_cell(0, 6, _safe(rf))
        pdf.ln(3)

    # ── Recommended Actions ──────────────────────────────────────────
    if care_plan.get("actions"):
        _section_title_pdf(pdf, "Recommended Actions")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        for act in care_plan["actions"]:
            pdf.set_x(pdf.l_margin)
            pdf.cell(6, 6, chr(149), align="R")
            pdf.set_x(pdf.l_margin + 8)
            pdf.multi_cell(0, 6, _safe(act))
        pdf.ln(3)

    # ── Recommended Specialist ───────────────────────────────────────
    _section_title_pdf(pdf, "Recommended Specialist")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    fields = [
        ("Specialty",  specialist.get("specialty", "")),
        ("Role",       specialist.get("role", "")),
        ("Reason",     specialist.get("reason", "")),
        ("Next Step",  specialist.get("next_step", "")),
    ]
    for label, value in fields:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(28, 6, f"{label}:")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.set_x(pdf.l_margin + 28)
        pdf.multi_cell(0, 6, _safe(value))
    pdf.ln(3)

    # ── Follow-Up Guidance ───────────────────────────────────────────
    if care_plan.get("follow_up"):
        _section_title_pdf(pdf, "Follow-Up Guidance")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        for fu in care_plan["follow_up"]:
            pdf.set_x(pdf.l_margin)
            pdf.cell(6, 6, chr(149), align="R")
            pdf.set_x(pdf.l_margin + 8)
            pdf.multi_cell(0, 6, _safe(fu))
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(32, 6, "Target Timeline:")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.set_x(pdf.l_margin + 32)
        pdf.cell(0, 6, _safe(care_plan.get("timeline", "As directed")), ln=True)
        pdf.ln(3)

    # ── Wellness Recommendations ─────────────────────────────────────
    if wellness_tips:
        _section_title_pdf(pdf, "Wellness Recommendations")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        for wt in wellness_tips:
            tip = _safe(wt.get("tip", ""))
            detail = _safe(wt.get("detail", ""))
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(6, 6, chr(149), align="R")
            pdf.set_x(pdf.l_margin + 8)
            pdf.cell(0, 6, tip, ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_x(pdf.l_margin + 8)
            pdf.multi_cell(0, 5, detail)
        pdf.ln(3)

    return bytes(pdf.output())


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE HELPERS (for PDF integration)
# ══════════════════════════════════════════════════════════════════════════════

def _save_to_pdf_store(module: str, risk_info: dict, care_plan: dict,
                       specialist: dict, wellness: list):
    """Accumulates care plan entries into session state for PDF export."""
    if "pdf_care_plans" not in st.session_state:
        st.session_state.pdf_care_plans = []
    # Replace existing entry for the same module (prevent duplicates)
    st.session_state.pdf_care_plans = [
        e for e in st.session_state.pdf_care_plans if e.get("module") != module
    ]
    st.session_state.pdf_care_plans.append({
        "module":     module,
        "risk_label": risk_info["label"],
        "tier":       risk_info["tier"],
        "care_plan":  care_plan,
        "specialist": specialist,
        "wellness":   wellness,
    })


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINTS
# ══════════════════════════════════════════════════════════════════════════════

def render_diabetes_recommendations(risk_percent: float, features: dict | None = None):
    """
    Renders the full diabetes care plan section below existing results.

    Parameters
    ----------
    risk_percent : float   — raw risk % from the existing model (not modified)
    features     : dict    — input feature dict (optional, for display only)
    """
    _inject_css()

    risk_info  = interpret_risk_score(risk_percent)
    tier       = risk_info["tier"]
    care_plan  = get_diabetes_care_plan(tier)
    specialist = recommend_diabetes_specialist(tier)
    wellness   = get_wellness_guidance("diabetes", tier)

    # Save to session state for PDF export
    _save_to_pdf_store("Diabetes Intelligence", risk_info, care_plan, specialist, wellness)

    _section_header("RISK-BASED CARE PLAN — DIABETES INTELLIGENCE")

    col_main, col_spec = st.columns([1.3, 1])

    with col_main:
        st.markdown('<div class="rcp-card">', unsafe_allow_html=True)
        _render_risk_badge(risk_info)

        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Key Risk Factors</div>',
            unsafe_allow_html=True
        )
        _render_list(care_plan["risk_factors"], bullet_color="#f59e0b")

        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin:1rem 0 0.5rem;">'
            'Recommended Actions</div>',
            unsafe_allow_html=True
        )
        _render_list(care_plan["actions"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col_spec:
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Recommended Specialist</div>',
            unsafe_allow_html=True
        )
        _render_specialist_card(specialist)
        _render_follow_up(care_plan["follow_up"], care_plan["timeline"])

    st.markdown(
        '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
        'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin:1.5rem 0 0.8rem;">'
        'Wellness Guidance</div>',
        unsafe_allow_html=True
    )
    _render_wellness_grid(wellness)
    _render_summary_banner(specialist["specialty"], risk_info["label"], care_plan["timeline"])

    with st.expander("📄 Download Care Plan Report", expanded=False):
        pdf_bytes = generate_care_plan_pdf_bytes(
            "Diabetes Risk", risk_info["label"], care_plan, specialist, wellness
        )
        st.download_button(
            "⬇ Download as PDF",
            data=pdf_bytes,
            file_name="diabetes_care_plan.pdf",
            mime="application/pdf",
            key="dl_diab_cp"
        )

    _render_disclaimer()


def render_heart_recommendations(risk_percent: float, features: dict | None = None):
    """
    Renders the full cardiovascular care plan section below existing results.

    Parameters
    ----------
    risk_percent : float   — raw risk % from the existing model (not modified)
    features     : dict    — input feature dict (optional, for display only)
    """
    _inject_css()

    risk_info  = interpret_risk_score(risk_percent)
    tier       = risk_info["tier"]
    care_plan  = get_heart_care_plan(tier)
    specialist = recommend_heart_specialist(tier)
    wellness   = get_wellness_guidance("heart", tier)

    # Save to session state for PDF export
    _save_to_pdf_store("Cardiovascular Intelligence", risk_info, care_plan, specialist, wellness)

    _section_header("RISK-BASED CARE PLAN — CARDIOVASCULAR INTELLIGENCE")

    col_main, col_spec = st.columns([1.3, 1])

    with col_main:
        st.markdown('<div class="rcp-card">', unsafe_allow_html=True)
        _render_risk_badge(risk_info)

        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Key Risk Factors</div>',
            unsafe_allow_html=True
        )
        _render_list(care_plan["risk_factors"], bullet_color="#f59e0b")

        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin:1rem 0 0.5rem;">'
            'Recommended Actions</div>',
            unsafe_allow_html=True
        )
        _render_list(care_plan["actions"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col_spec:
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Recommended Specialist</div>',
            unsafe_allow_html=True
        )
        _render_specialist_card(specialist)
        _render_follow_up(care_plan["follow_up"], care_plan["timeline"])

    st.markdown(
        '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
        'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin:1.5rem 0 0.8rem;">'
        'Wellness Guidance</div>',
        unsafe_allow_html=True
    )
    _render_wellness_grid(wellness)
    _render_summary_banner(specialist["specialty"], risk_info["label"], care_plan["timeline"])

    with st.expander("📄 Download Care Plan Report", expanded=False):
        pdf_bytes = generate_care_plan_pdf_bytes(
            "Cardiovascular Risk", risk_info["label"], care_plan, specialist, wellness
        )
        st.download_button(
            "⬇ Download as PDF",
            data=pdf_bytes,
            file_name="heart_care_plan.pdf",
            mime="application/pdf",
            key="dl_heart_cp"
        )

    _render_disclaimer()


def render_symptom_recommendations(top_diagnosis: str, differentials: list | None = None):
    """
    Renders the NLP/symptom care plan section below differential diagnosis results.

    Parameters
    ----------
    top_diagnosis : str     — primary differential label from existing NLP engine
    differentials : list    — full differentials list (optional, for context display)
    """
    _inject_css()

    symptom_cat = classify_symptom_category(top_diagnosis)
    care_plan   = get_symptom_care_plan(symptom_cat)
    specialist  = recommend_symptom_specialist(symptom_cat)

    # Build a neutral risk_info for PDF store
    _symp_risk = {"tier": symptom_cat, "label": symptom_cat.replace("_", " ").title()}
    _save_to_pdf_store("Clinical NLP Intelligence", _symp_risk, care_plan, specialist, [])

    # Synthesise a simple risk display for symptoms (always shown as 'clinical guidance')
    cat_display_map = {
        "respiratory":         ("🫁", "#60a5fa"),
        "cardiac":             ("🫀", "#ef4444"),
        "metabolic":           ("🔬", "#f59e0b"),
        "neurological":        ("🧠", "#a78bfa"),
        "gastroenterological": ("🏥", "#34d399"),
        "general":             ("⚕️",  "#00f2ff"),
    }
    cat_icon, cat_color = cat_display_map.get(symptom_cat, ("⚕️", "#00f2ff"))

    _section_header("CLINICAL GUIDANCE — DIFFERENTIAL DIAGNOSIS SUPPORT")

    st.markdown(f"""
    <div class="rcp-card">
        <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:1rem;">
            <span style="font-size:2rem;">{cat_icon}</span>
            <div>
                <div style="font-family:'DM Mono',monospace; font-size:0.68rem; text-transform:uppercase;
                            letter-spacing:0.15em; color:#6b8aab;">Symptom Category Detected</div>
                <div style="font-family:'Fraunces',serif; font-size:1.3rem; font-weight:600;
                            color:{cat_color};">{symptom_cat.replace("_", " ").title()}</div>
            </div>
        </div>
        <div style="font-family:'DM Mono',monospace; font-size:0.68rem; text-transform:uppercase;
                    letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.4rem;">
            Primary Differential
        </div>
        <div style="font-size:1rem; font-weight:600; color:#fff; margin-bottom:1rem;">{top_diagnosis}</div>
    </div>
    """, unsafe_allow_html=True)

    col_plan, col_spec = st.columns([1.3, 1])

    with col_plan:
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Recommended Actions</div>',
            unsafe_allow_html=True
        )
        _render_list(care_plan["actions"])
        _render_follow_up(care_plan["follow_up"], care_plan["timeline"])

    with col_spec:
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Recommended Specialist</div>',
            unsafe_allow_html=True
        )
        _render_specialist_card(specialist)

    _render_summary_banner(specialist["specialty"], symptom_cat.replace("_", " ").title(), care_plan["timeline"])

    with st.expander("📄 Download Clinical Guidance Report", expanded=False):
        pdf_bytes = generate_care_plan_pdf_bytes(
            "Clinical NLP / Differential Diagnosis",
            symptom_cat.replace("_", " ").title(),
            care_plan,
            specialist,
            []
        )
        st.download_button(
            "⬇ Download as PDF",
            data=pdf_bytes,
            file_name="symptom_guidance_report.pdf",
            mime="application/pdf",
            key="dl_symp_cp"
        )

    _render_disclaimer()


def render_drug_recommendations(
    toxicity_score: float,
    interactions: list | None = None,
    drug_list: list | None = None
):
    """
    Renders drug interaction care plan below existing pharmacovigilance results.

    Parameters
    ----------
    toxicity_score : float  — toxicity score from existing analytics (0–10)
    interactions   : list   — interaction list from existing engine (read-only)
    drug_list      : list   — queried drug names (for display only)
    """
    _inject_css()

    risk_info  = interpret_drug_severity(toxicity_score)
    tier       = risk_info["tier"]
    care_plan  = get_drug_care_plan(tier)
    specialist = recommend_drug_specialist(tier)
    wellness   = get_wellness_guidance("drug", tier)

    # Save to session state for PDF export
    _save_to_pdf_store("Pharmacovigilance Intelligence", risk_info, care_plan, specialist, wellness)

    _section_header("PHARMACOVIGILANCE CARE PLAN — DRUG SAFETY GUIDANCE")

    col_main, col_spec = st.columns([1.3, 1])

    with col_main:
        st.markdown('<div class="rcp-card">', unsafe_allow_html=True)
        _render_risk_badge(risk_info)

        if drug_list:
            drugs_str = " · ".join(d.title() for d in drug_list)
            st.markdown(
                f'<div style="font-size:0.78rem; color:#6b8aab; font-family:\'DM Mono\',monospace; '
                f'margin-bottom:1rem;">Regimen: {drugs_str}</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Interaction Severity Factors</div>',
            unsafe_allow_html=True
        )
        _render_list(care_plan["risk_factors"], bullet_color="#f59e0b")

        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin:1rem 0 0.5rem;">'
            'Recommended Monitoring & Actions</div>',
            unsafe_allow_html=True
        )
        _render_list(care_plan["actions"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col_spec:
        st.markdown(
            '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
            'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin-bottom:0.5rem;">'
            'Recommended Specialist</div>',
            unsafe_allow_html=True
        )
        _render_specialist_card(specialist)
        _render_follow_up(care_plan["follow_up"], care_plan["timeline"])

    st.markdown(
        '<div style="font-family:\'DM Mono\',monospace; font-size:0.68rem; '
        'text-transform:uppercase; letter-spacing:0.15em; color:#6b8aab; margin:1.5rem 0 0.8rem;">'
        'Medication Safety Guidance</div>',
        unsafe_allow_html=True
    )
    _render_wellness_grid(wellness)
    _render_summary_banner(specialist["specialty"], risk_info["label"], care_plan["timeline"])

    with st.expander("📄 Download Safety Report", expanded=False):
        pdf_bytes = generate_care_plan_pdf_bytes(
            "Pharmacovigilance / Drug Interaction",
            risk_info["label"],
            care_plan,
            specialist,
            wellness
        )
        st.download_button(
            "⬇ Download as PDF",
            data=pdf_bytes,
            file_name="drug_safety_report.pdf",
            mime="application/pdf",
            key="dl_drug_cp"
        )

    _render_disclaimer()
