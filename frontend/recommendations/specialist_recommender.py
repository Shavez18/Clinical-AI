"""
specialist_recommender.py
────────────────────────────────────────────────────────────────────────────
Returns structured specialist recommendation data based on module + risk tier.
NEVER displays real/fake doctor names, phone numbers, or booking systems.
"""

from __future__ import annotations


# ── Specialist data registry ──────────────────────────────────────────────────
_SPECIALIST_DB: dict[str, dict] = {
    "general_physician": {
        "specialty":  "General Physician",
        "role":       "Provides primary care, preventive guidance, and coordinates specialist referrals.",
        "icon":       "🩺",
    },
    "endocrinologist": {
        "specialty":  "Endocrinologist",
        "role":       "Specializes in hormonal and metabolic disorders, including diabetes and thyroid conditions.",
        "icon":       "🔬",
    },
    "cardiologist": {
        "specialty":  "Cardiologist",
        "role":       "Diagnoses and manages cardiovascular diseases, including heart failure, arrhythmias, and coronary artery disease.",
        "icon":       "🫀",
    },
    "pulmonologist": {
        "specialty":  "Pulmonologist",
        "role":       "Manages respiratory conditions such as asthma, COPD, and pulmonary infections.",
        "icon":       "🫁",
    },
    "neurologist": {
        "specialty":  "Neurologist",
        "role":       "Diagnoses and treats disorders of the nervous system including migraines, epilepsy, and stroke.",
        "icon":       "🧠",
    },
    "gastroenterologist": {
        "specialty":  "Gastroenterologist",
        "role":       "Manages disorders of the digestive system including the stomach, intestines, and liver.",
        "icon":       "🏥",
    },
    "internal_medicine": {
        "specialty":  "Internal Medicine Specialist",
        "role":       "Provides comprehensive care for adult patients with complex or undifferentiated medical conditions.",
        "icon":       "⚕️",
    },
    "clinical_pharmacologist": {
        "specialty":  "Clinical Pharmacologist",
        "role":       "Evaluates drug safety, pharmacokinetics, and manages complex polypharmacy regimens.",
        "icon":       "💊",
    },
    "pharmacist": {
        "specialty":  "Pharmacist / General Physician",
        "role":       "Reviews medication safety, dosing, and provides guidance on minor drug interactions.",
        "icon":       "⚗️",
    },
}


# ── Module-specific recommendation logic ─────────────────────────────────────

def recommend_diabetes_specialist(risk_tier: str) -> dict:
    """Returns specialist recommendation for diabetes module."""
    if risk_tier == "low":
        return {
            **_SPECIALIST_DB["general_physician"],
            "reason":       "Routine preventive healthcare and lifestyle guidance is recommended at this risk level.",
            "next_step":    "Consult a General Physician for an annual health check-up and metabolic screening.",
        }
    else:  # moderate or high
        return {
            **_SPECIALIST_DB["endocrinologist"],
            "reason":       "Elevated diabetes risk indicators detected. Specialist metabolic evaluation is advised.",
            "next_step":    "Consult a qualified Endocrinologist for a comprehensive metabolic and hormonal assessment.",
        }


def recommend_heart_specialist(risk_tier: str) -> dict:
    """Returns specialist recommendation for cardiovascular module."""
    if risk_tier == "low":
        return {
            **_SPECIALIST_DB["general_physician"],
            "reason":       "No high-risk cardiovascular indicators detected. Preventive primary care is appropriate.",
            "next_step":    "Consult a General Physician for routine cardiovascular health screening.",
        }
    else:  # moderate or high
        return {
            **_SPECIALIST_DB["cardiologist"],
            "reason":       "Elevated cardiovascular risk detected. Cardiological evaluation is clinically indicated.",
            "next_step":    "Consult a qualified Cardiologist for a comprehensive cardiovascular risk assessment.",
        }


def recommend_symptom_specialist(symptom_category: str) -> dict:
    """Returns specialist recommendation based on NLP-detected symptom category."""
    mapping = {
        "respiratory":         "pulmonologist",
        "cardiac":             "cardiologist",
        "metabolic":           "endocrinologist",
        "neurological":        "neurologist",
        "gastroenterological": "gastroenterologist",
        "general":             "internal_medicine",
    }
    key = mapping.get(symptom_category, "internal_medicine")
    specialist = _SPECIALIST_DB[key]
    reason_map = {
        "respiratory":         "The primary differential suggests a respiratory etiology.",
        "cardiac":             "Cardiac symptom patterns detected in the clinical notes.",
        "metabolic":           "Metabolic or endocrine indicators identified in the differential.",
        "neurological":        "Neurological symptom patterns detected. Specialist evaluation is advised.",
        "gastroenterological": "Gastrointestinal etiology suggested by the clinical notes.",
        "general":             "Undifferentiated clinical presentation. Internal Medicine evaluation is recommended.",
    }
    return {
        **specialist,
        "reason":    reason_map.get(symptom_category, "Clinical evaluation recommended."),
        "next_step": f"Consult a qualified {specialist['specialty']} for a detailed clinical evaluation.",
    }


def recommend_drug_specialist(risk_tier: str) -> dict:
    """Returns specialist recommendation for drug interaction module."""
    if risk_tier == "low":
        return {
            **_SPECIALIST_DB["pharmacist"],
            "reason":       "Minor interaction detected. A pharmacist or general physician review is sufficient.",
            "next_step":    "Discuss current medications with your prescribing physician or a licensed pharmacist.",
        }
    else:  # moderate or high
        return {
            **_SPECIALIST_DB["clinical_pharmacologist"],
            "reason":       "Significant pharmacokinetic or pharmacodynamic interactions detected. Expert review is required.",
            "next_step":    "Consult a Clinical Pharmacologist for a comprehensive drug regimen safety review.",
        }
