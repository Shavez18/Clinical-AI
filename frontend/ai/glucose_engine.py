"""
Glucose Interpreter Engine.
Interprets glucose levels and generates visual and textual clinical explanations.
"""
from utils.health_ranges import interpret_glucose

def analyze_glucose(value: float) -> dict:
    """
    Analyzes fasting glucose and builds a detailed explanation and HSL visual slider bar.
    """
    res = interpret_glucose(value)
    category = res["category"]
    interpretation = res["interpretation"]
    color = res["color"]
    
    # Calculate percentage for visual indicator (capped between 40 and 200 for rendering)
    min_val, max_val = 40.0, 200.0
    percentage = ((value - min_val) / (max_val - min_val)) * 100.0
    percentage = max(0.0, min(100.0, percentage))
    
    # Build HTML Visual Gauge / Slider
    visual_html = f"""
    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 12px; padding: 1rem; margin: 1rem 0; font-family: 'DM Sans', sans-serif;">
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #6b8aab; font-family: 'DM Mono', monospace; margin-bottom: 0.5rem;">
            <span>Hypoglycemia (&lt;70)</span>
            <span>Normal (70-99)</span>
            <span>Prediabetes (100-125)</span>
            <span>Diabetes (&ge;126)</span>
        </div>
        <div style="position: relative; height: 10px; background: linear-gradient(90deg, #ff003c 0%, #ff003c 15%, #00f2ff 15%, #00f2ff 45%, #ff9d00 45%, #ff9d00 65%, #ff003c 65%, #ff003c 100%); border-radius: 5px; width: 100%;">
            <div style="position: absolute; left: {percentage}%; top: -6px; transform: translateX(-50%); width: 22px; height: 22px; border-radius: 50%; background: #ffffff; border: 4px solid {color}; box-shadow: 0 0 10px {color};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #6b8aab; font-family: 'DM Mono', monospace; margin-top: 0.5rem;">
            <span>40 mg/dL</span>
            <span>70 mg/dL</span>
            <span>100 mg/dL</span>
            <span>126 mg/dL</span>
            <span>200+ mg/dL</span>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <span style="font-size: 1.5rem; font-weight: 700; color: {color}; text-shadow: 0 0 10px {color}33;">{value} mg/dL</span>
            <span style="display: block; font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #f0f6ff; text-transform: uppercase; margin-top: 0.25rem;">Current Classification: <strong>{category}</strong></span>
        </div>
    </div>
    """
    
    return {
        "value": value,
        "category": category,
        "interpretation": interpretation,
        "color": color,
        "visual_html": visual_html
    }
