"""
Blood Pressure Interpreter Engine.
Analyzes blood pressure metrics and provides clinical classifications and recommendations.
"""
from utils.health_ranges import interpret_blood_pressure

def analyze_blood_pressure(systolic: float, diastolic: float) -> dict:
    """
    Analyzes systolic and diastolic blood pressure values and returns category, details, and recommendations.
    """
    res = interpret_blood_pressure(systolic, diastolic)
    category = res["category"]
    interpretation = res["interpretation"]
    color = res["color"]
    
    # Custom guidelines based on classification
    guidelines = []
    if category == "Normal":
        guidelines.append("Optimal vascular health. Maintain a low-sodium diet and active lifestyle to sustain these numbers.")
    elif category == "Elevated Blood Pressure":
        guidelines.append("Reassess in 3-6 months. Focus on weight loss, physical activity, dietary changes (DASH diet), and reducing alcohol intake.")
    elif category == "Stage 1 Hypertension":
        guidelines.append("Initiate lifestyle modifications. Assess 10-year cardiovascular risk; if high, pharmacotherapy may be considered by your physician.")
    elif category == "Stage 2 Hypertension":
        guidelines.append("Requires prompt medical evaluation. Lifestyle modifications plus a combination of blood pressure lowering medications are typically indicated.")
    elif category == "Hypertensive Crisis":
        guidelines.append("URGENT: Re-measure immediately. If numbers remain above 180/120 mmHg, seek immediate emergency medical care.")
        
    visual_html = f"""
    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 16px; padding: 1.25rem; margin: 1rem 0; font-family: 'DM Sans', sans-serif; text-align: center;">
        <div style="font-size: 0.72rem; font-family: 'DM Mono', monospace; color: #6b8aab; text-transform: uppercase; margin-bottom: 0.5rem;">VITAL TELEMETRY</div>
        <div style="display: flex; justify-content: center; gap: 2rem; align-items: center; margin-bottom: 1rem;">
            <div>
                <div style="font-family: 'Fraunces', serif; font-size: 2.2rem; font-weight: 700; color: {color}; text-shadow: 0 0 10px {color}33;">{int(systolic)}</div>
                <div style="font-size: 0.65rem; color: #6b8aab; font-family: 'DM Mono', monospace; text-transform: uppercase;">Systolic (mmHg)</div>
            </div>
            <div style="font-family: 'Fraunces', serif; font-size: 2rem; color: #6b8aab;">/</div>
            <div>
                <div style="font-family: 'Fraunces', serif; font-size: 2.2rem; font-weight: 700; color: {color}; text-shadow: 0 0 10px {color}33;">{int(diastolic)}</div>
                <div style="font-size: 0.65rem; color: #6b8aab; font-family: 'DM Mono', monospace; text-transform: uppercase;">Diastolic (mmHg)</div>
            </div>
        </div>
        <div style="display: inline-block; color: {color}; font-weight: 600; font-size:0.85rem; background:{color}15; padding: 0.3rem 0.8rem; border-radius: 10px; border: 1px solid {color}33; text-transform: uppercase;">
            {category}
        </div>
    </div>
    """
    
    return {
        "systolic": systolic,
        "diastolic": diastolic,
        "category": category,
        "interpretation": interpretation,
        "color": color,
        "guidelines": guidelines,
        "visual_html": visual_html
    }
