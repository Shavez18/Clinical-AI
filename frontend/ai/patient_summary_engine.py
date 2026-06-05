"""
Patient Summary Engine.
Compiles user diagnostics into a structured clinical profile and generates downloadable HTML summaries.
"""
import streamlit as st
import datetime

def generate_patient_profile() -> dict:
    """
    Scans the active session state and logs to compile the current patient clinical profile.
    """
    profile = {
        "username": st.session_state.get("username", "Guest"),
        "role": st.session_state.get("role", "patient"),
        "age": st.session_state.get("adv_age") or st.session_state.get("adv_h_age") or st.session_state.get("adv_s_age") or 30,
        "gender": st.session_state.get("adv_s_gen") or ("Male" if st.session_state.get("adv_h_sex") == 1 else "Female"),
        "bmi": st.session_state.get("adv_bmi") or 0.0,
        "glucose": st.session_state.get("adv_gluc") or 0.0,
        "bp": f"{st.session_state.get('adv_h_trestbps') or st.session_state.get('adv_bp') or 120}/{st.session_state.get('adv_bp') or 80}",
        "cholesterol": st.session_state.get("adv_h_chol") or 0.0,
        "diabetes_risk": "Not Assessed",
        "cardio_risk": "Not Assessed",
        "nlp_diagnosis": "No current symptoms checked",
        "drug_interactions": "None analyzed",
        "recommendations": []
    }
    
    # Scan audit logs for latest results
    logs = st.session_state.get("audit_logs", [])
    for log in reversed(logs):
        if not isinstance(log, dict):
            continue
        module = log.get("Module", "")
        outcome = log.get("Outcome/Result", "")
        
        if "Diabetes" in module and profile["diabetes_risk"] == "Not Assessed":
            profile["diabetes_risk"] = outcome
        elif ("Heart" in module or "Cardiac" in module) and profile["cardio_risk"] == "Not Assessed":
            profile["cardio_risk"] = outcome
        elif "Differential" in module and profile["nlp_diagnosis"] == "No current symptoms checked":
            profile["nlp_diagnosis"] = log.get("Query Overview", "") + " -> " + outcome
        elif "Drug" in module and profile["drug_interactions"] == "None analyzed":
            profile["drug_interactions"] = log.get("Query Overview", "") + " -> " + outcome

    # Generate personalized recommendations
    if profile["bmi"] >= 30:
        profile["recommendations"].append("Weight management protocol advised due to Obese BMI score.")
    if profile["glucose"] >= 100:
        profile["recommendations"].append("Schedule fasting blood glucose or HbA1c screening to check prediabetic indicators.")
    if profile["cholesterol"] >= 200:
        profile["recommendations"].append("Incorporate dietary adjustments (low saturated fat) to address borderline or high lipid panel.")
        
    if not profile["recommendations"]:
        profile["recommendations"].append("Continue standard preventive maintenance checks annually.")
        
    return profile

def compile_clinical_summary_html(profile: dict) -> str:
    """
    Compiles the clinical profile into a beautiful, printable HTML document.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recs_list = "".join([f"<li>{r}</li>" for r in profile["recommendations"]])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>ClinicalAI | Patient Summary Report</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2d3748;
                background-color: #f7fafc;
                margin: 0;
                padding: 40px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.1);
                border-top: 6px solid #0d8c8c;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .title {{
                font-size: 24px;
                font-weight: 700;
                color: #0d8c8c;
            }}
            .timestamp {{
                font-size: 12px;
                color: #a0aec0;
                font-family: monospace;
            }}
            .section {{
                margin-bottom: 30px;
            }}
            .section-title {{
                font-size: 16px;
                font-weight: 700;
                color: #2b6cb0;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 15px;
                border-bottom: 1px solid #edf2f7;
                padding-bottom: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #edf2f7;
            }}
            th {{
                background-color: #f8fafc;
                font-weight: 600;
                color: #4a5568;
            }}
            .alert-box {{
                background-color: #ebf8ff;
                border-left: 4px solid #3182ce;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            .rec-list {{
                padding-left: 20px;
                line-height: 1.6;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                font-size: 11px;
                color: #a0aec0;
                border-top: 1px solid #e2e8f0;
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <div class="title">ClinicalAI Decision Support</div>
                    <div style="font-size: 14px; color: #4a5568;">Comprehensive Patient Summary Profile</div>
                </div>
                <div class="timestamp">Generated: {timestamp}</div>
            </div>
            
            <div class="section">
                <div class="section-title">Demographics & Telemetry</div>
                <table>
                    <tr>
                        <th>Parameter</th>
                        <th>Value</th>
                        <th>Parameter</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td><strong>User / Subject</strong></td>
                        <td>{profile['username']}</td>
                        <td><strong>Biological Profile</strong></td>
                        <td>{profile['age']} Yrs / {profile['gender']}</td>
                    </tr>
                    <tr>
                        <td><strong>BMI Metric</strong></td>
                        <td>{profile['bmi'] if profile['bmi'] > 0 else 'Not calculated'}</td>
                        <td><strong>Blood Glucose</strong></td>
                        <td>{f"{profile['glucose']} mg/dL" if profile['glucose'] > 0 else 'Not checked'}</td>
                    </tr>
                    <tr>
                        <td><strong>Blood Pressure</strong></td>
                        <td>{profile['bp']} mmHg</td>
                        <td><strong>Cholesterol (Serum)</strong></td>
                        <td>{f"{profile['cholesterol']} mg/dL" if profile['cholesterol'] > 0 else 'Not checked'}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">Clinical Risk Stratification</div>
                <table>
                    <tr>
                        <th style="width: 40%;">Telemetry Node</th>
                        <th style="width: 60%;">Stratification / Result</th>
                    </tr>
                    <tr>
                        <td><strong>Diabetes Predictive Risk</strong></td>
                        <td>{profile['diabetes_risk']}</td>
                    </tr>
                    <tr>
                        <td><strong>Cardiovascular Predictive Risk</strong></td>
                        <td>{profile['cardio_risk']}</td>
                    </tr>
                    <tr>
                        <td><strong>NLP Differential Screening</strong></td>
                        <td>{profile['nlp_diagnosis']}</td>
                    </tr>
                    <tr>
                        <td><strong>FDA Drug Interaction Screening</strong></td>
                        <td>{profile['drug_interactions']}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">Clinical Synthesis & Interventions</div>
                <div class="alert-box">
                    <strong>Medical Action Guidelines:</strong>
                    <ul class="rec-list">
                        {recs_list}
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                This patient summary report is an automated synthesis compiled by ClinicalAI Enterprise Decision Support protocol.<br/>
                All model evaluations must be validated by a licensed physician before clinical application.
            </div>
        </div>
    </body>
    </html>
    """
    return html

def render_summary_interface():
    """
    Renders an on-screen preview of the patient summary in the chatbot window,
    along with a download button.
    """
    profile = generate_patient_profile()
    html_content = compile_clinical_summary_html(profile)
    
    st.markdown("### 📋 Clinical Summary Preview")
    
    st.markdown(f"""
    **Demographics:** {profile['username']} ({profile['age']} Yrs, {profile['gender']})  
    **BMI:** {profile['bmi'] if profile['bmi'] > 0 else 'N/A'} | **Glucose:** {profile['glucose'] if profile['glucose'] > 0 else 'N/A'} mg/dL  
    **Diabetes Risk:** {profile['diabetes_risk']}  
    **Cardiac Risk:** {profile['cardio_risk']}  
    """, unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 Download Clinical Summary Report",
        data=html_content,
        file_name=f"clinical_summary_{profile['username']}.html",
        mime="text/html",
        key="summary_download_btn"
    )
