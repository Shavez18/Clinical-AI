"""
Symptom Assistant Module.
Helps explain symptoms, diagnoses, confidence scores, and clinical terminology.
"""

MEDICAL_DICTIONARY = {
    "angina": "Chest pain or discomfort caused when your heart muscle doesn't get enough oxygen-rich blood. It may feel like pressure or squeezing in your chest.",
    "typical angina": "Classic chest pain triggered by physical exertion or emotional stress, radiating to the arm, shoulder, neck, or jaw, and relieved by rest or nitroglycerin.",
    "atypical angina": "Chest discomfort that does not fit all the criteria of typical angina; often seen in women, diabetics, and elderly patients as shortness of breath or fatigue.",
    "non-anginal": "Chest discomfort that is likely musculoskeletal, gastrointestinal, or respiratory rather than cardiovascular.",
    "lvh": "Left Ventricular Hypertrophy. A condition in which the muscle wall of the heart's main pumping chamber (left ventricle) becomes thickened, often due to high blood pressure.",
    "st-t abnormality": "Alterations in the ST segment or T wave of an ECG, which can indicate myocardial ischemia (lack of blood flow to heart muscle), electrolyte imbalances, or hypertrophy.",
    "thalassemia": "An inherited blood disorder characterized by less oxygen-carrying protein (hemoglobin) and fewer red blood cells than normal.",
    "dyspnea": "Shortness of breath or difficulty breathing, often described as an intense tightening in the chest or air hunger.",
    "glycemic dysregulation": "Difficulty managing blood sugar levels, leading to frequent highs (hyperglycemia) or lows (hypoglycemia), commonly seen in insulin resistance.",
    "microvascular": "Relating to the smallest blood vessels, such as capillaries and arterioles, which can be damaged by long-term high blood sugar.",
    "hct": "Hematocrit. The proportion of total blood volume that is composed of red blood cells. Low HCT suggests anemia.",
    "rbc": "Red Blood Cell count. Measures the number of oxygen-carrying cells in the blood.",
    "wbc": "White Blood Cell count. Measures immune cells that fight infection.",
    "thyroid": "A gland in the neck that secretes hormones regulating growth, development, and metabolic rate.",
    # Diabetes Model Measures
    "pregnancies": "The number of times the patient has been pregnant. High numbers can be linked to gestational diabetes risks.",
    "glucose": "Fasting plasma glucose concentration (mg/dL) measured after an 8-hour fast. Normal is < 100 mg/dL. Prediabetes is 100-125 mg/dL. Diabetes is >= 126 mg/dL.",
    "blood pressure": "Diastolic blood pressure (mmHg). The pressure in the arteries when the heart rests between beats. Normal is < 80 mmHg.",
    "diastolic": "Diastolic blood pressure (mmHg), representing the minimum pressure in the arteries when the heart rests between beats.",
    "systolic": "Systolic blood pressure (mmHg), representing the maximum pressure in the arteries when the heart contracts/beats.",
    "skin thickness": "Triceps skinfold thickness (mm), a standard metric used in anthropometry to estimate total body fat percentage.",
    "insulin": "2-Hour serum insulin (mu U/ml). High levels indicate insulin resistance where cells fail to respond normally to the hormone.",
    "bmi": "Body Mass Index. A ratio of weight to height used to estimate body fat: weight (kg) / [height (m)]^2. Normal range is 18.5 - 24.9.",
    "diabetes pedigree function": "A score that estimates diabetes genetic risk based on family history of the disease. A higher score represents stronger hereditary links.",
    # Cardiac Model Measures
    "cp": "Chest Pain type. Categorized into Typical Angina, Atypical Angina, Non-anginal pain, or Asymptomatic.",
    "chest pain": "Discomfort in the chest cavity, which can be a key clinical indicator of myocardial ischemia (coronary artery disease) or muscular strain.",
    "trestbps": "Resting blood pressure (mmHg) on admission to the clinical facility. Elevated resting BP increases cardiovascular strain.",
    "chol": "Serum cholesterol level (mg/dL). Reflects total lipids in the blood. Desirable levels are < 200 mg/dL.",
    "cholesterol": "Serum cholesterol level (mg/dL). Reflects total lipids in the blood. Desirable levels are < 200 mg/dL.",
    "fbs": "Fasting Blood Sugar > 120 mg/dL (1 = true; 0 = false). Compares glycemic levels to heart health.",
    "restecg": "Resting electrocardiographic results. Normal, ST-T wave abnormality, or Left Ventricular Hypertrophy (LVH).",
    "thalach": "Maximum heart rate achieved during exercise stress testing. Decreased max heart rate is associated with lower cardiac reserve.",
    "max heart rate": "Maximum heart rate achieved during exercise stress testing. Decreased max heart rate is associated with lower cardiac reserve.",
    "exang": "Exercise-induced angina (1 = yes; 0 = no). Chest pain brought on by exercise indicates coronary artery stenosis.",
    "oldpeak": "ST depression induced by exercise relative to rest. Reflects ECG changes during stress testing, indicating cardiac ischemia.",
    "slope": "The slope of the peak exercise ST segment. Classified as Upsloping (healthy), Flat, or Downsloping (ischemic).",
    "ca": "Number of major blood vessels (0-3) colored by fluoroscopy. Represents the count of major coronary arteries showing occlusion.",
    "vessels": "Number of major blood vessels (0-3) colored by fluoroscopy. Represents the count of major coronary arteries showing occlusion.",
    "thal": "Thalassemia status, an inherited blood disorder. Categorized as Normal, Fixed defect, or Reversible defect."
}

def explain_symptom_or_term(query: str) -> str:
    """
    Scans the user query for clinical terms or symptoms and returns clear, professional explanations.
    """
    query_lower = query.lower()
    matches = []
    
    for term, definition in MEDICAL_DICTIONARY.items():
        if term in query_lower:
            matches.append(f"🔍 **{term.title()}**\n{definition}")
            
    if matches:
        return "\n\n".join(matches)
        
    return (
        "I can help explain clinical symptoms, terms, and how diagnostic engines work. "
        "Here are some terms you can ask me about: **Angina**, **LVH (Left Ventricular Hypertrophy)**, **Dyspnea**, **Thalassemia**, or **HCT/RBC**."
    )

def explain_differential_confidence(disease: str, prob: float, confidence_class: str) -> str:
    """
    Explains the statistical confidence scores of the NLP differential diagnosis engine.
    """
    explanation = f"### 🧠 Clinical NLP Rationale: {disease} ({prob}% Probability)\n"
    explanation += f"**Confidence Tier:** {confidence_class}\n\n"
    explanation += (
        "The Clinical NLP engine parses unstructured clinical text using named entity recognition "
        "and symptoms mapping. It matches symptoms to potential diagnostic pathways. "
        f"For **{disease}**, the confidence score is calculated based on:\n"
        "- **Symptom Density:** The presence of key pathognomonic symptoms.\n"
        "- **Duration & Demographics:** Cross-referencing age, gender, and duration weightings.\n"
        "- **Negative/Absence Flags:** Exclusion of contradictory findings.\n\n"
        "**Note:** A probability score represents model calibration based on historical clinical datasets. "
        "It should be used as a triage prioritization tool, not a definitive diagnosis."
    )
    return explanation
