"""
BMI Intelligence Engine.
Interprets height and weight to provide clinical BMI outputs.
"""
from utils.health_calculators import calculate_bmi, calculate_bmi_range

def analyze_bmi(height_cm: float, weight_kg: float) -> dict:
    """
    Computes BMI and returns detailed clinical classification,
    target ranges, and health risk implications.
    """
    bmi_score = calculate_bmi(height_cm, weight_kg)
    min_weight, max_weight = calculate_bmi_range(height_cm)
    
    if bmi_score <= 0:
        return {
            "bmi": 0.0,
            "category": "Invalid",
            "healthy_range": "18.5-24.9",
            "target_weight_range": "0kg-0kg",
            "adjustment": "None",
            "diabetes_impact": "N/A",
            "cardiovascular_impact": "N/A",
            "clinical_impact": "Please provide valid height and weight values."
        }
        
    # Categories
    if bmi_score < 18.5:
        category = "Underweight"
        adjustment = f"Gain {round(min_weight - weight_kg, 1)}kg"
        diabetes_impact = "Low baseline risk for Type 2 Diabetes, but high risk for nutrient deficiencies."
        cardiovascular_impact = "Potential increased risk for arrhythmia or hypotension."
        clinical_impact = "Elevated risk of osteoporosis, anemia, and immune dysfunction."
    elif bmi_score < 25.0:
        category = "Healthy / Normal Weight"
        adjustment = "Maintain current weight"
        diabetes_impact = "Optimal. Lowest correlation with insulin resistance."
        cardiovascular_impact = "Optimal vascular risk baseline."
        clinical_impact = "Metabolic health is in the ideal range. Continue balanced diet and physical activity."
    elif bmi_score < 30.0:
        category = "Overweight"
        adjustment = f"Lose {round(weight_kg - max_weight, 1)}kg"
        diabetes_impact = "Moderate increase in insulin resistance risk."
        cardiovascular_impact = "Mild to moderate increase in blood pressure and arterial stress."
        clinical_impact = "Moderate increase in diabetes and cardiovascular risk."
    else:
        category = "Obese"
        adjustment = f"Lose {round(weight_kg - max_weight, 1)}kg"
        diabetes_impact = "High risk. Strongly correlated with cellular insulin resistance and metabolic syndrome."
        cardiovascular_impact = "High risk of coronary artery disease, hypertension, and atherosclerosis."
        clinical_impact = "Severe risk amplification for metabolic, cardiovascular, and osteoarticular systems."
        
    return {
        "bmi": bmi_score,
        "category": category,
        "healthy_range": "18.5–24.9",
        "target_weight_range": f"{int(min_weight)}kg–{int(max_weight)}kg",
        "adjustment": adjustment,
        "diabetes_impact": diabetes_impact,
        "cardiovascular_impact": cardiovascular_impact,
        "clinical_impact": clinical_impact
    }
