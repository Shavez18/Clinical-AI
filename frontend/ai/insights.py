def generate_insights(features, risk_score):
    """
    Generates dynamic AI clinical insights and actionable recommendations
    based on the predicted risk score and underlying biometric features.
    """
    insights = []
    
    gluc = features.get('Glucose', 0)
    bmi = features.get('BMI', 0)
    bp = features.get('BloodPressure', 0)
    
    # High Risk Core Insights
    if risk_score >= 70:
        insights.append({
            "title": "🚨 CLINICAL ALERT",
            "desc": "High probability of Type 2 Diabetes detected. Immediate endocrinology consultation and HbA1c testing is strongly advised."
        })
    elif risk_score >= 30:
        insights.append({
            "title": "⚠️ PRE-DIABETIC PROTOCOL",
            "desc": "Moderate risk profile indicates potential insulin resistance. Implement lifestyle interventions and schedule follow-up fasting glucose test."
        })
    else:
        insights.append({
            "title": "✅ METABOLIC STABILITY",
            "desc": "Current biometrics indicate low risk. Maintain baseline monitoring and current lifestyle regimens."
        })
        
    # Feature-specific Insights
    if gluc > 125:
        insights.append({
            "title": "🩸 GLYCEMIC DYSREGULATION",
            "desc": f"Fasting glucose of {gluc} mg/dL exceeds clinical threshold (125 mg/dL). Investigate pancreatic beta-cell function."
        })
    elif 100 <= gluc <= 125:
        insights.append({
            "title": "🩸 IMPAIRED FASTING GLUCOSE",
            "desc": "Glucose levels suggest impaired tolerance. Consider continuous glucose monitoring (CGM) for postprandial analysis."
        })
        
    if bmi >= 30:
        insights.append({
            "title": "⚖️ ADIPOSITY RISK FACTOR",
            "desc": f"BMI of {bmi:.1f} falls in the obese category, significantly amplifying insulin resistance probability."
        })
        
    if bp > 90:
        insights.append({
            "title": "🫀 VASCULAR COMORBIDITY",
            "desc": "Elevated diastolic pressure noted. Assess cardiovascular risk overlap; microvascular complications often parallel metabolic syndrome."
        })
        
    # Ensure we return a good amount of insights for the UI, pad if necessary
    if len(insights) < 3:
        insights.append({
            "title": "🧬 PREVENTIVE ONCOLOGY/METABOLISM",
            "desc": "Regular annual screening recommended to maintain optimal metabolic baselines."
        })
        
    return insights
