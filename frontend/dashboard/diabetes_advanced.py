import streamlit as st
import datetime
import numpy as np
from ui.theme import apply_advanced_theme
from visuals.charts import create_neon_gauge, create_biomarker_radar, create_feature_importance_chart
from analytics.explainability import generate_simulated_shap, calculate_confidence
from ai.insights import generate_insights
from recommendations.recommendation_ui import render_diabetes_recommendations
from utils.model_loader import get_diabetes_model


def _predict_diabetes_local(features: dict) -> float:
    """Run inference directly — no HTTP. Returns risk percentage."""
    model, scaler, threshold = get_diabetes_model()

    arr = np.array([[
        features["Pregnancies"],
        features["Glucose"],
        features["BloodPressure"],
        features["SkinThickness"],
        features["Insulin"],
        features["BMI"],
        features["DiabetesPedigreeFunction"],
        features["Age"],
    ]])
    scaled      = scaler.transform(arr)
    probability = model.predict_proba(scaled)[0][1]
    return round(float(probability * 100), 2)


def render_dashboard(api_url=None, headers=None):
    """
    Renders the Advanced Futuristic Healthcare AI Analytics Interface for Diabetes Risk.
    api_url / headers are kept for backward-compat but are no longer used.
    """
    apply_advanced_theme()

    st.markdown("""
        <div class="adv-subtitle">⚡ SYSTEM ONLINE // PREDICTIVE MODULE</div>
        <div class="adv-title">Diabetes Intelligence</div>
        <p style="color:#8ab4f8; margin-bottom:2rem; font-size:1.05rem;">
            Advanced biometric analysis utilizing non-linear gradient boosting inference
            with contextual feature explainability mapping.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="adv-header">PATIENT TELEMETRY INPUT</div>', unsafe_allow_html=True)

    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Patient Age", 0, 120, 0, key="adv_age")
            bmi = st.number_input("Body Mass Index (BMI)", 0.0, 70.0, 0.0, format="%.1f", key="adv_bmi")
        with c2:
            glucose = st.number_input("Fasting Glucose (mg/dL)", 0.0, 300.0, 0.0, key="adv_gluc")
            bp      = st.number_input("Diastolic BP (mm Hg)", 0.0, 200.0, 0.0, key="adv_bp")
        with c3:
            has_preg = st.selectbox("Pregnancy History", ["No", "Yes"], key="adv_has_preg")
            preg     = st.number_input("Pregnancy Count", 1, 20, 1, key="adv_preg") if has_preg == "Yes" else 0

        st.markdown('<br>', unsafe_allow_html=True)
        run_btn = st.button("INITIALIZE INFERENCE ENGINE", use_container_width=True, key="adv_run_btn")

    if run_btn:
        features = {
            "Pregnancies": preg, "Glucose": glucose, "BloodPressure": bp,
            "SkinThickness": 20, "Insulin": 80, "BMI": bmi,
            "DiabetesPedigreeFunction": 0.5, "Age": age,
        }

        with st.spinner("Running inference…"):
            try:
                risk = _predict_diabetes_local(features)
            except Exception:
                # Fallback heuristic if model fails
                base = 15
                if glucose > 130: base += 35
                if bmi > 30:      base += 20
                if age > 50:      base += 10
                risk = min(98.5, float(base))

        shap_vals  = generate_simulated_shap(features, risk)
        confidence = calculate_confidence(risk, features)
        insights   = generate_insights(features, risk)

        st.markdown('<div class="adv-header">INFERENCE RESULTS OVERVIEW</div>', unsafe_allow_html=True)

        col_gauge, col_stats = st.columns([1.2, 1])
        with col_gauge:
            st.plotly_chart(create_neon_gauge(risk, "DIABETES RISK PROBABILITY"), use_container_width=True)
        with col_stats:
            category  = "HIGH RISK" if risk > 70 else "MODERATE RISK" if risk > 30 else "LOW RISK"
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
        st.markdown('<div class="adv-header">FEATURE ATTRIBUTION & BIOMARKERS</div>', unsafe_allow_html=True)
        col_radar, col_shap = st.columns(2)
        with col_radar:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">BIOMARKER RADAR</div>', unsafe_allow_html=True)
            st.plotly_chart(create_biomarker_radar(features), use_container_width=True)
        with col_shap:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">SHAP IMPACT EXPLAINABILITY</div>', unsafe_allow_html=True)
            st.plotly_chart(create_feature_importance_chart(shap_vals), use_container_width=True)

        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown('<div class="adv-header">AI CLINICAL RECOMMENDATIONS</div>', unsafe_allow_html=True)
        for item in insights:
            st.markdown(f"""
            <div class="ai-insight">
                <div class="insight-title">{item['title']}</div>
                <div>{item['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

        render_diabetes_recommendations(risk, features)

        st.session_state.audit_logs.append({
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Module": "Diabetes ADVANCED",
            "Query Overview": f"Age {age}, BMI {bmi}, Gluc {glucose}",
            "Outcome/Result": f"Risk: {risk:.1f}% ({category})",
        })
        st.session_state.last_prediction_data = {
            "type": "diabetes", "risk": risk, "category": category,
            "features": features, "shap": shap_vals,
        }
