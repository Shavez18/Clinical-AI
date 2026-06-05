"""
Body Fat Estimation Engine.
Estimates body fat percentage and provides clinical interpretation.
"""
from utils.health_calculators import estimate_body_fat

def analyze_body_fat(bmi: float, age: int, gender: str) -> dict:
    """
    Estimates body fat using the Deurenberg formula and returns classification.
    """
    percentage = estimate_body_fat(bmi, age, gender)
    
    if percentage <= 0:
        return {
            "percentage": 0.0,
            "category": "Invalid",
            "interpretation": "Please enter valid BMI, age, and gender parameters."
        }
        
    is_male = gender.lower() == "male"
    
    if is_male:
        if percentage < 6.0:
            category = "Essential Fat Only"
            interpretation = "Extremely low body fat level. Essential for survival, but not recommended for long-term health."
        elif percentage < 14.0:
            category = "Athletes"
            interpretation = "Excellent body fat level matching elite performance metrics. Highly lean."
        elif percentage < 18.0:
            category = "Fitness"
            interpretation = "Very healthy athletic shape with good muscle definition."
        elif percentage < 25.0:
            category = "Acceptable / Average"
            interpretation = "Healthy average body fat range. Associated with low systemic risk."
        else:
            category = "Obese"
            interpretation = "Elevated body fat levels. Associated with higher risks of cardiovascular disease and metabolic syndrome."
    else: # female
        if percentage < 14.0:
            category = "Essential Fat Only"
            interpretation = "Extremely low body fat level. Essential for reproductive and hormonal health, can cause amenorrhea if maintained."
        elif percentage < 21.0:
            category = "Athletes"
            interpretation = "Very lean. Typical range for competitive female athletes."
        elif percentage < 25.0:
            category = "Fitness"
            interpretation = "Healthy fit shape with good overall tone and lean mass."
        elif percentage < 32.0:
            category = "Acceptable / Average"
            interpretation = "Healthy average body fat range. Associated with typical metabolic profiles."
        else:
            category = "Obese"
            interpretation = "Elevated body fat levels. May negatively impact joints, cardiovascular system, and glycemic control."

    return {
        "percentage": percentage,
        "category": category,
        "interpretation": interpretation
    }
