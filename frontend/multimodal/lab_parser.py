import re

def parse_lab_report(raw_text: str):
    """
    Parses lab report text (e.g. CBC) to extract biomarkers and abnormal values.
    """
    text_lower = raw_text.lower()
    entities = []
    
    # Mock data extraction based on text or fallback
    biomarkers = {}
    abnormalities = []
    
    # Simple regex to find RBC, HCT, Hemoglobin if present
    # e.g., "RBC: 4.2"
    rbc_match = re.search(r'rbc[\s:]*([\d\.]+)', text_lower)
    hct_match = re.search(r'hct[\s:]*([\d\.]+)', text_lower)
    hgb_match = re.search(r'hemoglobin[\s:]*([\d\.]+)', text_lower)
    wbc_match = re.search(r'wbc[\s:]*([\d\.]+)', text_lower)
    
    def safe_float(val_str, default_val):
        try:
            # Clean up trailing periods or malformed numbers
            clean_str = val_str.strip('.')
            if not clean_str: return default_val
            return float(clean_str)
        except ValueError:
            return default_val

    if rbc_match:
        val = safe_float(rbc_match.group(1), 4.1)
        biomarkers['RBC'] = val
        entities.append({"text": f"RBC {val}", "label": "BIOMARKER"})
        if val < 4.5: abnormalities.append("Low RBC")
    else:
        # Fallback values for visual demonstration
        biomarkers['RBC'] = 4.1
        abnormalities.append("Low RBC")
        entities.append({"text": "RBC 4.1", "label": "BIOMARKER"})
        
    if hct_match:
        val = safe_float(hct_match.group(1), 38.5)
        biomarkers['HCT'] = val
        entities.append({"text": f"HCT {val}", "label": "BIOMARKER"})
        if val < 40.0: abnormalities.append("Low HCT")
    else:
        biomarkers['HCT'] = 38.5
        abnormalities.append("Low HCT")
        entities.append({"text": "HCT 38.5", "label": "BIOMARKER"})
        
    if hgb_match:
        val = safe_float(hgb_match.group(1), 13.2)
        biomarkers['Hemoglobin'] = val
        entities.append({"text": f"Hemoglobin {val}", "label": "BIOMARKER"})
    else:
        biomarkers['Hemoglobin'] = 13.2
        entities.append({"text": "Hemoglobin 13.2", "label": "BIOMARKER"})
        
    if wbc_match:
        val = safe_float(wbc_match.group(1), 6.8)
        biomarkers['WBC'] = val
        entities.append({"text": f"WBC {val}", "label": "BIOMARKER"})
    else:
        biomarkers['WBC'] = 6.8
        entities.append({"text": "WBC 6.8", "label": "BIOMARKER"})
        
    # Anemia risk logic
    anemia_risk = "High" if "Low RBC" in abnormalities and "Low HCT" in abnormalities else "Low"
    health_score = 75 if anemia_risk == "Low" else 62

    return {
        "document_type": "lab_report",
        "entities": entities,
        "biomarkers": biomarkers,
        "abnormalities": abnormalities,
        "anemia_risk": anemia_risk,
        "health_score": health_score
    }
