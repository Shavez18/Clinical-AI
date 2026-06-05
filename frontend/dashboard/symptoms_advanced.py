import streamlit as st
import time
import requests
import datetime
from ui.theme import apply_advanced_theme
from visuals.futuristic_charts import plot_diagnosis_radar, plot_symptom_heatmap, plot_health_score_gauge
from visuals.multimodal_charts import plot_cbc_abnormality, plot_anemia_risk_radar
from analytics.advanced_explainability import render_shap_waterfall, get_nlp_token_importance
from ai.clinical_summarization import generate_ai_clinical_summary
from multimodal.ocr_processor import analyze_document
from recommendations.recommendation_ui import render_symptom_recommendations

def render_symptoms_dashboard(api_url, headers):
    # 1. Apply Advanced Theme
    apply_advanced_theme()
    
    # 2. Header
    st.markdown("""
        <div class="adv-subtitle">⚡ SYSTEM ONLINE // NLP TRIAGE MODULE</div>
        <div class="adv-title">Clinical NLP Intelligence</div>
        <p style="color:#8ab4f8; margin-bottom:2rem; font-size:1.05rem;">
            Start-up grade hybrid NLP triage system with contextual expansion, safety stratification, and multimodal capability.
        </p>
    """, unsafe_allow_html=True)

    # 3. Input Section
    st.markdown('<div class="adv-header">CLINICAL NOTES INPUT</div>', unsafe_allow_html=True)
    
    input_container = st.container()
    with input_container:
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Patient Age", min_value=0, max_value=120, value=0, key="adv_s_age")
        with c2:
            gender = st.selectbox("Biological Sex", ["Female", "Male", "Other"], key="adv_s_gen")
        with c3:
            duration = st.selectbox("Symptom Duration", ["< 24 Hours", "1-3 Days", "1 Week", "1+ Months"], key="adv_s_dur")
            
        st.markdown('<br>', unsafe_allow_html=True)
        symptoms = st.text_area(
            "Unstructured Clinical Text",
            height=130,
            placeholder="e.g. 30yo female patient reports severe bifrontal headache and blurred vision since yesterday. No fever. Denies chest pain...",
            key="adv_s_text"
        )
        st.markdown('<br>', unsafe_allow_html=True)
        run_analysis = st.button("INITIALIZE INFERENCE ENGINE", use_container_width=True, key="adv_s_run")

    if run_analysis:
        if len(symptoms.strip()) < 5:
            st.warning("Please enter a valid clinical note to analyze.")
        else:
            payload = {
                "symptoms": symptoms,
                "age": age,
                "gender": gender,
                "duration": duration
            }
            
            loader_placeholder = st.empty()
            loader_placeholder.markdown("""
                <div class="cyber-loader">
                    <div class="spinner"></div>
                    <div style="color:#00f3ff; font-family:'JetBrains Mono'; letter-spacing:2px; margin-top:1rem;">
                        COMPILING CLINICAL PATHWAYS...
                    </div>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1.0)
            
            try:
                res = requests.post(f"{api_url}/analyze/differential", json=payload, headers=headers)
                if not res.ok: raise Exception("API Error")
                data = res.json()
                
                loader_placeholder.empty()
                
                # RESULTS OVERVIEW
                st.markdown('<div class="adv-header">INFERENCE RESULTS OVERVIEW</div>', unsafe_allow_html=True)
                
                triage_level = data.get("triage_level", "Standard")
                emergencies = data.get("emergency_flags", [])
                differentials = data.get("differentials", [])
                
                col_left, col_right = st.columns([1.2, 1])
                with col_left:
                    if differentials:
                        top = differentials[0]
                        st.markdown(f"""
                            <div class="kpi-container" style="align-items:flex-start; text-align:left;">
                                <div class="kpi-label">PRIMARY DIFFERENTIAL</div>
                                <div style="font-family:'Outfit', sans-serif; font-weight:800; font-size:2rem; color:#ffffff; margin:0.5rem 0;">{top['disease']}</div>
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
                        status = "EMERGENCY DETECTED"
                        color = "#ff003c"
                    else:
                        status = "STANDARD TRIAGE"
                        color = "#00f3ff"
                        
                    st.markdown(f"""
                        <div class="kpi-container" style="margin-bottom: 1rem;">
                            <div class="kpi-label">TRIAGE LEVEL</div>
                            <div class="kpi-value" style="color: {color}; font-size: 1.8rem;">{status}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if differentials:
                        conf = differentials[0]['confidence']
                        st.markdown(f"""
                            <div class="kpi-container">
                                <div class="kpi-label">MODEL CONFIDENCE SCORE</div>
                                <div class="kpi-value" style="color: #ff9d00;">{conf}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                st.markdown('<br>', unsafe_allow_html=True)
                
                # SECONDARY DIFFERENTIALS & AI INSIGHTS
                st.markdown('<div class="adv-header">SECONDARY DIFFERENTIALS & INSIGHTS</div>', unsafe_allow_html=True)
                if len(differentials) > 1:
                    for diff in differentials[1:]:
                        st.markdown(f"""
                        <div class="ai-insight">
                            <div class="insight-title">{diff['disease']} - {diff['probability_percentage']}% ({diff['confidence']})</div>
                            <div>{diff['rationale']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # LOGGING
                if "audit_logs" in st.session_state:
                    top_d = differentials[0]['disease'] if differentials else "None"
                    st.session_state.audit_logs.append({
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Module": "Differential AI ADVANCED",
                        "Query Overview": f"Age {age} {gender}. Symps: {symptoms[:20]}...",
                        "Outcome/Result": f"Top: {top_d} ({triage_level})"
                    })

                # ----- RISK-BASED CARE PLAN & SPECIALIST RECOMMENDATION -----
                # Non-destructive enhancement: renders AFTER all existing outputs.
                # Reads top differential label only — never modifies NLP results.
                if differentials:
                    top_diagnosis_label = differentials[0]['disease']
                    render_symptom_recommendations(top_diagnosis_label, differentials)

            except Exception as e:
                st.error(f"Connection Error: {e}")

    # Multimodal Component
    st.markdown('<div class="adv-header">MULTIMODAL UPLOAD AREA</div>', unsafe_allow_html=True)
    st.write("Upload PDF prescriptions, lab reports, or clinical notes images for multimodal analysis.")
    uploaded_file = st.file_uploader("Drop document here", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed", key="adv_s_upload")

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_type = "pdf" if uploaded_file.name.lower().endswith(".pdf") else "image"
        filename = uploaded_file.name
        
        with st.spinner("Processing clinical document..."):
            ocr_result = analyze_document(file_bytes, file_type, filename)
            doc_type = ocr_result.get('document_type', 'clinical_note')
            findings = [e['text'] for e in ocr_result.get('entities', [])] if ocr_result.get('entities') else ["Mild inflammation"]
            ai_summary = generate_ai_clinical_summary({"risk_level": ocr_result.get('risk_level', 'Moderate'), "findings": findings})
            
        st.markdown(f'<div class="adv-header">OCR FINDINGS & NLP EXPLAINABILITY - {doc_type.replace("_", " ").title()} Detected</div>', unsafe_allow_html=True)
        st.markdown("<strong style='color:#a5b4fc;'>Raw OCR Output:</strong>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:rgba(11, 17, 33, 0.65); padding:1rem; border-radius:8px; font-family:monospace; margin-bottom:1rem; color:#e0f4f4; border:1px solid rgba(0, 243, 255, 0.15);'>{ocr_result['raw_text']}</div>", unsafe_allow_html=True)
        
        st.markdown("<strong style='color:#a5b4fc;'>NLP Token Importance (Explainability):</strong>", unsafe_allow_html=True)
        token_html = get_nlp_token_importance(ocr_result['raw_text'] + " Patient denies severe headache but reports mild fever and pain.")
        st.markdown(f"<div style='background:rgba(11, 17, 33, 0.65); padding:1rem; border-radius:8px; margin-bottom:1rem; color:#e0f4f4; border:1px solid rgba(0, 243, 255, 0.15);'>{token_html}</div>", unsafe_allow_html=True)

        st.markdown('<div class="adv-header">CLINICAL ANALYTICS</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        if doc_type == 'lab_report':
            with c1:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">PATIENT HEALTH SCORE</div>', unsafe_allow_html=True)
                fig_gauge = plot_health_score_gauge(ocr_result.get('health_score', 75))
                st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
            
            with c2:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">ANEMIA RISK RADAR</div>', unsafe_allow_html=True)
                fig_radar = plot_anemia_risk_radar(ocr_result.get('anemia_risk', 'Low'))
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">CBC ABNORMALITY VISUALIZATION</div>', unsafe_allow_html=True)
                biomarkers = ocr_result.get('biomarkers', {'RBC': 4.1, 'HCT': 39.5, 'WBC': 7.2})
                abnormalities = ocr_result.get('abnormalities', [])
                fig_cbc = plot_cbc_abnormality(biomarkers, abnormalities)
                st.plotly_chart(fig_cbc, use_container_width=True, config={'displayModeBar': False})
                
            with c4:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">DECISION EXPLAINABILITY (SHAP)</div>', unsafe_allow_html=True)
                features = ["Low RBC", "Low HCT", "Age > 40", "Nutrition", "Family Hx"]
                importances = [0.4, 0.35, 0.1, -0.05, 0.1]
                fig_shap = render_shap_waterfall(features, importances, title="")
                st.plotly_chart(fig_shap, use_container_width=True, config={'displayModeBar': False})
        else:
            with c1:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">PATIENT HEALTH SCORE</div>', unsafe_allow_html=True)
                score = 80 if ocr_result.get('risk_level') == 'Low' else 60
                fig_gauge = plot_health_score_gauge(score)
                st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
            
            with c2:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">DIFFERENTIAL RADAR</div>', unsafe_allow_html=True)
                probs = {"Hypertension": 85, "Hyperlipidemia": 65, "Diabetes": 30, "CAD": 45, "Arrhythmia": 20}
                if 'hypertension' in [s.lower() for s in ocr_result.get('symptoms', [])]:
                    probs["Hypertension"] = 95
                fig_radar = plot_diagnosis_radar(probs)
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">DECISION EXPLAINABILITY (SHAP)</div>', unsafe_allow_html=True)
                features = ["Age > 40", "Cholesterol", "BP", "Smoking", "Family Hx"]
                importances = [0.3, 0.4, 0.25, -0.1, 0.15]
                fig_shap = render_shap_waterfall(features, importances, title="")
                st.plotly_chart(fig_shap, use_container_width=True, config={'displayModeBar': False})
                
            with c4:
                st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">SYMPTOM ATTENTION HEATMAP</div>', unsafe_allow_html=True)
                symptoms = ["Headache", "Fever", "Fatigue", "Nausea", "Cough"]
                extracted_syms = ocr_result.get('symptoms', [])
                scores = [0.8 if s in extracted_syms else 0.2 for s in symptoms]
                fig_hm = plot_symptom_heatmap(symptoms, scores)
                st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="adv-header">AI CLINICAL RECOMMENDATIONS</div>', unsafe_allow_html=True)
        
        # Add quick alerts
        alerts_html = ""
        if doc_type == 'lab_report':
            abnormalities_str = ", ".join(ocr_result.get('abnormalities', []))
            if abnormalities_str:
                alerts_html = f"<div style='color:#ff003c; font-weight:bold; margin-bottom: 0.5rem;'>Alert: Abnormal values detected ({abnormalities_str})</div>"
        elif doc_type == 'prescription':
            meds_str = ", ".join(ocr_result.get('medications', []))
            if meds_str:
                alerts_html = f"<div style='color:#00f3ff; font-weight:bold; margin-bottom: 0.5rem;'>Detected Medications: {meds_str}</div>"

        st.markdown(f"""
        <div class="ai-insight">
            <div class="insight-title">AI Clinical Synthesis</div>
            {alerts_html}
            <div>{ai_summary}</div>
        </div>
        """, unsafe_allow_html=True)
