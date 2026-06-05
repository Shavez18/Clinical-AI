"""
Lab Report Assistant Module.
Explains common lab tests including CBC, Glucose, Cholesterol, Liver, Kidney, and Thyroid panels.
"""

LAB_EXPLANATIONS = {
    "cbc": {
        "name": "Complete Blood Count (CBC)",
        "summary": "Measures cells in your blood to evaluate general health and detect conditions like anemia or infection.",
        "components": [
            ("RBC (Red Blood Cells)", "4.5 - 5.9 M/uL (Men), 4.1 - 5.1 M/uL (Women)", "Carry oxygen throughout your body. Low counts indicate anemia, leading to fatigue and weakness."),
            ("WBC (White Blood Cells)", "4.5 - 11.0 K/uL", "Combat infections and diseases. Elevated counts indicate active infections or inflammatory responses. Low counts suggest immunocompromise."),
            ("Hemoglobin (Hgb)", "13.5 - 17.5 g/dL (Men), 12.0 - 15.5 g/dL (Women)", "The protein in red blood cells that binds oxygen. Parallels RBC count findings."),
            ("Hematocrit (Hct)", "41% - 50% (Men), 36% - 48% (Women)", "The percentage of blood volume made of red blood cells. Elevated indicates dehydration; low indicates anemia or bleeding."),
            ("Platelets", "150 - 450 K/uL", "Crucial for blood clotting. Low counts (thrombocytopenia) lead to bruising and bleeding risks; high counts can lead to clotting risk.")
        ]
    },
    "liver": {
        "name": "Liver Function Panel",
        "summary": "Assesses how well your liver is functioning by measuring enzymes, proteins, and bilirubin levels.",
        "components": [
            ("ALT (Alanine Aminotransferase)", "7 - 56 U/L", "An enzyme found mainly in the liver. Elevated ALT indicates liver cell damage (hepatitis, fatty liver)."),
            ("AST (Aspartate Aminotransferase)", "10 - 40 U/L", "An enzyme found in liver, heart, and muscle. Elevated AST combined with ALT helps evaluate hepatic injury."),
            ("Albumin", "3.4 - 5.4 g/dL", "A protein synthesized by the liver. Low levels suggest chronic liver disease, kidney malfunction, or malnutrition."),
            ("Bilirubin (Total)", "0.1 - 1.2 mg/dL", "A waste product from old RBC breakdown. High levels cause jaundice (yellow skin/eyes) and suggest biliary blockage or liver dysfunction.")
        ]
    },
    "kidney": {
        "name": "Kidney Function Panel",
        "summary": "Measures waste products to evaluate how efficiently your kidneys are filtering blood.",
        "components": [
            ("Creatinine", "0.6 - 1.2 mg/dL (Men), 0.5 - 1.1 mg/dL (Women)", "A waste product from muscle breakdown. Elevated creatinine indicates reduced glomerular filtration capacity."),
            ("eGFR (Estimated Glomerular Filtration Rate)", ">= 90 mL/min/1.73m²", "Calculates kidney filtration efficiency. Values < 60 suggest kidney dysfunction or chronic kidney disease (CKD)."),
            ("BUN (Blood Urea Nitrogen)", "7 - 20 mg/dL", "Urea waste from protein metabolism. High values indicate renal impairment, dehydration, or high protein diets.")
        ]
    },
    "thyroid": {
        "name": "Thyroid Panel",
        "summary": "Evaluates thyroid gland activity and metabolic regulation.",
        "components": [
            ("TSH (Thyroid Stimulating Hormone)", "0.4 - 4.0 mIU/L", "Pituitary hormone that stimulates the thyroid. High TSH indicates Hypothyroidism (underactive thyroid); low TSH indicates Hyperthyroidism (overactive thyroid)."),
            ("Free T4 (Thyroxine)", "0.9 - 1.7 ng/dL", "The main active hormone produced directly by the thyroid. Correlates with TSH to verify gland function."),
            ("Free T3 (Triiodothyronine)", "2.3 - 4.2 pg/mL", "The highly active thyroid hormone metabolized from T4. Helps evaluate hyperthyroid details.")
        ]
    }
}

def explain_lab_report(query: str) -> str:
    """
    Identifies lab test inquiries and returns standard clinical summaries and reference tables.
    """
    q = query.lower()
    matches = []
    
    # Check if a specific panel is queried
    for key, data in LAB_EXPLANATIONS.items():
        if key in q or (key == "cbc" and "complete blood count" in q) or (key == "liver" and "hepatic" in q) or (key == "kidney" and ("renal" in q or "creatinine" in q)) or (key == "thyroid" and "tsh" in q):
            comp_rows = ""
            for name, range_val, desc in data["components"]:
                comp_rows += f"| **{name}** | {range_val} | {desc} |\n"
                
            matches.append(
                f"### 📋 Reference Standards: {data['name']}\n"
                f"*{data['summary']}*\n\n"
                f"| Biomarker | Reference Range | Clinical Significance |\n"
                f"| :--- | :--- | :--- |\n"
                f"{comp_rows}"
            )
            
    if matches:
        return "\n\n".join(matches)
        
    return (
        "I can explain lab report metrics. Please specify a panel: "
        "**CBC (Complete Blood Count)**, **Liver Function Panel**, **Kidney / Renal Function Panel**, or **Thyroid Panel (TSH)**."
    )

def explain_parsed_ocr_report(ocr_result: dict) -> str:
    """
    Summarizes parsed OCR lab report results (biomarkers and abnormalities).
    """
    doc_type = ocr_result.get("document_type", "")
    if doc_type != "lab_report":
        return "The uploaded document is not classified as a laboratory report. I can only interpret lab biomarkers like CBC values."
        
    biomarkers = ocr_result.get("biomarkers", {})
    abnormalities = ocr_result.get("abnormalities", [])
    
    summary = "### ⚕️ OCR Lab Report Summary:\n"
    if abnormalities:
        summary += f"⚠️ **Abnormalities Detected:** {', '.join(abnormalities)}\n\n"
    else:
        summary += "✅ **No major abnormalities detected.** All values appear within standard limits.\n\n"
        
    summary += "#### Extracted Telemetry Values:\n"
    for k, v in biomarkers.items():
        ref_text = ""
        # Provide simple range reference if known
        if k == "RBC": ref_text = " (Ref: 4.1 - 5.9 M/uL)"
        elif k == "HCT": ref_text = " (Ref: 36% - 50%)"
        elif k == "WBC": ref_text = " (Ref: 4.5 - 11.0 K/uL)"
        elif k == "Hemoglobin": ref_text = " (Ref: 12.0 - 17.5 g/dL)"
        
        status = "🔴" if any(k in a for a in abnormalities) else "🟢"
        summary += f"- {status} **{k}:** {v}{ref_text}\n"
        
    summary += "\n**Clinical Explanations:**\n"
    for abnormal in abnormalities:
        if "RBC" in abnormal or "HCT" in abnormal:
            summary += "- **Anemia / Fatigue Correlation:** Low RBC and/or Hematocrit indicates lower oxygen transport. This frequently correlates with patient reports of fatigue, shortness of breath, or weakness.\n"
        elif "WBC" in abnormal:
            summary += "- **Immune Response:** Abnormal WBC points to possible infection, inflammation, or immune strain.\n"
            
    summary += "\n*Note: Simulated OCR findings. Please review physical documents to confirm exact digital transcription.*"
    return summary
