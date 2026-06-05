"""
Health Ranges Utility.
Defines clinical reference ranges for Fasting Glucose, Cholesterol, and Blood Pressure.
"""

def interpret_glucose(value: float) -> dict:
    """
    Interprets Fasting Glucose value (mg/dL).
    Ranges:
    - Normal: < 100 mg/dL
    - Prediabetes: 100-125 mg/dL
    - Diabetes: >= 126 mg/dL
    """
    if value <= 0:
        return {"category": "Invalid", "interpretation": "Please enter a valid glucose value.", "color": "#6b8aab"}
    
    if value < 70:
        return {
            "category": "Hypoglycemia",
            "interpretation": "Low blood sugar levels. May cause dizziness, sweating, confusion, and requires immediate glucose intake.",
            "color": "#ff003c" # red
        }
    elif value < 100:
        return {
            "category": "Normal",
            "interpretation": "Fasting blood sugar is in a healthy, normal range.",
            "color": "#00f2ff" # teal/blue
        }
    elif value <= 125:
        return {
            "category": "Prediabetes",
            "interpretation": "Impaired fasting glucose. Elevated risk of progressing to Type 2 Diabetes. Lifestyle and dietary intervention recommended.",
            "color": "#ff9d00" # orange
        }
    else:
        return {
            "category": "Diabetes Range",
            "interpretation": "Fasting glucose meets the diagnostic threshold for diabetes. Diagnostic confirmation via HbA1c test and physician consult are strongly advised.",
            "color": "#ff003c" # red
        }

def interpret_cholesterol(total: float, ldl: float, hdl: float, trig: float, gender: str = "Male") -> dict:
    """
    Interprets Cholesterol Panel (mg/dL).
    """
    results = {}
    
    # Total Cholesterol
    if total <= 0:
        results["total"] = {"category": "N/A", "interpretation": "No data", "color": "#6b8aab"}
    elif total < 200:
        results["total"] = {"category": "Desirable", "interpretation": "Healthy level, associated with lower risk of heart disease.", "color": "#00f2ff"}
    elif total < 240:
        results["total"] = {"category": "Borderline High", "interpretation": "Moderately elevated. Review saturated fat intake.", "color": "#ff9d00"}
    else:
        results["total"] = {"category": "High", "interpretation": "Elevated risk of cardiovascular issues. Action/intervention recommended.", "color": "#ff003c"}
        
    # LDL (Bad Cholesterol)
    if ldl <= 0:
        results["ldl"] = {"category": "N/A", "interpretation": "No data", "color": "#6b8aab"}
    elif ldl < 100:
        results["ldl"] = {"category": "Optimal", "interpretation": "Optimal level for arterial health.", "color": "#00f2ff"}
    elif ldl < 130:
        results["ldl"] = {"category": "Near Optimal", "interpretation": "Good baseline level.", "color": "#00f2ff"}
    elif ldl < 160:
        results["ldl"] = {"category": "Borderline High", "interpretation": "Elevated. Consider lipid-lowering lifestyle adjustments.", "color": "#ff9d00"}
    elif ldl < 190:
        results["ldl"] = {"category": "High", "interpretation": "Significant arterial plaque risk factor.", "color": "#ff003c"}
    else:
        results["ldl"] = {"category": "Very High", "interpretation": "Critically elevated. Medical assessment indicated.", "color": "#ff003c"}

    # HDL (Good Cholesterol)
    hdl_low_threshold = 40 if gender.lower() == "male" else 50
    if hdl <= 0:
        results["hdl"] = {"category": "N/A", "interpretation": "No data", "color": "#6b8aab"}
    elif hdl < hdl_low_threshold:
        results["hdl"] = {"category": "Low (Unfavorable)", "interpretation": "Higher cardiac risk. Exercise and healthy fats help raise HDL.", "color": "#ff003c"}
    elif hdl < 60:
        results["hdl"] = {"category": "Acceptable", "interpretation": "Normal range.", "color": "#00f2ff"}
    else:
        results["hdl"] = {"category": "High (Protective)", "interpretation": "Optimal. High HDL actively protects against heart disease.", "color": "#34d399"} # green

    # Triglycerides
    if trig <= 0:
        results["trig"] = {"category": "N/A", "interpretation": "No data", "color": "#6b8aab"}
    elif trig < 150:
        results["trig"] = {"category": "Normal", "interpretation": "Optimal level of blood fats.", "color": "#00f2ff"}
    elif trig < 200:
        results["trig"] = {"category": "Borderline High", "interpretation": "Slightly elevated. Review simple sugars and alcohol intake.", "color": "#ff9d00"}
    elif trig < 500:
        results["trig"] = {"category": "High", "interpretation": "Increased risk of cardiovascular disease.", "color": "#ff003c"}
    else:
        results["trig"] = {"category": "Very High", "interpretation": "Very high levels. Risk of acute pancreatitis. Urgent consult needed.", "color": "#ff003c"}

    return results

def interpret_blood_pressure(systolic: float, diastolic: float) -> dict:
    """
    Classifies Blood Pressure using ACC/AHA guidelines:
    - Normal: < 120 AND < 80 mmHg
    - Elevated: 120-129 AND < 80 mmHg
    - Stage 1: 130-139 OR 80-89 mmHg
    - Stage 2: >= 140 OR >= 90 mmHg
    - Crisis: > 180 and/or > 120 mmHg
    """
    if systolic <= 0 or diastolic <= 0:
        return {"category": "Invalid", "interpretation": "Please enter valid blood pressure values.", "color": "#6b8aab"}
    
    if systolic > 180 or diastolic > 120:
        return {
            "category": "Hypertensive Crisis",
            "interpretation": "Critically high blood pressure. Requires immediate emergency medical attention if accompanied by chest pain or headache.",
            "color": "#ff003c"
        }
    elif systolic >= 140 or diastolic >= 90:
        return {
            "category": "Stage 2 Hypertension",
            "interpretation": "High blood pressure. Requires lifestyle modifications and likely prescription pharmacotherapy. Monitor regularly.",
            "color": "#ff003c"
        }
    elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
        return {
            "category": "Stage 1 Hypertension",
            "interpretation": "Early high blood pressure. Lifestyle interventions (diet, exercise, stress reduction) are recommended.",
            "color": "#ff9d00"
        }
    elif (120 <= systolic <= 129) and diastolic < 80:
        return {
            "category": "Elevated Blood Pressure",
            "interpretation": "Systolic pressure is slightly elevated. Monitor levels periodically to prevent development of hypertension.",
            "color": "#ff9d00"
        }
    elif systolic < 120 and diastolic < 80:
        return {
            "category": "Normal",
            "interpretation": "Blood pressure is in the optimal healthy range.",
            "color": "#00f2ff"
        }
    else:
        # Default fallback for unusual cases (e.g. systolic < 120 but diastolic 80-89, which is classified as Stage 1)
        return {
            "category": "Stage 1 Hypertension",
            "interpretation": "Diastolic value indicates early high blood pressure.",
            "color": "#ff9d00"
        }
