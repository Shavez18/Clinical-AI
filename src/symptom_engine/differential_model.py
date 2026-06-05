import os
import joblib
import json
import logging
import numpy as np
from src.symptom_engine.disease_rules import DISEASE_RULES, SYMPTOM_WEIGHTS, CONTEXT_RULES

# Configure basic logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ClinicalEngine")

# Load artifacts
_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
try:
    _model = joblib.load(os.path.join(_BASE, "differential_model.pkl"))
    _vectorizer = joblib.load(os.path.join(_BASE, "clinical_vectorizer.pkl"))
except Exception as e:
    logger.error(f"Models not found or failed to load. Setup error: {str(e)}")
    _model = None
    _vectorizer = None

class DifferentialEngine:
    def __init__(self):
        self.model = _model
        self.vectorizer = _vectorizer
        self.disease_rules = DISEASE_RULES
        self.context_rules = CONTEXT_RULES
        
        self.demographic_rules = {
            "Pregnancy": {"gender": "Female", "weight_if_wrong_gender": 0.0},
            "Prostate Cancer": {"gender": "Male", "weight_if_wrong_gender": 0.0},
        }

    def _calculate_rule_score(self, disease: str, parsed_symptoms: dict) -> float:
        text = parsed_symptoms.get("clean_text", "").lower()
        patient_symptoms = set(parsed_symptoms.get("raw_symptoms_list", []))
        
        score = 0.0
        rule = self.disease_rules.get(disease, {})
        if not rule: return 0.0

        # Required Symptoms
        required_list = rule.get("required", [])
        if required_list:
            for req in required_list:
                if req in patient_symptoms or req in text:
                    score += 0.5
                    if score >= 0.7: break
        
        # Supporting Symptoms
        for supp in rule.get("supporting", []):
            if supp in patient_symptoms or supp in text:
                score += 0.2

        return min(1.0, score)

    def predict_differentials(self, parsed_symptoms: dict, age: int = 30, gender: str = "Unknown", top_n: int = 5):
        if not self.model or not self.vectorizer:
            return [{"disease": "System Error", "probability_percentage": 0, "confidence": "Low", "rationale": "Models not loaded."}]
            
        clean_text = parsed_symptoms.get("clean_text", "")
        if not clean_text: return []

        logger.info(f"--- \U0001fa7a DIAGNOSIS INFERENCE ---")
        
        # 1. ML Engine
        vec = self.vectorizer.transform([clean_text])
        probabilities = self.model.predict_proba(vec)[0]
        classes = self.model.classes_

        combined_results = []
        patient_symptoms = set(parsed_symptoms.get("raw_symptoms_list", []))
        negated_symptoms = set(parsed_symptoms.get("negated_symptoms", []))
        context_features = parsed_symptoms.get("context_features", [])
        
        for i, disease in enumerate(classes):
            ml_score = float(probabilities[i])
            rule_score = self._calculate_rule_score(disease, parsed_symptoms)
            
            # Hybrid
            final_prob = (0.6 * ml_score) + (0.4 * rule_score)
            rule = self.disease_rules.get(disease, {})
            
            # STRICT FILTERING
            # A. Required Symptom Missing -> PRUNE
            required_list = rule.get("required", [])
            has_required = any(req in patient_symptoms or req in clean_text for req in required_list)
            if required_list and not has_required:
                continue

            # B. Context Bonus
            ctx_rule = self.context_rules.get(disease)
            if ctx_rule:
                for ctx in context_features:
                    if any(kw in ctx.lower() for kw in ctx_rule["keywords"]):
                        final_prob += ctx_rule["bonus"]
                        break

            # C. Demographic Adjustment
            demo_rule = self.demographic_rules.get(disease)
            if demo_rule and gender != "Unknown":
                if demo_rule.get("gender") and gender != demo_rule["gender"]:
                    continue

            # D. Age-based Risk Adjustment
            if age > 55 and disease in ["Heart attack", "Stroke", "Hypertension "]:
                final_prob += 0.15
            if age < 15 and disease == "Chicken pox":
                final_prob += 0.2

            if final_prob > 0.05:
                combined_results.append({"disease": disease, "probability": final_prob})

        # 2. Emergency Overrides
        emergency_flags = parsed_symptoms.get("flags", [])
        if emergency_flags:
            # Escalation logic for confirmed multiple critical flags
            escalate_list = ["Heart attack", "Stroke"]
            for res in combined_results:
                if res["disease"] in escalate_list:
                    res["probability"] *= 2.0
                    res["is_emergency"] = True

        # 3. Normalization & Calibration
        total_prob = sum(res["probability"] for res in combined_results)
        if total_prob == 0: return []

        for res in combined_results:
            res["probability"] /= total_prob
            
            # Generic dominance cap
            max_weight = parsed_symptoms.get("max_symptom_weight", 0)
            if max_weight <= 3: res["probability"] = min(0.30, res["probability"])
            
            if res.get("is_emergency"):
                 res["probability"] = min(0.99, max(0.81, res["probability"]))
            else:
                 res["probability"] = min(0.95, res["probability"])

        combined_results.sort(key=lambda x: x["probability"], reverse=True)
        top_results = combined_results[:top_n]
        
        final_differentials = []
        for res in top_results:
            prob_pct = round(res["probability"] * 100, 1)
            confidence = "High" if prob_pct >= 70 else "Medium" if prob_pct >= 40 else "Low"
            
            final_differentials.append({
                "disease": res["disease"],
                "probability_percentage": prob_pct,
                "confidence": confidence,
                "rationale": self._generate_rationale(res["disease"], parsed_symptoms)
            })
            
        return final_differentials

    def _generate_rationale(self, disease, parsed_symptoms):
        text = parsed_symptoms.get("clean_text", "").lower()
        patient_symptoms = set(parsed_symptoms.get("raw_symptoms_list", []))
        rule = self.disease_rules.get(disease, {})
        
        matched_req = [r.capitalize() for r in rule.get("required", []) if r in patient_symptoms or r in text]
        matched_supp = [s.capitalize() for s in rule.get("supporting", []) if s in patient_symptoms or s in text]
        
        reasoning = []
        if matched_req: reasoning.append(f"Matching core indicators: {', '.join(matched_req)}.")
        if matched_supp: reasoning.append(f"Supporting clinical evidence: {', '.join(matched_supp)}.")
        
        if not reasoning:
            reasoning.append(f"Statistical correlation with current symptom profile for {disease}.")
            
        return " ".join(reasoning)

differential_engine = DifferentialEngine()
