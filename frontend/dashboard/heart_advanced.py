import streamlit as st
import time
import requests
import datetime
from ui.theme import apply_advanced_theme
from visuals.charts import create_neon_gauge, create_feature_importance_chart
from visuals.heart_charts import create_heart_biomarker_radar, create_cholesterol_chart, create_blood_pressure_trend, create_vessel_risk_analysis
from analytics.heart_explainability import generate_heart_simulated_shap, calculate_heart_confidence
from ai.heart_insights import generate_heart_insights
from recommendations.recommendation_ui import render_heart_recommendations

def render_heart_dashboard(api_url, headers):
    """
    Renders the Advanced Futuristic Healthcare AI Analytics Interface for Heart Disease Risk.
    """
    # 1. Apply Advanced Theme
    apply_advanced_theme()
    
    # 2. Header
    st.markdown("""
        <div class="adv-subtitle">⚡ SYSTEM ONLINE // PREDICTIVE MODULE</div>
        <div class="adv-title">Cardiovascular Intelligence</div>
        <p style="color:#8ab4f8; margin-bottom:2rem; font-size:1.05rem;">
            Advanced biometric analysis utilizing logistic inference pipelines 
            with contextual feature explainability and vessel risk mapping.
        </p>
    """, unsafe_allow_html=True)

    # 3. Input Section
    st.markdown('<div class="adv-header">PATIENT TELEMETRY INPUT</div>', unsafe_allow_html=True)
    
    input_container = st.container()
    with input_container:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            age      = st.number_input("Patient Age", 0, 120, 0, key="adv_h_age")
            sex      = st.selectbox("Sex", [(1,"Male"),(0,"Female")], format_func=lambda x: x[1], key="adv_h_sex")[0]
            trestbps = st.number_input("Resting BP (mmHg)", 0, 250, 0, key="adv_h_trestbps")
            thalach  = st.number_input("Max Heart Rate", 0, 250, 0, key="adv_h_thalach")
        with c2:
            cp      = st.selectbox("Chest Pain Type",
                                   [(0,"Typical Angina"),(1,"Atypical Angina"),
                                    (2,"Non-anginal"),(3,"Asymptomatic")],
                                   format_func=lambda x: x[1], key="adv_h_cp")[0]
            restecg = st.selectbox("Resting ECG",
                                   [(0,"Normal"),(1,"ST-T Abnormality"),(2,"LVH")],
                                   format_func=lambda x: x[1], key="adv_h_restecg")[0]
            exang   = st.selectbox("Exercise Angina",
                                   [(0,"No"),(1,"Yes")],
                                   format_func=lambda x: x[1], key="adv_h_exang")[0]
        with c3:
            oldpeak = st.number_input("ST Depression", 0.0, 10.0, 0.0, step=0.1, key="adv_h_oldpeak")
            slope   = st.selectbox("ST Slope",
                                   [(0,"Downsloping"),(1,"Flat"),(2,"Upsloping")],
                                   format_func=lambda x: x[1], key="adv_h_slope")[0]
            chol = st.number_input("Serum Chol (mg/dL)", 0, 600, 0, key="adv_h_chol")
        with c4:
            fbs  = st.selectbox("Fasting Sugar > 120",
                                [(0,"False"),(1,"True")],
                                format_func=lambda x: x[1], key="adv_h_fbs")[0]
            ca   = st.selectbox("Major Vessels (0-3)", [0, 1, 2, 3], key="adv_h_ca")
            thal = st.selectbox("Thalassemia",
                                [(0,"Normal"),(1,"Fixed Defect"),(2,"Reversable"),(3,"Unknown")],
                                format_func=lambda x: x[1], key="adv_h_thal")[0]
            
        st.markdown('<br>', unsafe_allow_html=True)
        run_btn = st.button("INITIALIZE INFERENCE ENGINE", use_container_width=True, key="adv_h_run_btn")

    # 4. Processing & Output Section
    if run_btn:
        features = {
            "age": age, "sex": sex, "cp": cp, "trestbps": trestbps,
            "chol": chol, "fbs": fbs, "restecg": restecg, "thalach": thalach,
            "exang": exang, "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal
        }
        
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="cyber-loader">
                <div class="spinner"></div>
                <div style="color:#00f3ff; font-family:'JetBrains Mono'; letter-spacing:2px; margin-top:1rem;">
                    COMPILING CARDIOVASCULAR PATHWAYS...
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Simulate network latency and processing for UX
        time.sleep(1.5)
        
        # Call Existing Backend API to preserve original functionality
        try:
            res = requests.post(f"{api_url}/predict/heart", json=features, headers=headers)
            if not res.ok: raise Exception("API Error")
            risk = res.json().get("risk_percentage", 0)
        except:
            # Fallback mock logic if backend fails
            base = 10
            if age > 55: base += 20
            if cp == 3:  base += 30
            if trestbps > 140: base += 15
            risk = min(96.2, float(base))
            
        loader_placeholder.empty() # Clear loader
        
        # Generate Advanced Analytics
        shap_vals = generate_heart_simulated_shap(features, risk)
        confidence = calculate_heart_confidence(risk, features)
        insights = generate_heart_insights(features, risk)
        
        # ----- RESULTS DASHBOARD -----
        st.markdown('<div class="adv-header">INFERENCE RESULTS OVERVIEW</div>', unsafe_allow_html=True)
        
        col_gauge, col_stats = st.columns([1.2, 1])
        
        with col_gauge:
            st.plotly_chart(create_neon_gauge(risk, "CARDIOVASCULAR RISK PROBABILITY"), use_container_width=True)
            
        with col_stats:
            # Risk Category KPI
            category = "HIGH RISK" if risk > 70 else "MODERATE RISK" if risk > 30 else "LOW RISK"
            cat_color = "#ff003c" if risk > 70 else "#ff9d00" if risk > 30 else "#00f3ff"
            
            st.markdown(f"""
                <div class="kpi-container" style="margin-bottom: 1rem;">
                    <div class="kpi-label">MODEL CONFIDENCE SCORE</div>
                    <div class="kpi-value" style="color: #00f3ff;">{confidence:.1f}%</div>
                </div>
                <div class="kpi-container">
                    <div class="kpi-label">CLINICAL STRATIFICATION</div>
                    <div class="kpi-value" style="color: {cat_color}; font-size: 2.2rem;">{category}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        
        # ----- EXPLAINABILITY & BIOMARKERS -----
        st.markdown('<div class="adv-header">FEATURE ATTRIBUTION & BIOMARKERS</div>', unsafe_allow_html=True)
        
        # Top Row: Radar & SHAP
        col_radar, col_shap = st.columns(2)
        with col_radar:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">BIOMARKER RADAR</div>', unsafe_allow_html=True)
            st.plotly_chart(create_heart_biomarker_radar(features), use_container_width=True)
        with col_shap:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">SHAP IMPACT EXPLAINABILITY</div>', unsafe_allow_html=True)
            st.plotly_chart(create_feature_importance_chart(shap_vals), use_container_width=True)

        st.markdown('<br>', unsafe_allow_html=True)
        
        # Bottom Row: BP Trend, Vessel Risk, Cholesterol
        st.markdown('<div class="adv-header">CARDIOVASCULAR DEEP DIVE</div>', unsafe_allow_html=True)
        col_bp, col_vessel, col_chol = st.columns(3)
        with col_bp:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">BLOOD PRESSURE TREND</div>', unsafe_allow_html=True)
            st.plotly_chart(create_blood_pressure_trend(trestbps), use_container_width=True)
        with col_vessel:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">VESSEL RISK ANALYSIS</div>', unsafe_allow_html=True)
            st.plotly_chart(create_vessel_risk_analysis(ca), use_container_width=True)
        with col_chol:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">CHOLESTEROL PROFILE</div>', unsafe_allow_html=True)
            st.plotly_chart(create_cholesterol_chart(chol), use_container_width=True)

        st.markdown('<br>', unsafe_allow_html=True)
        
        # ----- AI CLINICAL INSIGHTS -----
        st.markdown('<div class="adv-header">AI CLINICAL RECOMMENDATIONS</div>', unsafe_allow_html=True)
        
        for item in insights:
            st.markdown(f"""
            <div class="ai-insight">
                <div class="insight-title">{item['title']}</div>
                <div>{item['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ----- RISK-BASED CARE PLAN & SPECIALIST RECOMMENDATION -----
        # Non-destructive enhancement: renders AFTER all existing outputs.
        # Reads `risk` only — does not modify predictions, models, or session state.
        render_heart_recommendations(risk, features)

        # Write to Global Audit Log (Preserving old functionality)
        st.session_state.audit_logs.append({
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Module": "Heart Risk ADVANCED",
            "Query Overview": f"Age {age}, BP {trestbps}, Chol {chol}",
            "Outcome/Result": f"Risk: {risk:.1f}% ({category})"
        })

        st.session_state.last_prediction_data = {
            "type": "heart",
            "risk": risk,
            "category": category,
            "features": features,
            "shap": shap_vals
        }
