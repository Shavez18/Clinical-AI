import time

def generate_ai_clinical_summary(context_data):
    """
    Generates a futuristic AI-driven clinical summary based on multimodal inputs.
    """
    time.sleep(2.0) # Simulate LLM generation time
    
    # Extract details safely
    risk_level = context_data.get("risk_level", "Moderate")
    key_findings = context_data.get("findings", [])
    
    findings_html = "".join([f"<li>{f}</li>" for f in key_findings]) if key_findings else "<li>No critical findings reported.</li>"
    
    summary = f"""
    <div style="font-family: 'DM Sans', sans-serif; color: #e2e8f0; line-height: 1.6; font-size: 0.95rem;">
        <p>Based on the multimodal analysis of the provided clinical documents and symptom reports, the patient presents a <strong>{risk_level}</strong> risk profile.</p>
        <p><strong>Key AI Observations:</strong></p>
        <ul style="color: #0dfddb;">
            {findings_html}
        </ul>
        <p><em>Recommendation:</em> Correlate these AI-extracted findings with clinical judgment. Consider ordering standard metabolic panels and following up on the reported symptoms.</p>
    </div>
    """
    
    return summary
