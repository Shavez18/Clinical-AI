"""
Cholesterol Interpreter Engine.
Analyzes lipid panel values (Total Cholesterol, LDL, HDL, Triglycerides) and provides clinical feedback.
"""
from utils.health_ranges import interpret_cholesterol

def analyze_cholesterol(total: float, ldl: float, hdl: float, trig: float, gender: str = "Male") -> dict:
    """
    Analyzes lipid panel parameters and returns interpretations, visual grids, and health tips.
    """
    res = interpret_cholesterol(total, ldl, hdl, trig, gender)
    
    # Check if any values are flagged as High or Low (unfavorable)
    warnings = []
    recommendations = []
    
    if res["total"]["category"] in ["Borderline High", "High"]:
        warnings.append("Elevated Total Cholesterol.")
        recommendations.append("Limit saturated and trans fats. Increase dietary fiber intake (oats, legumes, fruits).")
        
    if res["ldl"]["category"] in ["Borderline High", "High", "Very High"]:
        warnings.append("Elevated LDL ('bad') cholesterol.")
        recommendations.append("Incorporate foods rich in omega-3 fatty acids (salmon, walnuts, flaxseeds). Consider consulting a doctor regarding statin therapy if levels remain high.")
        
    if res["hdl"]["category"] == "Low (Unfavorable)":
        warnings.append("Low HDL ('good') cholesterol.")
        recommendations.append("Participate in regular aerobic exercise (e.g. brisk walking 30 mins daily). Avoid smoking.")
        
    if res["trig"]["category"] in ["Borderline High", "High", "Very High"]:
        warnings.append("Elevated Triglycerides.")
        recommendations.append("Reduce consumption of simple sugars, alcohol, and refined carbohydrates. Weight loss can significantly lower triglycerides.")

    if not warnings:
        warnings.append("All lipid biomarkers are in optimal ranges.")
        recommendations.append("Maintain your current healthy balanced diet and active lifestyle. Excellent work!")

    # Build HTML Visual Table/Grid
    grid_html = f"""
    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 16px; padding: 1.25rem; margin: 1rem 0; font-family: 'DM Sans', sans-serif;">
        <table style="width:100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #6b8aab; text-transform: uppercase;">
                    <th style="padding: 0.75rem 0.5rem;">Biomarker</th>
                    <th style="padding: 0.75rem 0.5rem; text-align: right;">Value</th>
                    <th style="padding: 0.75rem 0.5rem; text-align: center;">Classification</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <td style="padding: 0.75rem 0.5rem; font-weight: 600;">Total Cholesterol</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: right; font-family: 'DM Mono', monospace; color: {res['total']['color']}; font-weight: 700;">{total} mg/dL</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: center;"><span style="color: {res['total']['color']}; font-weight: 600; font-size:0.8rem; background:{res['total']['color']}15; padding: 0.2rem 0.6rem; border-radius: 8px; border: 1px solid {res['total']['color']}33;">{res['total']['category']}</span></td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <td style="padding: 0.75rem 0.5rem; font-weight: 600;">LDL (Bad)</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: right; font-family: 'DM Mono', monospace; color: {res['ldl']['color']}; font-weight: 700;">{ldl} mg/dL</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: center;"><span style="color: {res['ldl']['color']}; font-weight: 600; font-size:0.8rem; background:{res['ldl']['color']}15; padding: 0.2rem 0.6rem; border-radius: 8px; border: 1px solid {res['ldl']['color']}33;">{res['ldl']['category']}</span></td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <td style="padding: 0.75rem 0.5rem; font-weight: 600;">HDL (Good)</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: right; font-family: 'DM Mono', monospace; color: {res['hdl']['color']}; font-weight: 700;">{hdl} mg/dL</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: center;"><span style="color: {res['hdl']['color']}; font-weight: 600; font-size:0.8rem; background:{res['hdl']['color']}15; padding: 0.2rem 0.6rem; border-radius: 8px; border: 1px solid {res['hdl']['color']}33;">{res['hdl']['category']}</span></td>
                </tr>
                <tr>
                    <td style="padding: 0.75rem 0.5rem; font-weight: 600;">Triglycerides</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: right; font-family: 'DM Mono', monospace; color: {res['trig']['color']}; font-weight: 700;">{trig} mg/dL</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: center;"><span style="color: {res['trig']['color']}; font-weight: 600; font-size:0.8rem; background:{res['trig']['color']}15; padding: 0.2rem 0.6rem; border-radius: 8px; border: 1px solid {res['trig']['color']}33;">{res['trig']['category']}</span></td>
                </tr>
            </tbody>
        </table>
    </div>
    """

    return {
        "raw_interpretations": res,
        "warnings": warnings,
        "recommendations": recommendations,
        "grid_html": grid_html
    }
