# Expanded Disease Mapping System
# Assigns required, supporting, and exclusion symptoms for strong clinical validations

DISEASE_RULES = {
    "Heart attack": {
        "required": ["chest pain"],
        "supporting": ["shortness of breath", "sweating", "nausea", "vomiting", "pain", "dizziness"],
        "exclude": []
    },
    "Stroke": {
        "required": ["unilateral weakness", "loss of consciousness", "stroke", "speech difficulty", "fainting"],
        "supporting": ["dizziness", "confusion", "headache", "numbness"],
        "exclude": []
    },
    "(vertigo) Paroymsal  Positional Vertigo": {
        "required": ["dizziness", "spinning", "loss of balance", "movement", "unsteadiness"],
        "supporting": ["nausea", "vomiting"],
        "exclude": []
    },
    "Migraine": {
        "required": ["headache", "severe headache", "unilateral headache", "aura"],
        "supporting": ["nausea", "vomiting", "photophobia", "visual disturbance", "stiff neck"],
        "exclude": []
    },
    "Malaria": {
        "required": ["fever", "chill", "chills"],
        "supporting": ["sweating", "headache", "nausea", "muscle pain", "fatigue"],
        "exclude": []
    },
    "Dengue": {
        "required": ["fever"],
        "supporting": ["joint pain", "eye pain", "rash", "spot", "red", "headache", "muscle pain", "appetite loss"],
        "exclude": []
    },
    "GERD": {
        "required": ["heartburn", "chest pain", "acid", "acidity"],
        "supporting": ["cough", "ulcer", "nausea"],
        "exclude": []
    },
    "Pneumonia": {
        "required": ["shortness of breath", "cough", "breathlessness", "fever"],
        "supporting": ["chest pain", "sputum", "rusty phlegm", "fast heart rate", "fatigue", "chill"],
        "exclude": []
    },
    "Tuberculosis": {
        "required": ["cough", "sputum", "blood", "blood in sputum"],
        "supporting": ["weight loss", "chest pain", "shortness of breath", "fever", "night sweats", "fatigue"],
        "exclude": []
    },
    "Common Cold": {
        "required": ["congestion", "runny nose", "sneezing", "cough", "sore throat"],
        "supporting": ["headache", "fatigue", "fever", "chest pressure", "smell loss", "eye redness"],
        "exclude": []
    },
    "Gastroenteritis": {
        "required": ["diarrhoea", "vomiting", "nausea"],
        "supporting": ["stomach pain", "abdominal pain", "dehydration", "sunken eyes", "fever"],
        "exclude": []
    },
    "Typhoid": {
        "required": ["fever", "belly pain", "abdominal pain"],
        "supporting": ["chill", "fatigue", "headache", "nausea", "toxic look", "constipation"],
        "exclude": []
    },
    "Allergy": {
        "required": ["sneezing", "runny nose", "itching", "watering eyes", "rash"],
        "supporting": ["congestion", "cough", "shivering", "chills"],
        "exclude": []
    },
    "Arthritis": {
        "required": ["joint pain", "stiff joint", "stiff neck", "painful movement"],
        "supporting": ["muscle weakness", "swelling", "fatigue"],
        "exclude": []
    },
    "Bronchial Asthma": {
        "required": ["shortness of breath", "wheezing", "breathlessness"],
        "supporting": ["cough", "chest tightness", "fatigue", "mucoid sputum"],
        "exclude": []
    },
    "Diabetes ": {
        "required": ["sugar", "excessive hunger", "excessive thirst", "frequent urination"],
        "supporting": ["fatigue", "weight loss", "blurred vision", "obesity"],
        "exclude": []
    },
    "Hypertension ": {
        "required": ["dizziness", "headache", "chest pain"],
        "supporting": ["lack of concentration", "loss of balance", "fatigue"],
        "exclude": []
    },
    "Hepatitis A": {
        "required": ["yellow skin", "yellowish skin", "yellow eyes", "abdominal pain", "dark urine"],
        "supporting": ["fever", "nausea", "fatigue"],
        "exclude": []
    },
    "AIDS": {
        "required": ["fever", "fatigue", "muscle pain", "rash", "sore throat"],
        "supporting": ["weight loss", "patch"],
        "exclude": []
    },
    "Chicken pox": {
        "required": ["rash", "itching", "fever", "fatigue"],
        "supporting": ["headache", "red spots"],
        "exclude": []
    },
    "Fungal infection": {
        "required": ["itching", "skin rash", "rash"],
        "supporting": ["dischromic patches", "swelling"],
        "exclude": []
    }
}

CONTEXT_RULES = {
    "Malaria": {"keywords": ["travel", "tropical", "africa", "asia", "india"], "bonus": 0.45},
    "Dengue": {"keywords": ["travel", "tropical", "mosquito", "rainy"], "bonus": 0.35},
    "Tuberculosis": {"keywords": ["months", "years", "chronic", "weeks"], "bonus": 0.4},
    "Pneumonia": {"keywords": ["days", "week"], "bonus": 0.25}
}

# The Master List must include both lemmas and common surface forms
_CORE = ["fatigue", "weakness", "pain", "swelling", "redness", "itching", "rash", "fever", "cough", "nausea", "headache", "dizziness", "vomiting", "chills", "sweating", "sweat", "shortness of breath", "chest pain", "joint pain", "muscle pain", "stomach pain", "abdominal pain", "diarrhoea", "constipation", "weight loss", "yellow skin", "yellow eyes", "dark urine", "skin rash"]
MASTER_SYMPTOMS_LIST = set(_CORE)
for disease, rule in DISEASE_RULES.items():
    MASTER_SYMPTOMS_LIST.update(rule.get("required", []))
    MASTER_SYMPTOMS_LIST.update(rule.get("supporting", []))

SYMPTOM_WEIGHTS = {
    "chest pain": 10, "shortness of breath": 10, "stroke": 10, "loss of consciousness": 10, "unilateral weakness": 10, "speech difficulty": 10, "fainting": 10,
    "severe headache": 9, "unilateral headache": 8, "high fever": 9, "fever": 7, "photophobia": 8, "aura": 8, "stiff neck": 8,
    "yellow eyes": 9, "yellow skin": 9, "dark urine": 8, "skin rash": 7, "rash": 6,
    "nausea": 5, "vomiting": 6, "headache": 6, "dizziness": 6, "sweating": 5, "sweat": 5, "chills": 5, "cough": 5, "diarrhoea": 6, "stomach pain": 6, "abdominal pain": 6,
    "fatigue": 3, "pain": 3, "sneezing": 2, "runny nose": 3, "sore throat": 3, "itching": 2
}
