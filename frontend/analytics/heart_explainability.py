import random

def generate_heart_simulated_shap(features, risk_score):
    """
    Simulates SHAP feature attributions for cardiovascular risk.
    """
    shap_values = {}
    
    # Age: Risk increases with age
    age = features.get('age', 0)
    if age > 55:
        shap_values['Age'] = (age - 55) * 0.1 + random.uniform(1.0, 3.0)
    else:
        shap_values['Age'] = random.uniform(-1.5, -0.2)
        
    # Trestbps (Resting Blood Pressure)
    trestbps = features.get('trestbps', 0)
    if trestbps > 130:
        shap_values['Resting BP'] = (trestbps - 130) * 0.05 + random.uniform(0.5, 2.0)
    else:
        shap_values['Resting BP'] = random.uniform(-1.0, 0.5)

    # Chol (Cholesterol)
    chol = features.get('chol', 0)
    if chol > 240:
        shap_values['Cholesterol'] = (chol - 240) * 0.02 + random.uniform(0.5, 2.0)
    else:
        shap_values['Cholesterol'] = random.uniform(-1.5, 0.5)
        
    # Thalach (Max Heart Rate) - lower is often worse for given effort, but here just simulated
    thalach = features.get('thalach', 0)
    if thalach < 120:
        shap_values['Max Heart Rate'] = random.uniform(1.0, 3.0)
    else:
        shap_values['Max Heart Rate'] = random.uniform(-2.0, 0.0)

    # Chest Pain (cp)
    cp = features.get('cp', 0)
    if cp > 0: # 1, 2, 3 indicate some angina or non-anginal pain
        shap_values['Chest Pain Type'] = cp * 1.5 + random.uniform(0.5, 2.0)
    else:
        shap_values['Chest Pain Type'] = random.uniform(-1.0, 0.0)
        
    # Oldpeak (ST Depression)
    oldpeak = features.get('oldpeak', 0.0)
    if oldpeak > 1.0:
        shap_values['ST Depression'] = oldpeak * 2.0 + random.uniform(0.5, 1.5)
    else:
        shap_values['ST Depression'] = random.uniform(-1.0, 0.0)
        
    # Normalize the SHAP values
    total_positive_shap = sum(v for v in shap_values.values() if v > 0)
    scale_factor = (risk_score / 10.0) / (total_positive_shap + 0.1) if risk_score > 20 else 0.5
    
    final_shap = {k: v * scale_factor for k, v in shap_values.items()}
    return final_shap

def calculate_heart_confidence(risk_score, features):
    """
    Simulates a prediction confidence metric for heart disease.
    """
    if risk_score > 85 or risk_score < 15:
        base_conf = random.uniform(94.0, 99.1)
    elif risk_score > 70 or risk_score < 30:
        base_conf = random.uniform(88.0, 93.9)
    else:
        base_conf = random.uniform(78.0, 87.9)
        
    # Penalize confidence if inputs are highly anomalous
    if features.get('trestbps', 0) > 200 or features.get('chol', 0) > 500:
        base_conf -= random.uniform(5.0, 10.0)
        
    return min(99.9, max(50.0, base_conf))
