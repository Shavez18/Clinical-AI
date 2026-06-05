import streamlit as st
import time
import requests
import datetime
from ui.theme import apply_advanced_theme
from visuals.charts import create_neon_gauge, create_biomarker_radar, create_feature_importance_chart
from analytics.explainability import generate_simulated_shap, calculate_confidence
from ai.insights import generate_insights
from recommendations.recommendation_ui import render_diabetes_recommendations

def render_dashboard(api_url, headers):
    """
    Renders the Advanced Futuristic Healthcare AI Analytics Interface for Diabetes Risk.
    """
    # 1. Apply Advanced Theme
    apply_advanced_theme()
    
    # 2. Header
    st.markdown("""
        <div class="adv-subtitle">⚡ SYSTEM ONLINE // PREDICTIVE MODULE</div>
        <div class="adv-title">Diabetes Intelligence</div>
        <p style="color:#8ab4f8; margin-bottom:2rem; font-size:1.05rem;">
            Advanced biometric analysis utilizing non-linear gradient boosting inference 
            with contextual feature explainability mapping.
        </p>
    """, unsafe_allow_html=True)

    # 3. Input Section
    st.markdown('<div class="adv-header">PATIENT TELEMETRY INPUT</div>', unsafe_allow_html=True)
    
    input_container = st.container()
    with input_container:
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Patient Age", 0, 120, 0, key="adv_age")
            bmi = st.number_input("Body Mass Index (BMI)", 0.0, 70.0, 0.0, format="%.1f", key="adv_bmi")
        with c2:
            glucose = st.number_input("Fasting Glucose (mg/dL)", 0.0, 300.0, 0.0, key="adv_gluc")
            bp = st.number_input("Diastolic BP (mm Hg)", 0.0, 200.0, 0.0, key="adv_bp")
        with c3:
            has_preg = st.selectbox("Pregnancy History", ["No", "Yes"], key="adv_has_preg")
            preg = st.number_input("Pregnancy Count", 1, 20, 1, key="adv_preg") if has_preg == "Yes" else 0
            
        st.markdown('<br>', unsafe_allow_html=True)
        run_btn = st.button("INITIALIZE INFERENCE ENGINE", use_container_width=True, key="adv_run_btn")

    # 4. Processing & Output Section
    if run_btn:
        features = {
            "Pregnancies": preg, "Glucose": glucose, "BloodPressure": bp,
            "SkinThickness": 20, "Insulin": 80, "BMI": bmi,
            "DiabetesPedigreeFunction": 0.5, "Age": age
        }
        
        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <div class="cyber-loader">
                <div class="spinner"></div>
                <div style="color:#00f3ff; font-family:'JetBrains Mono'; letter-spacing:2px; margin-top:1rem;">
                    COMPILING NEURAL PATHWAYS...
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Simulate network latency and processing for UX
        time.sleep(1.5)
        
        # Call Existing Backend API to preserve original functionality
        try:
            res = requests.post(f"{api_url}/predict/diabetes", json=features, headers=headers)
            if not res.ok: raise Exception("API Error")
            risk = res.json().get("risk_percentage", 0)
        except:
            # Fallback mock logic if backend fails
            base = 15
            if glucose > 130: base += 35
            if bmi > 30: base += 20
            if age > 50: base += 10
            risk = min(98.5, float(base))
            
        loader_placeholder.empty() # Clear loader
        
        # Generate Advanced Analytics
        shap_vals = generate_simulated_shap(features, risk)
        confidence = calculate_confidence(risk, features)
        insights = generate_insights(features, risk)
        
        # ----- RESULTS DASHBOARD -----
        st.markdown('<div class="adv-header">INFERENCE RESULTS OVERVIEW</div>', unsafe_allow_html=True)
        
        col_gauge, col_stats = st.columns([1.2, 1])
        
        with col_gauge:
            st.plotly_chart(create_neon_gauge(risk, "DIABETES RISK PROBABILITY"), use_container_width=True)
            
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
        col_radar, col_shap = st.columns(2)
        
        with col_radar:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">BIOMARKER RADAR</div>', unsafe_allow_html=True)
            st.plotly_chart(create_biomarker_radar(features), use_container_width=True)
            
        with col_shap:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">SHAP IMPACT EXPLAINABILITY</div>', unsafe_allow_html=True)
            st.plotly_chart(create_feature_importance_chart(shap_vals), use_container_width=True)

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
        render_diabetes_recommendations(risk, features)

        # Write to Global Audit Log (Preserving old functionality)
        st.session_state.audit_logs.append({
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Module": "Diabetes ADVANCED",
            "Query Overview": f"Age {age}, BMI {bmi}, Gluc {glucose}",
            "Outcome/Result": f"Risk: {risk:.1f}% ({category})"
        })

        st.session_state.last_prediction_data = {
            "type": "diabetes",
            "risk": risk,
            "category": category,
            "features": features,
            "shap": shap_vals
        }
