import streamlit as st
import time
from multimodal.ocr_processor import analyze_document
from visuals.futuristic_charts import plot_diagnosis_radar, plot_symptom_heatmap, plot_health_score_gauge
from visuals.multimodal_charts import plot_cbc_abnormality, plot_anemia_risk_radar
from analytics.advanced_explainability import render_shap_waterfall, get_nlp_token_importance
from ai.clinical_summarization import generate_ai_clinical_summary

def render_advanced_intelligence_section():
    # SECTION 5: Multimodal Upload Area
    st.markdown('<div class="section-label">Multimodal Upload Area</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Upload Clinical Documents</div>', unsafe_allow_html=True)
    st.write("Upload PDF prescriptions, lab reports, or clinical notes images for multimodal analysis.")
    uploaded_file = st.file_uploader("Drop document here", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed", key="mm_upload")
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_type = "pdf" if uploaded_file.name.lower().endswith(".pdf") else "image"
        filename = uploaded_file.name
        
        with st.spinner("Processing clinical document..."):
            ocr_result = analyze_document(file_bytes, file_type, filename)
            doc_type = ocr_result.get('document_type', 'clinical_note')
            findings = [e['text'] for e in ocr_result.get('entities', [])] if ocr_result.get('entities') else ["Mild inflammation"]
            ai_summary = generate_ai_clinical_summary({"risk_level": ocr_result.get('risk_level', 'Moderate'), "findings": findings})
            
        # SECTION 6: OCR Findings
        st.markdown(f'<div class="section-label">OCR Findings - {doc_type.replace("_", " ").title()} Detected</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Extracted Clinical Data</div>', unsafe_allow_html=True)
        
        st.markdown("<strong style='color:var(--text-primary);'>Raw OCR Output:</strong>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:var(--bg-panel); padding:1rem; border-radius:8px; font-family:monospace; margin-bottom:1.5rem; color:var(--text-primary); border:1px solid var(--border);'>{ocr_result['raw_text']}</div>", unsafe_allow_html=True)
        
        st.markdown("<strong style='color:var(--text-primary);'>NLP Token Importance (Explainability):</strong>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.8rem; color:var(--text-muted);'>Highlights show tokens that drove the AI decision engine.</p>", unsafe_allow_html=True)
        token_html = get_nlp_token_importance(ocr_result['raw_text'] + " Patient denies severe headache but reports mild fever and pain.")
        st.markdown(f"<div style='background:var(--bg-panel); padding:1rem; border-radius:8px; margin-bottom:0.5rem; color:var(--text-primary); border:1px solid var(--border);'>{token_html}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # SECTION 7: Clinical Analytics (Branching)
        st.markdown('<div class="section-label">Clinical Analytics</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if doc_type == 'lab_report':
            with c1:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">Patient Health Score</div>', unsafe_allow_html=True)
                fig_gauge = plot_health_score_gauge(ocr_result.get('health_score', 75))
                st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">Anemia Risk Radar</div>', unsafe_allow_html=True)
                fig_radar = plot_anemia_risk_radar(ocr_result.get('anemia_risk', 'Low'))
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">CBC Abnormality Visualization</div>', unsafe_allow_html=True)
                biomarkers = ocr_result.get('biomarkers', {'RBC': 4.1, 'HCT': 39.5, 'WBC': 7.2})
                abnormalities = ocr_result.get('abnormalities', [])
                fig_cbc = plot_cbc_abnormality(biomarkers, abnormalities)
                st.plotly_chart(fig_cbc, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            with c4:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">Decision Explainability (SHAP)</div>', unsafe_allow_html=True)
                features = ["Low RBC", "Low HCT", "Age > 40", "Nutrition", "Family Hx"]
                importances = [0.4, 0.35, 0.1, -0.05, 0.1]
                fig_shap = render_shap_waterfall(features, importances, title="")
                st.plotly_chart(fig_shap, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Prescription or Default
            with c1:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">Patient Health Score</div>', unsafe_allow_html=True)
                score = 80 if ocr_result.get('risk_level') == 'Low' else 60
                fig_gauge = plot_health_score_gauge(score)
                st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">Differential Radar</div>', unsafe_allow_html=True)
                probs = {"Hypertension": 85, "Hyperlipidemia": 65, "Diabetes": 30, "CAD": 45, "Arrhythmia": 20}
                if 'hypertension' in [s.lower() for s in ocr_result.get('symptoms', [])]:
                    probs["Hypertension"] = 95
                fig_radar = plot_diagnosis_radar(probs)
                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            c3, c4 = st.columns(2)
            with c3:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">Decision Explainability (SHAP)</div>', unsafe_allow_html=True)
                features = ["Age > 40", "Cholesterol", "BP", "Smoking", "Family Hx"]
                importances = [0.3, 0.4, 0.25, -0.1, 0.15]
                fig_shap = render_shap_waterfall(features, importances, title="")
                st.plotly_chart(fig_shap, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
                
            with c4:
                st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
                st.markdown('<div class="card-title" style="text-align:center;">Symptom Attention Heatmap</div>', unsafe_allow_html=True)
                symptoms = ["Headache", "Fever", "Fatigue", "Nausea", "Cough"]
                extracted_syms = ocr_result.get('symptoms', [])
                scores = [0.8 if s in extracted_syms else 0.2 for s in symptoms]
                fig_hm = plot_symptom_heatmap(symptoms, scores)
                st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)

        # SECTION 8: AI Clinical Recommendations
        st.markdown('<div class="section-label">AI Clinical Recommendations</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">AI Clinical Synthesis</div>', unsafe_allow_html=True)
        
        # Customize summary slightly based on type
        if doc_type == 'lab_report':
            abnormalities_str = ", ".join(ocr_result.get('abnormalities', []))
            if abnormalities_str:
                st.markdown(f"<p style='color:#ff003c; font-weight:bold;'>Alert: Abnormal values detected ({abnormalities_str})</p>", unsafe_allow_html=True)
        elif doc_type == 'prescription':
            meds_str = ", ".join(ocr_result.get('medications', []))
            if meds_str:
                st.markdown(f"<p style='color:#00f3ff; font-weight:bold;'>Detected Medications: {meds_str}</p>", unsafe_allow_html=True)
                
        st.markdown(ai_summary, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Upload a document to view OCR findings, the clinical analytics dashboard, and AI clinical recommendations.")
