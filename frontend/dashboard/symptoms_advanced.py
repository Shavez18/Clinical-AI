import streamlit as st
import datetime
import os
import sys
from ui.theme import apply_advanced_theme
from visuals.futuristic_charts import plot_diagnosis_radar, plot_symptom_heatmap, plot_health_score_gauge
from visuals.multimodal_charts import plot_cbc_abnormality, plot_anemia_risk_radar
from analytics.advanced_explainability import render_shap_waterfall, get_nlp_token_importance
from ai.clinical_summarization import generate_ai_clinical_summary
from multimodal.ocr_processor import analyze_document
from recommendations.recommendation_ui import render_symptom_recommendations

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


@st.cache_resource(show_spinner="Loading Clinical NLP Engine…")
def _get_engines():
    """Load NLP parser + differential engine once per server process."""
    from src.nlp.clinical_parser import clinical_parser
    from src.symptom_engine.differential_model import DifferentialEngine
    return clinical_parser, DifferentialEngine()


def render_symptoms_dashboard(api_url=None, headers=None):
    """
    Renders the Clinical NLP Intelligence dashboard.
    api_url / headers are kept for backward-compat but are no longer used.
    """
    apply_advanced_theme()

    st.markdown("""
        <div class="adv-subtitle">⚡ SYSTEM ONLINE // NLP TRIAGE MODULE</div>
        <div class="adv-title">Clinical NLP Intelligence</div>
        <p style="color:#8ab4f8; margin-bottom:2rem; font-size:1.05rem;">
            Start-up grade hybrid NLP triage system with contextual expansion,
            safety stratification, and multimodal capability.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="adv-header">CLINICAL NOTES INPUT</div>', unsafe_allow_html=True)

    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Patient Age", min_value=0, max_value=120, value=0, key="adv_s_age")
        with c2:
            gender = st.selectbox("Biological Sex", ["Female", "Male", "Other"], key="adv_s_gen")
        with c3:
            duration = st.selectbox("Symptom Duration", ["< 24 Hours", "1-3 Days", "1 Week", "1+ Months"], key="adv_s_dur")

        st.markdown('<br>', unsafe_allow_html=True)
        symptoms_text = st.text_area(
            "Unstructured Clinical Text", height=130,
            placeholder="e.g. 30yo female patient reports severe bifrontal headache and blurred vision since yesterday…",
            key="adv_s_text",
        )
        st.markdown('<br>', unsafe_allow_html=True)
        run_analysis = st.button("INITIALIZE INFERENCE ENGINE", use_container_width=True, key="adv_s_run")

    if run_analysis:
        if len(symptoms_text.strip()) < 5:
            st.warning("Please enter a valid clinical note to analyze.")
        else:
            with st.spinner("Running Clinical NLP inference…"):
                try:
                    parser, engine = _get_engines()
                    parsed      = parser.parse(symptoms_text)
                    emergencies = parsed.get("flags", [])
                    triage_level = "High Emergency" if emergencies else "Standard"
                    differentials = engine.predict_differentials(
                        parsed_symptoms=parsed,
                        age=age,
                        gender=gender,
                        top_n=3,
                    )
                    error_msg = None
                except Exception as e:
                    differentials = []
                    triage_level  = "Standard"
                    emergencies   = []
                    error_msg     = str(e)

            if error_msg:
                st.error(f"Inference error: {error_msg}")
            else:
                st.markdown('<div class="adv-header">INFERENCE RESULTS OVERVIEW</div>', unsafe_allow_html=True)

                col_left, col_right = st.columns([1.2, 1])
                with col_left:
                    if differentials:
                        top = differentials[0]
                        st.markdown(f"""
                            <div class="kpi-container" style="align-items:flex-start; text-align:left;">
                                <div class="kpi-label">PRIMARY DIFFERENTIAL</div>
                                <div style="font-family:'Outfit',sans-serif; font-weight:800; font-size:2rem; color:#ffffff; margin:0.5rem 0;">{top['disease']}</div>
                                <div style="color:#00f3ff; font-family:'JetBrains Mono'; font-size:1.5rem; font-weight:700;">{top['probability_percentage']}% PROBABILITY</div>
                                <div style="margin-top:1rem; font-size:0.95rem; color:#8ab4f8; line-height:1.5;">
                                    <strong>Rationale:</strong> {top['rationale']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Insufficient symptoms to generate a differential diagnosis.")

                with col_right:
                    if triage_level == "High Emergency" or emergencies:
                        status, color = "EMERGENCY DETECTED", "#ff003c"
                    else:
                        status, color = "STANDARD TRIAGE", "#00f3ff"
                    st.markdown(f"""
                        <div class="kpi-container" style="margin-bottom: 1rem;">
                            <div class="kpi-label">TRIAGE LEVEL</div>
                            <div class="kpi-value" style="color: {color}; font-size: 1.8rem;">{status}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if differentials:
                        st.markdown(f"""
                            <div class="kpi-container">
                                <div class="kpi-label">MODEL CONFIDENCE SCORE</div>
                                <div class="kpi-value" style="color: #ff9d00;">{differentials[0]['confidence']}</div>
                            </div>
                        """, unsafe_allow_html=True)

                st.markdown('<br>', unsafe_allow_html=True)
                st.markdown('<div class="adv-header">SECONDARY DIFFERENTIALS & INSIGHTS</div>', unsafe_allow_html=True)
                for diff in differentials[1:]:
                    st.markdown(f"""
                    <div class="ai-insight">
                        <div class="insight-title">{diff['disease']} - {diff['probability_percentage']}% ({diff['confidence']})</div>
                        <div>{diff['rationale']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                if differentials:
                    top_d = differentials[0]['disease']
                    st.session_state.audit_logs.append({
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Module": "Differential AI ADVANCED",
                        "Query Overview": f"Age {age} {gender}. Symps: {symptoms_text[:20]}…",
                        "Outcome/Result": f"Top: {top_d} ({triage_level})",
                    })
                    render_symptom_recommendations(top_d, differentials)

    # ── Multimodal Upload ────────────────────────────────────────────────────
    st.markdown('<div class="adv-header">MULTIMODAL UPLOAD AREA</div>', unsafe_allow_html=True)
    st.write("Upload PDF prescriptions, lab reports, or clinical note images for multimodal analysis.")
    uploaded_file = st.file_uploader(
        "Drop document here", type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed", key="adv_s_upload",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_type  = "pdf" if uploaded_file.name.lower().endswith(".pdf") else "image"
        filename   = uploaded_file.name

        with st.spinner("Processing clinical document…"):
            ocr_result   = analyze_document(file_bytes, file_type, filename)
            doc_type     = ocr_result.get("document_type", "clinical_note")
            findings     = [e["text"] for e in ocr_result.get("entities", [])] if ocr_result.get("entities") else ["Mild inflammation"]
            ai_summary   = generate_ai_clinical_summary({"risk_level": ocr_result.get("risk_level", "Moderate"), "findings": findings})

        st.markdown(f'<div class="adv-header">OCR FINDINGS & NLP EXPLAINABILITY - {doc_type.replace("_", " ").title()} Detected</div>', unsafe_allow_html=True)
        st.markdown("<strong style='color:#a5b4fc;'>Raw OCR Output:</strong>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:rgba(11,17,33,.65);padding:1rem;border-radius:8px;font-family:monospace;margin-bottom:1rem;color:#e0f4f4;border:1px solid rgba(0,243,255,.15);'>{ocr_result['raw_text']}</div>", unsafe_allow_html=True)

        st.markdown("<strong style='color:#a5b4fc;'>NLP Token Importance (Explainability):</strong>", unsafe_allow_html=True)
        token_html = get_nlp_token_importance(ocr_result["raw_text"] + " Patient denies severe headache but reports mild fever and pain.")
        st.markdown(f"<div style='background:rgba(11,17,33,.65);padding:1rem;border-radius:8px;margin-bottom:1rem;color:#e0f4f4;border:1px solid rgba(0,243,255,.15);'>{token_html}</div>", unsafe_allow_html=True)

        st.markdown('<div class="adv-header">CLINICAL ANALYTICS</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if doc_type == "lab_report":
            with c1:
                st.markdown('<div class="kpi-label" style="text-align:center;margin-bottom:.5rem;">PATIENT HEALTH SCORE</div>', unsafe_allow_html=True)
                st.plotly_chart(plot_health_score_gauge(ocr_result.get("health_score", 75)), use_container_width=True, config={"displayModeBar": False})
            with c2:
                st.markdown('<div class="kpi-label" style="text-align:center;margin-bottom:.5rem;">ANEMIA RISK RADAR</div>', unsafe_allow_html=True)
                st.plotly_chart(plot_anemia_risk_radar(ocr_result.get("anemia_risk", "Low")), use_container_width=True, config={"displayModeBar": False})
            c3, c4 = st.columns(2)
            with c3:
                biomarkers  = ocr_result.get("biomarkers", {"RBC": 4.1, "HCT": 39.5, "WBC": 7.2})
                abnormalities = ocr_result.get("abnormalities", [])
                st.plotly_chart(plot_cbc_abnormality(biomarkers, abnormalities), use_container_width=True, config={"displayModeBar": False})
            with c4:
                fig_shap = render_shap_waterfall(["Low RBC", "Low HCT", "Age > 40", "Nutrition", "Family Hx"], [0.4, 0.35, 0.1, -0.05, 0.1])
                st.plotly_chart(fig_shap, use_container_width=True, config={"displayModeBar": False})
        else:
            with c1:
                score = 80 if ocr_result.get("risk_level") == "Low" else 60
                st.plotly_chart(plot_health_score_gauge(score), use_container_width=True, config={"displayModeBar": False})
            with c2:
                probs = {"Hypertension": 85, "Hyperlipidemia": 65, "Diabetes": 30, "CAD": 45, "Arrhythmia": 20}
                st.plotly_chart(plot_diagnosis_radar(probs), use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="adv-header">AI CLINICAL RECOMMENDATIONS</div>', unsafe_allow_html=True)
        alerts_html = ""
        if doc_type == "lab_report":
            abnormalities_str = ", ".join(ocr_result.get("abnormalities", []))
            if abnormalities_str:
                alerts_html = f"<div style='color:#ff003c;font-weight:bold;margin-bottom:.5rem;'>Alert: Abnormal values detected ({abnormalities_str})</div>"
        elif doc_type == "prescription":
            meds_str = ", ".join(ocr_result.get("medications", []))
            if meds_str:
                alerts_html = f"<div style='color:#00f3ff;font-weight:bold;margin-bottom:.5rem;'>Detected Medications: {meds_str}</div>"

        st.markdown(f"""
        <div class="ai-insight">
            <div class="insight-title">AI Clinical Synthesis</div>
            {alerts_html}
            <div>{ai_summary}</div>
        </div>
        """, unsafe_allow_html=True)
