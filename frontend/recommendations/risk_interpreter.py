"""
risk_interpreter.py
────────────────────────────────────────────────────────────────────────────
Non-destructive helper: reads prediction outputs only, never modifies them.
Converts raw risk scores / category strings into a structured risk tier dict.
"""

from __future__ import annotations


# ── Risk thresholds (read-only constants) ─────────────────────────────────────
_LOW_MAX      = 30   # <= 30 → Low
_MODERATE_MAX = 70   # 31–70 → Moderate


def interpret_risk_score(risk_percent: float) -> dict:
    """
    Parameters
    ----------
    risk_percent : float   (0–100)

    Returns
    -------
    dict with keys: tier, label, color, bg_color, emoji
    """
    if risk_percent <= _LOW_MAX:
        return {
            "tier":     "low",
            "label":    "Low Risk",
            "color":    "#22c55e",          # green-500
            "bg_color": "rgba(34,197,94,0.10)",
            "border":   "rgba(34,197,94,0.30)",
            "emoji":    "🟢",
        }
    elif risk_percent <= _MODERATE_MAX:
        return {
            "tier":     "moderate",
            "label":    "Moderate Risk",
            "color":    "#f59e0b",          # amber-400
            "bg_color": "rgba(245,158,11,0.10)",
            "border":   "rgba(245,158,11,0.30)",
            "emoji":    "🟡",
        }
    else:
        return {
            "tier":     "high",
            "label":    "High Risk",
            "color":    "#ef4444",          # red-500
            "bg_color": "rgba(239,68,68,0.10)",
            "border":   "rgba(239,68,68,0.30)",
            "emoji":    "🔴",
        }


def interpret_risk_category(category_str: str) -> dict:
    """
    Accepts category strings produced by existing dashboards
    ('LOW RISK', 'MODERATE RISK', 'HIGH RISK') and returns the same
    structured dict as interpret_risk_score().
    """
    cat = category_str.upper().strip()
    if "LOW" in cat:
        return interpret_risk_score(0.0)        # representative low value
    elif "MODERATE" in cat:
        return interpret_risk_score(50.0)
    else:
        return interpret_risk_score(100.0)


def interpret_drug_severity(toxicity_score: float) -> dict:
    """
    Converts drug toxicity score (0–10) to a risk tier for drug interactions.
    """
    if toxicity_score < 3.5:
        return {
            "tier":     "low",
            "label":    "Low Severity",
            "color":    "#22c55e",
            "bg_color": "rgba(34,197,94,0.10)",
            "border":   "rgba(34,197,94,0.30)",
            "emoji":    "🟢",
        }
    elif toxicity_score < 6.5:
        return {
            "tier":     "moderate",
            "label":    "Moderate Severity",
            "color":    "#f59e0b",
            "bg_color": "rgba(245,158,11,0.10)",
            "border":   "rgba(245,158,11,0.30)",
            "emoji":    "🟡",
        }
    else:
        return {
            "tier":     "high",
            "label":    "High Severity",
            "color":    "#ef4444",
            "bg_color": "rgba(239,68,68,0.10)",
            "border":   "rgba(239,68,68,0.30)",
            "emoji":    "🔴",
        }


def classify_symptom_category(top_diagnosis: str) -> str:
    """
    Maps a differential diagnosis label to a broad symptom category
    used by the specialist recommender.
    """
    text = top_diagnosis.lower()
    respiratory_keywords = ["asthma", "pneumonia", "bronchitis", "copd", "tuberculosis",
                            "lung", "respiratory", "pleural", "cough", "dyspnea"]
    cardiac_keywords     = ["heart", "cardiac", "angina", "myocardial", "coronary",
                            "arrhythmia", "palpitation", "hypertension", "cardiovascular"]
    metabolic_keywords   = ["diabetes", "thyroid", "metabolic", "obesity", "glucose",
                            "insulin", "endocrine", "hormonal"]
    neuro_keywords       = ["migraine", "headache", "seizure", "epilepsy", "neuro",
                            "stroke", "vertigo", "dementia", "parkinson"]
    gastro_keywords      = ["gastritis", "ulcer", "ibs", "crohn", "colitis", "liver",
                            "hepatitis", "gastro", "bowel", "colon", "reflux", "gerd"]

    if any(k in text for k in respiratory_keywords):
        return "respiratory"
    if any(k in text for k in cardiac_keywords):
        return "cardiac"
    if any(k in text for k in metabolic_keywords):
        return "metabolic"
    if any(k in text for k in neuro_keywords):
        return "neurological"
    if any(k in text for k in gastro_keywords):
        return "gastroenterological"
    return "general"
