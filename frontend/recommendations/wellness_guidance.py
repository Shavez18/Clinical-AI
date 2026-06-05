"""
wellness_guidance.py
────────────────────────────────────────────────────────────────────────────
Returns wellness tips and lifestyle guidance per module and risk tier.
All content is generic, evidence-based, and does not reference real persons.
"""

from __future__ import annotations


_WELLNESS_DB: dict[str, dict[str, list[dict]]] = {
    "diabetes": {
        "low": [
            {"icon": "🥗", "tip": "Diet",     "detail": "Prioritise whole grains, vegetables, lean proteins, and limit refined sugars."},
            {"icon": "🏃", "tip": "Exercise",  "detail": "Aim for 150 minutes of moderate aerobic activity per week (walking, cycling, swimming)."},
            {"icon": "💤", "tip": "Sleep",     "detail": "Maintain 7–9 hours of quality sleep; poor sleep disrupts glucose metabolism."},
            {"icon": "🧘", "tip": "Stress",    "detail": "Practice mindfulness or deep-breathing exercises to reduce cortisol levels."},
            {"icon": "🚭", "tip": "Lifestyle", "detail": "Avoid tobacco products; smoking significantly elevates diabetes-related complications."},
        ],
        "moderate": [
            {"icon": "📊", "tip": "Monitoring", "detail": "Track fasting glucose regularly; maintain a personal glucose log to identify trends."},
            {"icon": "🥗", "tip": "Nutrition",  "detail": "Adopt a low-glycaemic-index diet; consult a registered dietitian for a personalised plan."},
            {"icon": "🏋️", "tip": "Exercise",   "detail": "Combine aerobic exercise with resistance training for improved insulin sensitivity."},
            {"icon": "⚖️",  "tip": "Weight",    "detail": "A 5–7% reduction in body weight can significantly lower diabetes progression risk."},
            {"icon": "💊",  "tip": "Medical",   "detail": "Discuss preventive medication options (e.g., Metformin) with your endocrinologist."},
        ],
        "high": [
            {"icon": "🚨", "tip": "Priority",    "detail": "Seek immediate medical evaluation; do not delay specialist consultation."},
            {"icon": "📋", "tip": "Testing",     "detail": "Complete all recommended confirmatory tests (HbA1c, OGTT) as soon as possible."},
            {"icon": "🍽️", "tip": "Diet",        "detail": "Follow a medically supervised nutritional plan; restrict all high-sugar and processed foods."},
            {"icon": "📱", "tip": "Tracking",    "detail": "Use a glucose monitoring device and log readings daily to share with your physician."},
            {"icon": "🤝", "tip": "Support",     "detail": "Consider joining a structured diabetes management programme for education and support."},
        ],
    },
    "heart": {
        "low": [
            {"icon": "❤️",  "tip": "Heart Health", "detail": "Maintain blood pressure below 130/80 mmHg through regular monitoring."},
            {"icon": "🏃",  "tip": "Exercise",      "detail": "Engage in moderate cardiovascular exercise for at least 150 minutes weekly."},
            {"icon": "🥑",  "tip": "Nutrition",     "detail": "Adopt a Mediterranean-style diet rich in omega-3 fatty acids and antioxidants."},
            {"icon": "🚭",  "tip": "Smoking",       "detail": "Tobacco cessation is the single most effective cardiovascular preventive measure."},
            {"icon": "🍷",  "tip": "Alcohol",       "detail": "Limit alcohol to no more than 1 unit per day for women, 2 units for men."},
        ],
        "moderate": [
            {"icon": "📏",  "tip": "BP Monitoring", "detail": "Record blood pressure at home twice daily; target below 130/80 mmHg."},
            {"icon": "🧪",  "tip": "Lipid Profile", "detail": "Obtain a fasting lipid panel; target LDL below 100 mg/dL."},
            {"icon": "🏋️",  "tip": "Exercise",      "detail": "Supervised cardiac rehabilitation-style exercise can reduce moderate risk significantly."},
            {"icon": "🧂",  "tip": "Sodium",        "detail": "Restrict sodium intake to under 2,300 mg/day to support blood pressure control."},
            {"icon": "💤",  "tip": "Sleep",         "detail": "Address sleep apnoea if suspected; it is a major modifiable cardiac risk factor."},
        ],
        "high": [
            {"icon": "🚨",  "tip": "Urgent Care",  "detail": "Do not ignore chest pain, shortness of breath, or palpitations — seek immediate evaluation."},
            {"icon": "💊",  "tip": "Medication",   "detail": "Adhere strictly to any prescribed antihypertensives, statins, or antiplatelet agents."},
            {"icon": "📊",  "tip": "Monitoring",   "detail": "Daily blood pressure and heart rate logging is essential at this risk level."},
            {"icon": "🥗",  "tip": "Diet",         "detail": "Follow a cardiologist-approved dietary plan with strict sodium and saturated fat restriction."},
            {"icon": "🤝",  "tip": "Support",      "detail": "Enrol in a structured cardiac risk reduction programme with multi-disciplinary support."},
        ],
    },
    "drug": {
        "low": [
            {"icon": "📋", "tip": "Medication List",  "detail": "Keep an updated list of all medications, including over-the-counter drugs and supplements."},
            {"icon": "⏰", "tip": "Adherence",        "detail": "Take medications at the prescribed time to maintain consistent therapeutic levels."},
            {"icon": "🍽️", "tip": "Food Interactions","detail": "Ask your pharmacist about any food–drug interactions relevant to your regimen."},
        ],
        "moderate": [
            {"icon": "🔬", "tip": "Drug Monitoring",  "detail": "Request therapeutic drug monitoring if your regimen includes narrow therapeutic index drugs."},
            {"icon": "📊", "tip": "Lab Tests",        "detail": "Regular liver and kidney function tests can detect early signs of drug-induced organ stress."},
            {"icon": "🚫", "tip": "Self-medicating",  "detail": "Do not add over-the-counter medications without consulting your pharmacist or physician."},
            {"icon": "📋", "tip": "Reconciliation",   "detail": "Medication reconciliation by a clinical pharmacologist is strongly recommended."},
        ],
        "high": [
            {"icon": "🚨", "tip": "Urgent Review",   "detail": "High-severity interactions require immediate pharmacological review and possible regimen change."},
            {"icon": "🏥", "tip": "Hospitalisation", "detail": "If systemic toxicity symptoms appear (confusion, arrhythmia, severe nausea), seek emergency care."},
            {"icon": "💊", "tip": "Alternatives",    "detail": "Request clinically safe therapeutic alternatives from your clinical pharmacologist."},
            {"icon": "📱", "tip": "Symptom Watch",   "detail": "Monitor for new symptoms daily and report any changes to your healthcare team immediately."},
        ],
    },
}


def get_wellness_guidance(module: str, risk_tier: str) -> list[dict]:
    """
    Parameters
    ----------
    module    : 'diabetes' | 'heart' | 'drug'
    risk_tier : 'low' | 'moderate' | 'high'

    Returns
    -------
    List of wellness tip dicts: [{"icon", "tip", "detail"}, ...]
    """
    return _WELLNESS_DB.get(module, {}).get(risk_tier, [])
