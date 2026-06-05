def classify_document(raw_text: str, filename: str = "") -> str:
    """
    Classifies the uploaded document based on text content and filename heuristics.
    Returns: 'lab_report', 'prescription', or 'clinical_note'
    """
    text_lower = raw_text.lower()
    filename_lower = filename.lower()
    
    # Heuristics for Lab Reports (e.g. CBC)
    lab_keywords = ['cbc', 'complete blood count', 'hemoglobin', 'hct', 'rbc', 'wbc', 'platelets', 'laboratory', 'test results', 'biomarker', 'reference range']
    if any(kw in text_lower for kw in lab_keywords) or 'lab' in filename_lower:
        return 'lab_report'
        
    # Heuristics for Prescriptions
    prescription_keywords = ['rx', 'prescription', 'take', 'po', 'qhs', 'mg', 'tablet', 'pharmacy', 'refill', 'medication']
    if any(kw in text_lower for kw in prescription_keywords) or 'prescription' in filename_lower or 'rx' in filename_lower:
        return 'prescription'
        
    # Default fallback
    return 'clinical_note'
