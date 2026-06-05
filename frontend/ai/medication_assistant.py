"""
Drug Information Assistant Module.
Explains purposes, adverse effects, interactions, and monitoring parameters for common medications.
"""

DRUG_DATABASE = {
    "metformin": {
        "purpose": "Biguanide antihyperglycemic used as first-line therapy for Type 2 Diabetes to improve insulin sensitivity and reduce hepatic glucose production.",
        "adverse_effects": "Gastrointestinal disturbances (nausea, diarrhea, abdominal pain), metallic taste, and rare but serious lactic acidosis.",
        "monitoring": "Renal function (eGFR) prior to initiation and at least annually. Monitor HbA1c every 3-6 months.",
        "interactions": "Contrast dyes (increased risk of lactic acidosis; hold metformin 48h before/after), alcohol (enhances lactic acidosis risk)."
    },
    "lisinopril": {
        "purpose": "ACE Inhibitor used for management of hypertension and heart failure. Relaxes blood vessels to lower blood pressure.",
        "adverse_effects": "Dry cough, hyperkalemia (high potassium), dizziness, headache, and rare but serious angioedema (swelling).",
        "monitoring": "Serum potassium, serum creatinine, and renal function. Regular blood pressure tracking.",
        "interactions": "Potassium supplements or potassium-sparing diuretics (e.g., Spironolactone) - risk of severe hyperkalemia. NSAIDs (e.g., Ibuprofen) - reduces lisinopril efficacy and increases renal toxicity risk."
    },
    "atorvastatin": {
        "purpose": "HMG-CoA Reductase Inhibitor (statin) used to lower LDL cholesterol and triglycerides while raising HDL cholesterol, reducing risk of myocardial infarction.",
        "adverse_effects": "Myalgia (muscle pain/weakness), mild elevation of liver enzymes (ALT/AST), dyspepsia, and headache.",
        "monitoring": "Baseline liver function tests (LFTs). Periodic lipid panels to assess therapy response.",
        "interactions": "Grapefruit juice (increases atorvastatin blood levels, raising risk of muscle toxicity/rhabdomyolysis). Certain antifungals and fibrates."
    },
    "lipitor": {
        "purpose": "Brand name for Atorvastatin, an HMG-CoA Reductase Inhibitor used to treat hypercholesterolemia and reduce cardiovascular risk.",
        "adverse_effects": "Myalgia, mild liver enzyme elevation, and digestive issues.",
        "monitoring": "Baseline liver function tests and periodic lipid panels.",
        "interactions": "Grapefruit juice, fibrates, and certain antimicrobials."
    },
    "aspirin": {
        "purpose": "Antiplatelet agent (NSAID) used to prevent thrombosis, stroke, and myocardial infarction in patients with established cardiovascular disease.",
        "adverse_effects": "Gastrointestinal bleeding, gastric ulcers, tinnitus (at higher doses), and bruising.",
        "monitoring": "Monitor for signs of bleeding (black tarry stools, easy bruising) and periodic hemoglobin levels.",
        "interactions": "Anticoagulants (e.g. Warfarin, Apixaban) - significantly elevates bleeding risk. NSAIDs (can block aspirin's cardio-protective antiplatelet effect)."
    },
    "warfarin": {
        "purpose": "Vitamin K antagonist anticoagulant used to prevent thromboembolic complications in atrial fibrillation, mechanical heart valves, and DVT.",
        "adverse_effects": "Major bleeding, skin necrosis, hematomas, and bruising.",
        "monitoring": "Frequent blood testing of Prothrombin Time / International Normalized Ratio (INR). Target INR is usually 2.0-3.0.",
        "interactions": "Aspirin/NSAIDs (massive bleeding risk), antibiotics (can alter gut flora and raise INR), Vitamin K rich foods (green leafy vegetables - can decrease warfarin efficacy; maintain consistent intake)."
    }
}

def explain_medication(query: str) -> str:
    """
    Looks up medication details from query and returns formatted explanations.
    """
    query_lower = query.lower()
    matches = []
    
    for drug, data in DRUG_DATABASE.items():
        if drug in query_lower:
            matches.append(
                f"### 💊 Medication Profile: {drug.title()}\n"
                f"- **Clinical Purpose:** {data['purpose']}\n"
                f"- **Adverse Effects:** {data['adverse_effects']}\n"
                f"- **Monitoring Requirements:** {data['monitoring']}\n"
                f"- **Notable Interactions:** {data['interactions']}"
            )
            
    if matches:
        return "\n\n".join(matches)
        
    return (
        "I can explain clinical indications, adverse effects, interactions, and monitoring requirements for drugs. "
        "Try asking me about **Metformin**, **Lisinopril**, **Atorvastatin (Lipitor)**, **Aspirin**, or **Warfarin**."
    )

def explain_drug_interaction(drug_a: str, drug_b: str, interaction_details: str = "") -> str:
    """
    Explains the pharmacological mechanism behind a detected drug-drug interaction.
    """
    drug_a_l, drug_b_l = drug_a.lower(), drug_b.lower()
    
    # Check if we have standard interaction explanation in DB
    explanation = f"### ⚠️ Drug Interaction: {drug_a.title()} + {drug_b.title()}\n"
    
    # Custom known interactions
    if ("aspirin" in drug_a_l and "warfarin" in drug_b_l) or ("warfarin" in drug_a_l and "aspirin" in drug_b_l):
        explanation += (
            "**Mechanism:** Synergistic pharmacodynamic interaction. Both agents inhibit thrombus formation via different pathways "
            "(Aspirin inhibits platelet aggregation; Warfarin inhibits clotting factor synthesis). Combining them dramatically increases "
            "the risk of major gastrointestinal and systemic bleeding.\n"
            "**Action / Monitoring:** Monitor INR closely. Watch for symptoms of bleeding (bruising, dark stools, nosebleeds)."
        )
    elif ("lisinopril" in drug_a_l and "spironolactone" in drug_b_l) or ("spironolactone" in drug_a_l and "lisinopril" in drug_b_l):
        explanation += (
            "**Mechanism:** Additive hyperkalemic effect. Lisinopril reduces aldosterone levels, leading to potassium retention. Spironolactone "
            "is a potassium-sparing diuretic that blocks aldosterone receptors, also causing potassium retention. The combination can lead to "
            "life-threatening hyperkalemia (cardiac arrhythmias).\n"
            "**Action / Monitoring:** Check serum potassium and creatinine within 1-2 weeks of starting combination, then periodically."
        )
    else:
        explanation += (
            f"**Details:** {interaction_details or 'Co-administration may alter metabolic clearance or produce additive pharmacodynamic effects.'}\n"
            "**Guidance:** Advise clinical review. Regular telemetry, renal profiling, and patient warning of adverse indicators (dizziness, fatigue, bleeding) are recommended."
        )
        
    return explanation
