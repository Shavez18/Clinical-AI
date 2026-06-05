import streamlit as st
import datetime
import time

from ui.theme import apply_advanced_theme
from integrations.api_wrapper import fetch_drug_interactions
from analytics.drug_analytics import (
    calculate_toxicity_score,
    extract_pharmacological_classes,
    generate_compatibility_matrix,
    estimate_organ_impact
)
from visuals.drug_charts import (
    render_risk_gauge,
    render_organ_impact_radar,
    render_interaction_network,
    render_compatibility_heatmap
)
from ai.drug_recommendations import (
    get_clinical_recommendations,
    render_clinical_rationale_card
)
from recommendations.recommendation_ui import render_drug_recommendations

def render_drug_dashboard(API_URL, headers):
    """Main rendering function for the advanced Drug Interaction Dashboard."""
    
    # Apply Advanced Theme
    apply_advanced_theme()
    
    st.markdown(f"""
        <div class="adv-subtitle">⚡ SYSTEM ONLINE // PHARMACOVIGILANCE MODULE</div>
        <div class="adv-title">Pharmacovigilance Intelligence</div>
        <p style="color:#8ab4f8; margin-bottom:2rem; font-size:1.05rem;">
            Enterprise-grade multi-drug interaction ecosystem and toxicity analytics.
        </p>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # QUERY SECTION
    # -------------------------------------------------------------
    st.markdown('<div class="adv-header">MEDICATION REGIMEN QUERY</div>', unsafe_allow_html=True)
    st.info("⚕ Enter a polypharmacy regimen (2 or more generic names) to generate an AI safety analysis.")
    
    drugs = st.text_input(
        "Medications",
        placeholder="e.g. warfarin, amiodarone, aspirin, atorvastatin",
        label_visibility="collapsed",
        key="drug_input_adv"
    )
    
    st.markdown('<br>', unsafe_allow_html=True)
    run = st.button("INITIALIZE PHARMACOVIGILANCE ANALYSIS", use_container_width=True)

    if run:
        if not drugs:
            st.warning("Please enter at least two medication names.")
            return

        drug_list = [d.strip() for d in drugs.split(",") if d.strip()]
        if len(drug_list) < 2:
            st.warning("Please enter at least two medications to check interactions.")
            return

        with st.spinner("Analyzing multi-drug ecosystem…"):
            data = fetch_drug_interactions(API_URL, headers, drug_list)
        
        if "error" in data:
            st.error(f"System Error: {data['error']}")
            return
            
        analysis = data.get("analysis", {})
        interactions = analysis.get("interactions", [])
        safety_profiles = analysis.get("safety_profiles", [])
        base_risk_score = analysis.get("risk_score", 5.0)
        
        # --- Analytics Computation ---
        toxicity_score = calculate_toxicity_score(base_risk_score, interactions, safety_profiles)
        pharma_classes = extract_pharmacological_classes(safety_profiles)
        comp_matrix = generate_compatibility_matrix(drug_list, interactions)
        organ_impact = estimate_organ_impact(interactions, safety_profiles)
        
        # -------------------------------------------------------------
        # ROW 1: RISK & ORGAN IMPACT
        # -------------------------------------------------------------
        st.markdown('<div class="adv-header">TOXICITY & SEVERITY RISK</div>', unsafe_allow_html=True)
        
        r1c1, r1c2 = st.columns([1, 1.2])
        
        with r1c1:
            fig_gauge = render_risk_gauge(toxicity_score, "Systemic Toxicity Score")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Clinical Recommendation based on toxicity
            st.markdown('<div style="margin-top:1rem; padding-top:1rem; border-top:1px solid rgba(0, 243, 255, 0.2);">', unsafe_allow_html=True)
            recs = get_clinical_recommendations(interactions)
            icon, msg = recs[0]
            st.markdown(f"**{icon}**<br><span style='font-size:0.85rem; color:#8ab4f8;'>{msg}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with r1c2:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">ORGAN SYSTEM IMPACT PREDICTION</div>', unsafe_allow_html=True)
            fig_radar = render_organ_impact_radar(organ_impact)
            st.plotly_chart(fig_radar, use_container_width=True)

        # -------------------------------------------------------------
        # ROW 2: ECOSYSTEM & COMPATIBILITY
        # -------------------------------------------------------------
        st.markdown('<div class="adv-header">MULTI-DRUG INTERACTION NETWORK</div>', unsafe_allow_html=True)
        
        r2c1, r2c2 = st.columns([1.2, 1])
        
        with r2c1:
            if interactions:
                fig_net = render_interaction_network(drug_list, interactions)
                st.plotly_chart(fig_net, use_container_width=True)
                st.markdown("<div style='text-align:center; font-size:0.8rem; color:#8ab4f8;'>Nodes: Medications | Edges: Interactions (Color indicates severity)</div>", unsafe_allow_html=True)
            else:
                st.success("✅ No interactions found to construct network.")
            
        with r2c2:
            st.markdown('<div class="kpi-label" style="text-align:center; margin-bottom:0.5rem;">CONTRAINDICATION HEATMAP</div>', unsafe_allow_html=True)
            fig_heat = render_compatibility_heatmap(comp_matrix)
            st.plotly_chart(fig_heat, use_container_width=True)

        # -------------------------------------------------------------
        # ROW 3: AI EXPLAINABILITY & CLINICAL RATIONALE
        # -------------------------------------------------------------
        st.markdown('<div class="adv-header">AI EXPLAINABILITY & PATHWAY REASONING</div>', unsafe_allow_html=True)
        
        if interactions:
            for i in interactions:
                render_clinical_rationale_card(i)
        else:
            st.markdown('<div style="background: rgba(0, 243, 255, 0.03); border: 1px solid rgba(0, 243, 255, 0.3); padding: 1rem; border-radius: 10px; color: #e0f4f4;">✅ <strong>Clear:</strong> The AI engine confirms no significant pharmacokinetic or pharmacodynamic interactions detected in this regimen.</div>', unsafe_allow_html=True)

        # -------------------------------------------------------------
        # ROW 4: PHARMACOLOGICAL PROFILES
        # -------------------------------------------------------------
        st.markdown('<div class="adv-header">PHARMACOLOGICAL CLASS ANALYSIS</div>', unsafe_allow_html=True)
        
        for sp in safety_profiles:
            drug_name = sp.get("drug", "Unknown").title()
            p_class = pharma_classes.get(drug_name.lower(), "Systemic Agent")
            
            with st.expander(f"🔬 {drug_name} ({p_class})", expanded=False):
                if sp.get("error"):
                    st.warning(sp["error"])
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"<strong style='color:#ff003c; font-size:0.85rem; display:block; margin-bottom:0.5rem;'>Boxed Warnings</strong>", unsafe_allow_html=True)
                        if sp["boxed_warnings"]:
                            for w in sp["boxed_warnings"]:
                                st.markdown(f"""
                                <div style="background: rgba(255, 0, 60, 0.1); border-left: 3px solid #ff003c; padding: 0.8rem; margin-bottom: 0.5rem; border-radius: 4px; color: #e0f4f4; font-size: 0.85rem; line-height: 1.4;">
                                    {w}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background: rgba(0, 243, 255, 0.05); border-left: 3px solid #00f3ff; padding: 0.8rem; margin-bottom: 0.5rem; border-radius: 4px; color: #e0f4f4; font-size: 0.85rem;">
                                No boxed warnings detected.
                            </div>
                            """, unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<strong style='color:#ff9d00; font-size:0.85rem; display:block; margin-bottom:0.5rem;'>Contraindications</strong>", unsafe_allow_html=True)
                        if sp["contraindications"]:
                            for c in sp["contraindications"]:
                                st.markdown(f"""
                                <div style="background: rgba(255, 157, 0, 0.1); border-left: 3px solid #ff9d00; padding: 0.8rem; margin-bottom: 0.5rem; border-radius: 4px; color: #e0f4f4; font-size: 0.85rem; line-height: 1.4;">
                                    {c}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background: rgba(0, 243, 255, 0.05); border-left: 3px solid #00f3ff; padding: 0.8rem; margin-bottom: 0.5rem; border-radius: 4px; color: #e0f4f4; font-size: 0.85rem;">
                                No contraindications detected.
                            </div>
                            """, unsafe_allow_html=True)

        # Audit Log Write
        if "audit_logs" in st.session_state:
            st.session_state.audit_logs.append({
                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Module": "Advanced Pharmacovigilance",
                "Query Overview": f"{', '.join(drug_list)[:30]}",
                "Outcome/Result": f"Toxicity Score: {toxicity_score:.1f}"
            })
        
        st.markdown("""
        <div style="margin-top:3rem; padding:1.5rem; background:rgba(11, 17, 33, 0.65); border-radius:12px; border:1px solid rgba(0, 243, 255, 0.15); text-align:center;">
            <span style="font-size:0.75rem; color:#8ab4f8; font-family:'JetBrains Mono', monospace;">
                <strong>CLINICAL AI DISCLAIMER:</strong> This platform is designed for investigational intelligence and decision support. 
                It does not replace professional pharmacist review or physician judgment. CYP450 reasoning is deterministically simulated for this demo.
            </span>
        </div>
        """, unsafe_allow_html=True)

        # ----- RISK-BASED CARE PLAN & SPECIALIST RECOMMENDATION -----
        # Non-destructive enhancement: renders AFTER all existing outputs.
        # Reads toxicity_score only — does not modify drug analysis or session state.
        render_drug_recommendations(toxicity_score, interactions, drug_list)

