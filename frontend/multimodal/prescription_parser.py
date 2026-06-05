import re

def parse_prescription(raw_text: str):
    """
    Parses prescription text to extract medications, dosages, and symptoms.
    """
    text_lower = raw_text.lower()
    
    # Simple heuristic extraction
    entities = []
    medications = []
    symptoms = []
    
    # Common medications lookup
    common_meds = ['lisinopril', 'atorvastatin', 'metformin', 'amoxicillin', 'ibuprofen', 'omeprazole', 'albuterol', 'gabapentin', 'losartan']
    for med in common_meds:
        if med in text_lower:
            entities.append({"text": med.capitalize(), "label": "MEDICATION"})
            medications.append(med.capitalize())
            
    # Common symptoms/diagnoses lookup
    common_symptoms = ['hypertension', 'hyperlipidemia', 'headache', 'fever', 'cough', 'nausea', 'diabetes', 'pain']
    for sym in common_symptoms:
        if sym in text_lower:
            entities.append({"text": sym.capitalize(), "label": "DIAGNOSIS"})
            symptoms.append(sym.capitalize())
            
    # Fallback if nothing found
    if not entities:
        entities = [
            {"text": "Unknown Medication", "label": "MEDICATION"},
            {"text": "Unknown Condition", "label": "DIAGNOSIS"}
        ]
        
    return {
        "document_type": "prescription",
        "entities": entities,
        "medications": medications,
        "symptoms": symptoms,
        "risk_level": "Moderate" if 'hypertension' in text_lower else "Low"
    }
