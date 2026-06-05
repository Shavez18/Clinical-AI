import pandas as pd
import numpy as np

def calculate_toxicity_score(risk_score, interactions, safety_profiles):
    """Calculates a simulated multi-factor toxicity score."""
    # Base score is risk_score
    score = risk_score
    
    # Add penalty for major interactions
    major_count = sum(1 for i in interactions if i.get("severity", "").lower() == "major")
    score += major_count * 15
    
    # Add penalty for boxed warnings and contraindications
    for sp in safety_profiles:
        score += len(sp.get("boxed_warnings", [])) * 5
        score += len(sp.get("contraindications", [])) * 3
        
    # Cap at 100
    return min(100.0, score)

def extract_pharmacological_classes(safety_profiles):
    """Mocks extraction of pharmacological classes for visualization."""
    # Since OpenFDA data format might not explicitly state simple classes,
    # we simulate this based on drug names to create a rich UI.
    mock_classes = {
        "aspirin": "NSAID",
        "warfarin": "Anticoagulant",
        "amiodarone": "Antiarrhythmic",
        "lisinopril": "ACE Inhibitor",
        "metformin": "Biguanide",
        "atorvastatin": "Statin",
        "omeprazole": "PPI",
        "simvastatin": "Statin",
        "levothyroxine": "Thyroid Hormone",
        "amlodipine": "Calcium Channel Blocker",
    }
    
    classes = {}
    for sp in safety_profiles:
        drug = sp.get("drug", "").lower()
        # Find partial match or default to 'Unknown Class'
        assigned_class = "Systemic Agent"
        for k, v in mock_classes.items():
            if k in drug:
                assigned_class = v
                break
        classes[drug] = assigned_class
    return classes

def generate_compatibility_matrix(drug_list, interactions):
    """Generates a matrix showing compatibility between all pairs of drugs."""
    n = len(drug_list)
    matrix = np.zeros((n, n))
    
    # Map severity to numeric risk
    severity_map = {"major": 0.9, "moderate": 0.5, "minor": 0.2}
    
    for i in interactions:
        pair = [d.lower() for d in i.get("drug_pair", [])]
        sev = i.get("severity", "").lower()
        val = severity_map.get(sev, 0.1)
        
        # Find indices
        idx1, idx2 = -1, -1
        for idx, d in enumerate(drug_list):
            if pair[0] in d.lower(): idx1 = idx
            if pair[1] in d.lower(): idx2 = idx
            
        if idx1 != -1 and idx2 != -1:
            matrix[idx1][idx2] = val
            matrix[idx2][idx1] = val # symmetric
            
    # Self compatibility is 0 risk
    for i in range(n):
        matrix[i][i] = 0.0
        
    return pd.DataFrame(matrix, index=drug_list, columns=drug_list)

def estimate_organ_impact(interactions, safety_profiles):
    """Estimates the impact of the drug regimen on various organ systems."""
    organs = {
        "Hepatic (Liver)": 10,
        "Renal (Kidney)": 10,
        "Cardiovascular": 10,
        "Gastrointestinal": 10,
        "Neurological": 10
    }
    
    # Increase risk based on interactions and warnings
    for i in interactions:
        mech = i.get("mechanism", "").lower()
        sev = i.get("severity", "").lower()
        multiplier = 2 if sev == "major" else 1.5 if sev == "moderate" else 1.1
        
        if "cyp" in mech or "metabolism" in mech:
            organs["Hepatic (Liver)"] *= multiplier
        if "renal" in mech or "clearance" in mech:
            organs["Renal (Kidney)"] *= multiplier
        if "qt" in mech or "blood pressure" in mech or "arrhythmia" in mech:
            organs["Cardiovascular"] *= multiplier
        if "bleeding" in mech or "ulcer" in mech:
            organs["Gastrointestinal"] *= multiplier
        if "cns" in mech or "sedation" in mech:
            organs["Neurological"] *= multiplier
            
    for sp in safety_profiles:
        for w in sp.get("boxed_warnings", []):
            w_lower = w.lower()
            if "liver" in w_lower or "hepatic" in w_lower: organs["Hepatic (Liver)"] += 20
            if "kidney" in w_lower or "renal" in w_lower: organs["Renal (Kidney)"] += 20
            if "heart" in w_lower or "cardio" in w_lower: organs["Cardiovascular"] += 20
            if "bleed" in w_lower or "gi" in w_lower: organs["Gastrointestinal"] += 20
            if "seizure" in w_lower or "cns" in w_lower: organs["Neurological"] += 20
            
    # Cap values at 100
    for k in organs:
        organs[k] = min(100, organs[k])
        
    return organs
