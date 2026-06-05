"""
Recommendation Engine Module.
Generates clinical recommendations, diet modifications, and exercise regimes.
"""

def get_recommendations(bmi: float = 0, glucose: float = 0, cholesterol: float = 0, bp_systolic: float = 0, bp_diastolic: float = 0) -> list:
    """
    Generates target recommendations based on blood pressure, blood glucose, cholesterol, and BMI.
    """
    recs = []
    
    # BMI Recommendations
    if bmi >= 30:
        recs.append({
            "category": "Diet & Lifestyle",
            "title": "⚖️ Weight Management (Obesity)",
            "guideline": "Aim for a moderate calorie deficit. Target 150 minutes of moderate-intensity aerobic exercise per week combined with strength training. Prioritize whole foods with low caloric density."
        })
    elif bmi >= 25:
        recs.append({
            "category": "Diet & Lifestyle",
            "title": "⚖️ Weight Management (Overweight)",
            "guideline": "Focus on lifestyle habits. Reduce portion sizes, limit processed snacks, and build a consistent physical activity schedule."
        })
        
    # Glucose Recommendations
    if glucose >= 126:
        recs.append({
            "category": "Clinical Follow-up",
            "title": "🩸 Diabetes Level Glycemia",
            "guideline": "Endocrinologist consult recommended. Get an HbA1c blood test to confirm average glucose levels. Monitor carbohydrate intake and log daily values."
        })
    elif glucose >= 100:
        recs.append({
            "category": "Preventive Diet",
            "title": "🩸 Prediabetes Glycemia Control",
            "guideline": "Adopt a low-glycemic index diet. Increase fiber intake to slow glucose absorption. Avoid sugary beverages and simple sugars."
        })
        
    # Cholesterol Recommendations
    if cholesterol >= 240:
        recs.append({
            "category": "Dietary Intervention",
            "title": "🍔 Hypercholesterolemia Management",
            "guideline": "Substantially reduce saturated fats and eliminate trans fats. Incorporate soluble fiber (oats, beans) and plant sterols to help lower LDL."
        })
    elif cholesterol >= 200:
        recs.append({
            "category": "Preventive Lifestyle",
            "title": "🍔 Borderline High Cholesterol",
            "guideline": "Incorporate heart-healthy fats (olive oil, avocados, nuts). Keep track of lipid profiles every 6 months."
        })
        
    # Blood Pressure Recommendations
    if bp_systolic >= 140 or bp_diastolic >= 90:
        recs.append({
            "category": "Clinical Management",
            "title": "🫀 Hypertension Control",
            "guideline": "Restrict sodium intake to <1,500 mg per day. Check blood pressure twice daily. Discuss medical management options with your physician."
        })
    elif (120 <= bp_systolic < 140) or (80 <= bp_diastolic < 90):
        recs.append({
            "category": "Preventive Action",
            "title": "🫀 Elevated Blood Pressure",
            "guideline": "Implement the DASH (Dietary Approaches to Stop Hypertension) diet, rich in potassium, calcium, and magnesium. Limit alcohol and stress."
        })
        
    # Default recommendations if all parameters are normal
    if not recs:
        recs.append({
            "category": "Wellness Maintenance",
            "title": "🟢 Optimal Metabolic State",
            "guideline": "All tracked parameters are within reference limits. Maintain a nutrient-dense diet, stay hydrated, aim for 7-8 hours of sleep, and participate in regular exercise."
        })
        
    return recs
