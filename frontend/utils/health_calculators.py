"""
Health Calculators Utility.
Provides basic calculations for BMI, Body Fat Percentage, and Ideal Weight.
"""

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculates BMI given height in cm and weight in kg."""
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 1)

def calculate_bmi_range(height_cm: float) -> tuple[float, float]:
    """Returns the healthy weight range (kg) for a height based on normal BMI (18.5 to 24.9)."""
    if height_cm <= 0:
        return 0.0, 0.0
    height_m = height_cm / 100.0
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)
    return round(min_weight, 1), round(max_weight, 1)

def estimate_body_fat(bmi: float, age: int, gender: str) -> float:
    """
    Estimates body fat percentage using the Deurenberg formula.
    gender: 'Male' or 'Female' (or 'Other')
    """
    if bmi <= 0 or age <= 0:
        return 0.0
    
    # Gender value: Male = 1, Female = 0
    gender_val = 1 if gender.lower() == 'male' else 0
    
    # Deurenberg formula for adults
    body_fat = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_val) - 5.4
    return max(0.0, round(body_fat, 1))

def calculate_ideal_weight_devine(height_cm: float, gender: str) -> float:
    """
    Calculates ideal body weight in kg using the Devine Formula (1974).
    Devine formula is based on height in inches (> 60 inches / 152.4 cm).
    """
    if height_cm <= 0:
        return 0.0
    
    height_inches = height_cm / 2.54
    inches_over_60 = max(0.0, height_inches - 60)
    
    if gender.lower() == 'male':
        weight = 50.0 + (2.3 * inches_over_60)
    else: # default/female
        weight = 45.5 + (2.3 * inches_over_60)
        
    return round(weight, 1)

def calculate_ideal_weight_robinson(height_cm: float, gender: str) -> float:
    """
    Calculates ideal body weight in kg using the Robinson Formula (1983).
    """
    if height_cm <= 0:
        return 0.0
    
    height_inches = height_cm / 2.54
    inches_over_60 = max(0.0, height_inches - 60)
    
    if gender.lower() == 'male':
        weight = 52.0 + (1.9 * inches_over_60)
    else:
        weight = 49.0 + (1.7 * inches_over_60)
        
    return round(weight, 1)
