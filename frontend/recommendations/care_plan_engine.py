"""
care_plan_engine.py
────────────────────────────────────────────────────────────────────────────
Generates structured care plan data objects per module and risk tier.
Pure data layer — no Streamlit calls, no UI code.
"""

from __future__ import annotations


# ── DIABETES CARE PLANS ───────────────────────────────────────────────────────

_DIABETES_PLANS = {
    "low": {
        "risk_factors": [
            "BMI in acceptable range",
            "Fasting glucose within reference",
            "Age-related metabolic monitoring recommended",
        ],
        "actions": [
            "Maintain a healthy BMI through balanced nutrition",
            "Engage in at least 150 minutes of moderate aerobic activity per week",
            "Schedule annual fasting glucose and HbA1c monitoring",
            "Follow a fibre-rich, low-glycaemic-index diet",
            "Ensure adequate sleep (7–9 hours per night)",
        ],
        "follow_up": [
            "Annual general health check-up",
            "Glucose monitoring every 12 months",
            "Weight and BMI check at each primary care visit",
        ],
        "timeline": "12 months",
    },
    "moderate": {
        "risk_factors": [
            "Elevated fasting glucose or borderline BMI",
            "Possible insulin resistance",
            "Lifestyle factors contributing to metabolic risk",
        ],
        "actions": [
            "Initiate structured dietary modifications (low glycaemic index diet)",
            "Increase physical activity to 150–300 minutes per week",
            "Monitor fasting glucose quarterly",
            "Implement weight-management strategy",
            "Consider dietitian referral for personalised meal planning",
        ],
        "follow_up": [
            "Fasting glucose test – within 1 month",
            "HbA1c test – within 3 months",
            "Weight and BMI monitoring – monthly",
            "Endocrinologist consultation – within 4 weeks",
        ],
        "timeline": "3 months",
    },
    "high": {
        "risk_factors": [
            "Significantly elevated glucose levels",
            "High BMI or obesity",
            "Strong metabolic risk profile",
            "Possible pre-diabetic or early-onset diabetic state",
        ],
        "actions": [
            "Immediate medical evaluation by an Endocrinologist",
            "Daily glucose self-monitoring",
            "Comprehensive confirmatory laboratory testing (OGTT, HbA1c)",
            "Structured lifestyle modification programme",
            "Nutritional therapy and medical nutrition planning",
        ],
        "follow_up": [
            "Urgent Endocrinologist referral – within 2 weeks",
            "Confirmatory blood work – within 1 week",
            "HbA1c test – immediately",
            "Follow-up monitoring – every 4–6 weeks",
        ],
        "timeline": "2–4 weeks",
    },
}


# ── HEART CARE PLANS ──────────────────────────────────────────────────────────

_HEART_PLANS = {
    "low": {
        "risk_factors": [
            "Blood pressure within normal range",
            "No significant arrhythmia indicators",
            "Age-appropriate cardiovascular profile",
        ],
        "actions": [
            "Maintain target blood pressure below 130/80 mmHg",
            "Engage in 150 minutes of moderate aerobic exercise weekly",
            "Follow a heart-healthy diet (DASH or Mediterranean)",
            "Avoid tobacco and limit alcohol consumption",
            "Monitor resting heart rate and blood pressure periodically",
        ],
        "follow_up": [
            "Annual cardiovascular screening",
            "Blood pressure check every 6 months",
            "Lipid profile annually",
        ],
        "timeline": "12 months",
    },
    "moderate": {
        "risk_factors": [
            "Borderline ECG findings",
            "Elevated resting blood pressure",
            "Sub-optimal lipid profile",
        ],
        "actions": [
            "Obtain a resting ECG evaluation",
            "Request a comprehensive lipid profile (LDL, HDL, triglycerides)",
            "Initiate strict blood pressure monitoring (home BP log)",
            "Begin structured dietary modifications",
            "Increase supervised physical activity",
        ],
        "follow_up": [
            "ECG evaluation – within 2 weeks",
            "Lipid profile test – within 1 month",
            "Blood pressure monitoring – bi-weekly",
            "Cardiology consultation – within 4 weeks",
        ],
        "timeline": "4–6 weeks",
    },
    "high": {
        "risk_factors": [
            "Elevated cardiovascular risk across multiple parameters",
            "Possible ischaemic indicators",
            "Significant blood pressure and cholesterol abnormalities",
        ],
        "actions": [
            "Urgent comprehensive cardiovascular evaluation",
            "Stress testing and advanced cardiac imaging if indicated",
            "Multi-factorial risk factor assessment",
            "Immediate lifestyle modification programme",
            "Pharmacological management review by cardiologist",
        ],
        "follow_up": [
            "Cardiologist referral – within 1–2 weeks",
            "Comprehensive cardiovascular panel – immediately",
            "ECG and echocardiogram – within 2 weeks",
            "Follow-up consultation – every 4 weeks",
        ],
        "timeline": "1–2 weeks",
    },
}


# ── SYMPTOM / DIFFERENTIAL CARE PLANS ────────────────────────────────────────

_SYMPTOM_PLANS = {
    "respiratory": {
        "risk_factors": ["Respiratory symptom cluster identified", "Possible airway or pulmonary pathology"],
        "actions": [
            "Pulmonary function evaluation",
            "Chest imaging if clinically indicated",
            "Monitor oxygen saturation",
            "Avoid environmental triggers (smoking, pollutants)",
        ],
        "follow_up": [
            "Pulmonologist consultation – within 2 weeks",
            "Chest X-ray if indicated",
            "Symptom diary monitoring",
        ],
        "timeline": "2 weeks",
    },
    "cardiac": {
        "risk_factors": ["Cardiac symptom patterns detected", "Possible cardiovascular etiology"],
        "actions": [
            "Urgent ECG and cardiac enzyme assessment",
            "Blood pressure and heart rate monitoring",
            "Avoid strenuous physical activity until evaluated",
        ],
        "follow_up": [
            "Cardiologist referral – urgent",
            "ECG – immediately",
            "Troponin and cardiac panel – if indicated",
        ],
        "timeline": "1 week (urgent)",
    },
    "metabolic": {
        "risk_factors": ["Metabolic or endocrine symptom pattern", "Hormonal imbalance indicators"],
        "actions": [
            "Comprehensive metabolic panel",
            "Thyroid function tests",
            "Glucose and insulin level assessment",
            "Dietary and lifestyle modification",
        ],
        "follow_up": [
            "Endocrinologist consultation – within 2 weeks",
            "Blood metabolic panel – within 1 week",
        ],
        "timeline": "2 weeks",
    },
    "neurological": {
        "risk_factors": ["Neurological symptom indicators", "CNS or peripheral nervous system involvement"],
        "actions": [
            "Neurological examination by specialist",
            "MRI or CT imaging if indicated",
            "Medication review for neuro-toxic agents",
        ],
        "follow_up": [
            "Neurology referral – within 2 weeks",
            "Imaging as directed by neurologist",
        ],
        "timeline": "2 weeks",
    },
    "gastroenterological": {
        "risk_factors": ["Gastrointestinal symptom pattern identified", "Possible GI tract pathology"],
        "actions": [
            "Dietary modification and avoidance of trigger foods",
            "Stool analysis if infection suspected",
            "Liver function tests if indicated",
        ],
        "follow_up": [
            "Gastroenterology consultation – within 3 weeks",
            "Relevant laboratory work-up",
        ],
        "timeline": "3 weeks",
    },
    "general": {
        "risk_factors": ["Undifferentiated symptom presentation", "Multiple body systems potentially involved"],
        "actions": [
            "Comprehensive physical examination",
            "Routine blood work (CBC, CMP, urinalysis)",
            "Symptom documentation for follow-up evaluation",
        ],
        "follow_up": [
            "Internal Medicine consultation – within 2 weeks",
            "Baseline laboratory investigations",
        ],
        "timeline": "2 weeks",
    },
}


# ── DRUG INTERACTION CARE PLANS ───────────────────────────────────────────────

_DRUG_PLANS = {
    "low": {
        "risk_factors": ["Minor pharmacokinetic interaction detected", "Clinically manageable at primary care level"],
        "actions": [
            "Review current medication list with prescribing physician",
            "Monitor for any unusual side effects",
            "Maintain medication adherence",
            "Avoid self-adjusting dosages without medical advice",
        ],
        "follow_up": [
            "Pharmacist medication review – at next dispensing",
            "Physician check-in – at next scheduled appointment",
        ],
        "timeline": "Next routine visit",
    },
    "moderate": {
        "risk_factors": [
            "Moderate pharmacodynamic or pharmacokinetic interaction",
            "CYP450 enzyme pathway involvement possible",
        ],
        "actions": [
            "Consult clinical pharmacologist for regimen review",
            "Consider therapeutic drug monitoring (TDM)",
            "Adjust dosing schedule under physician guidance",
            "Monitor organ function (renal, hepatic) as appropriate",
        ],
        "follow_up": [
            "Clinical Pharmacologist consultation – within 2 weeks",
            "Therapeutic drug monitoring – as indicated",
            "Laboratory monitoring – liver and kidney function",
        ],
        "timeline": "2 weeks",
    },
    "high": {
        "risk_factors": [
            "High-severity pharmacological interaction detected",
            "Potential for serious adverse drug reaction",
            "Possible contraindication or toxicity risk",
        ],
        "actions": [
            "Urgent clinical pharmacologist review",
            "Consider immediate medication regimen modification",
            "Implement intensive adverse effect monitoring",
            "Hospital-level monitoring if systemic toxicity suspected",
        ],
        "follow_up": [
            "Urgent Clinical Pharmacologist referral – within 1 week",
            "Immediate laboratory toxicity screening",
            "Emergency evaluation if acute symptoms present",
        ],
        "timeline": "Urgent – 1 week or sooner",
    },
}


# ── Public API ────────────────────────────────────────────────────────────────

def get_diabetes_care_plan(risk_tier: str) -> dict:
    return _DIABETES_PLANS.get(risk_tier, _DIABETES_PLANS["low"])

def get_heart_care_plan(risk_tier: str) -> dict:
    return _HEART_PLANS.get(risk_tier, _HEART_PLANS["low"])

def get_symptom_care_plan(symptom_category: str) -> dict:
    return _SYMPTOM_PLANS.get(symptom_category, _SYMPTOM_PLANS["general"])

def get_drug_care_plan(risk_tier: str) -> dict:
    return _DRUG_PLANS.get(risk_tier, _DRUG_PLANS["low"])
