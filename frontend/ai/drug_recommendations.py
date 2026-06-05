import streamlit as st

def generate_ai_explanation(interaction):
    """Generates an AI-driven explanation for a specific interaction."""
    pair = " and ".join(interaction.get("drug_pair", []))
    mech = interaction.get("mechanism", "").lower()
    sev = interaction.get("severity", "").lower()
    
    explanation = ""
    if "cyp" in mech:
        explanation = f"**CYP450 Pathway Competition:** {pair.title()} both rely on the Cytochrome P450 enzyme system in the liver for clearance. This creates competitive inhibition, potentially leading to toxic accumulation of one or both agents."
    elif "qt" in mech or "arrhythmia" in mech:
        explanation = f"**Synergistic Cardiotoxicity:** Co-administration of {pair.title()} significantly increases the risk of QT interval prolongation, a dangerous electrical disturbance in the heart that can lead to Torsades de Pointes."
    elif "bleeding" in mech or "anticoag" in mech:
        explanation = f"**Hemostatic Compromise:** The combination of {pair.title()} exerts a compounded effect on blood coagulation pathways, exponentially increasing the risk of major gastrointestinal or intracranial bleeding events."
    else:
        explanation = f"**Pharmacodynamic Synergy/Antagonism:** The interaction between {pair.title()} ({sev} severity) alters the expected therapeutic index, either through direct receptor competition or overlapping systemic effects."
        
    return explanation

def get_clinical_recommendations(interactions):
    """Provides general clinical recommendations based on the interactions profile."""
    has_major = any(i.get("severity", "").lower() == "major" for i in interactions)
    has_moderate = any(i.get("severity", "").lower() == "moderate" for i in interactions)
    
    recs = []
    if has_major:
        recs.append(("🚨 Contraindication Alert", "Consider immediate discontinuation or substitution of the interacting agents. If co-administration is absolutely necessary, admit patient for continuous telemetry and laboratory monitoring."))
        recs.append(("💉 Alternative Therapy", "Consult clinical pharmacist for safer therapeutic alternatives within the same pharmacological classes that do not share the same CYP450 metabolism pathways."))
    elif has_moderate:
        recs.append(("⚠️ Dosage Adjustment Required", "Empirically reduce the dosage of the substrate drug by 30-50% and titrate upwards based on clinical response and serum levels."))
        recs.append(("🔬 Monitoring Protocol", "Establish a strict outpatient monitoring protocol. Check comprehensive metabolic panel (CMP) and relevant drug troughs within 5-7 days of initiation."))
    else:
        recs.append(("✅ Standard Monitoring", "No severe interactions detected. Proceed with standard clinical monitoring and counsel patient on standard adverse effects."))
        
    return recs

def render_clinical_rationale_card(interaction):
    """Renders a single interactive rationale card for an interaction."""
    pair = " + ".join(interaction.get("drug_pair", [])).title()
    sev = interaction.get("severity", "Unknown")
    
    color_map = {
        "Major": ("#ff003c", "🔴"),
        "Moderate": ("#ff9d00", "🟠"),
        "Minor": ("#00f3ff", "🟢")
    }
    text_c, icon = color_map.get(sev, ("#8ab4f8", "⚪"))
    
    st.markdown(f"""
    <div style="background: rgba(0, 243, 255, 0.03); border-left: 4px solid {text_c}; padding: 1.2rem 1.5rem; margin-bottom: 1rem; border-radius: 0 12px 12px 0; color: #e0f4f4; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.8rem;">
            <div style="font-family:'Outfit', sans-serif; font-size:1.1rem; font-weight:700; color:#ffffff;">
                {pair}
            </div>
            <div style="background: rgba(11, 17, 33, 0.8); color:{text_c}; border: 1px solid {text_c}; padding:0.2rem 0.6rem; border-radius:6px; font-size:0.75rem; font-weight:700; font-family:'JetBrains Mono', monospace; letter-spacing:1px; text-transform:uppercase;">
                {icon} {sev} SEVERITY
            </div>
        </div>
        <div style="font-size:0.95rem; color:#e0f4f4; margin-bottom:0.8rem; line-height: 1.6;">
            {generate_ai_explanation(interaction)}
        </div>
        <div style="font-size:0.85rem; background:rgba(11, 17, 33, 0.6); padding: 0.8rem; border-radius: 8px; color:#8ab4f8; border: 1px dashed rgba(0, 243, 255, 0.2);">
            <strong style="color:#00f3ff;">Clinical Action:</strong> {interaction.get("clinical_recommendation", "Monitor therapy.")}
        </div>
    </div>
    """, unsafe_allow_html=True)
