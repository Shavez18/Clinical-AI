def generate_heart_insights(features, risk_score):
    """
    Generates dynamic AI clinical insights and actionable recommendations
    based on the predicted cardiovascular risk score and underlying features.
    """
    insights = []
    
    age = features.get('age', 0)
    trestbps = features.get('trestbps', 0)
    chol = features.get('chol', 0)
    cp = features.get('cp', 0)
    fbs = features.get('fbs', 0)
    
    # High Risk Core Insights
    if risk_score >= 70:
        insights.append({
            "title": "🚨 ACUTE CARDIOVASCULAR RISK",
            "desc": "High probability of coronary artery disease detected. Immediate cardiology consultation, stress testing, and angiogram evaluation are strongly advised."
        })
    elif risk_score >= 30:
        insights.append({
            "title": "⚠️ ELEVATED VASCULAR THREAT",
            "desc": "Moderate risk profile indicates potential atherosclerosis or structural abnormalities. Recommend lifestyle modification and comprehensive lipid panel."
        })
    else:
        insights.append({
            "title": "✅ CARDIAC STABILITY",
            "desc": "Current vitals indicate low cardiovascular risk. Maintain baseline monitoring, aerobic exercise, and current dietary regimens."
        })
        
    # Feature-specific Insights
    if trestbps > 140:
        insights.append({
            "title": "🫀 HYPERTENSION PROTOCOL",
            "desc": f"Resting blood pressure of {trestbps} mmHg exceeds stage 2 hypertension thresholds. Investigate anti-hypertensive pharmacotherapy."
        })
    elif 120 <= trestbps <= 140:
        insights.append({
            "title": "🫀 PRE-HYPERTENSION",
            "desc": "Blood pressure levels suggest elevated vascular resistance. Consider DASH diet and sodium restriction."
        })
        
    if chol >= 240:
        insights.append({
            "title": "🩸 HYPERLIPIDEMIA RISK",
            "desc": f"Serum cholesterol of {chol} mg/dL is dangerously high. Initiate statin therapy evaluation and strict dietary lipid management."
        })
        
    if cp > 0:
        insights.append({
            "title": "⚡ ISCHEMIC PAIN MARKERS",
            "desc": "Presence of non-typical or typical angina requires ruling out acute coronary syndrome via serial ECGs and troponin assays."
        })
        
    if fbs == 1:
        insights.append({
            "title": "🩺 METABOLIC COMORBIDITY",
            "desc": "Fasting blood sugar > 120 mg/dL detected. Assess for concurrent metabolic syndrome, which exponentially increases coronary risk."
        })
        
    # Ensure we return a good amount of insights for the UI
    if len(insights) < 4:
        insights.append({
            "title": "🧬 LONG-TERM CARDIAC HEALTH",
            "desc": "Continue routine preventive cardiology screenings. Maintain minimum 150 minutes of moderate aerobic activity weekly."
        })
        
    return insights
