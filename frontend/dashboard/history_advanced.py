"""
history_advanced.py
─────────────────────────────────────────────────────────────────────────────
Main entry point for the Advanced Clinical Records & Analytics Center.
Call: render_history_dashboard(username)
"""
import streamlit as st
import datetime
import pandas as pd

from ui.theme import apply_advanced_theme
from history.clinical_records import (
    get_session_records, get_record_stats, filter_records,
    get_timeline_data, compute_risk_progression, generate_ai_summary,
)
from analytics.clinical_analytics import (
    plot_risk_progression, plot_module_frequency, plot_risk_distribution,
    plot_activity_timeline, plot_prediction_heatmap, plot_avg_risk_gauge,
)
from history.export_engine import export_csv, export_json, generate_pdf_report


# ── Shared style helpers ──────────────────────────────────────────────────────
def _kpi(label: str, value: str, color: str = "#00f3ff", sub: str = ""):
    return f"""
    <div class="kpi-container">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{color};font-size:2.2rem;">{value}</div>
        {"<div style='color:#8ab4f8;font-size:0.78rem;margin-top:0.3rem;'>"+sub+"</div>" if sub else ""}
    </div>"""


def _section(title: str):
    st.markdown(f'<div class="adv-header">{title}</div>', unsafe_allow_html=True)


def _insight(title: str, body: str, color: str = "#00f3ff"):
    st.markdown(f"""
    <div class="ai-insight" style="border-left-color:{color};">
        <div class="insight-title" style="color:{color};">{title}</div>
        <div>{body}</div>
    </div>""", unsafe_allow_html=True)


# ── Additional CSS injected once ──────────────────────────────────────────────
_EXTRA_CSS = """
<style>
/* Tab bar */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(11,17,33,0.6) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(0,243,255,0.15) !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #8ab4f8 !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(0,243,255,0.12) !important;
    color: #00f3ff !important;
    box-shadow: 0 0 12px rgba(0,243,255,0.2) !important;
}
/* Timeline card */
.timeline-card {
    background: rgba(11,17,33,0.65);
    border: 1px solid rgba(0,243,255,0.12);
    border-left: 4px solid;
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.7rem;
    transition: background 0.2s ease;
}
.timeline-card:hover { background: rgba(0,243,255,0.05); }
.timeline-ts {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #8ab4f8;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}
.timeline-mod {
    font-weight: 700;
    font-size: 0.88rem;
    color: #00f3ff;
    margin-bottom: 0.2rem;
}
.timeline-query { font-size: 0.84rem; color: #e0f4f4; }
.timeline-result {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #8ab4f8;
    margin-top: 0.3rem;
}
/* Severity badge */
.badge {
    display: inline-block;
    padding: 0.18rem 0.6rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    font-family: 'JetBrains Mono', monospace;
}
/* Export card */
.export-card {
    background: rgba(11,17,33,0.65);
    border: 1px solid rgba(0,243,255,0.15);
    border-radius: 16px;
    padding: 1.5rem 1.5rem 1.2rem;
    text-align: center;
    margin-bottom: 1rem;
}
.export-icon { font-size: 2.4rem; margin-bottom: 0.5rem; }
.export-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: #00f3ff;
    margin-bottom: 0.3rem;
}
.export-desc { font-size: 0.82rem; color: #8ab4f8; margin-bottom: 0.9rem; }
/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: rgba(11,17,33,0.5);
    border: 1px dashed rgba(0,243,255,0.2);
    border-radius: 16px;
    margin: 1rem 0;
}
.empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.empty-msg {
    font-family: 'JetBrains Mono', monospace;
    color: #8ab4f8;
    font-size: 0.9rem;
    letter-spacing: 0.5px;
}
/* Scrollable audit table */
[data-testid="stDataFrame"] { border: 1px solid rgba(0,243,255,0.15) !important; border-radius:10px !important; }
</style>"""


# ── Severity badge helper ─────────────────────────────────────────────────────
_SEV_COLORS = {"HIGH": "#ff003c", "MODERATE": "#ff9d00", "LOW": "#00e676", "N/A": "#8ab4f8"}

def _badge(severity: str) -> str:
    col = _SEV_COLORS.get(severity, "#8ab4f8")
    return (f'<span class="badge" style="background:rgba(0,0,0,0.3);'
            f'border:1px solid {col};color:{col};">{severity}</span>')


# ═════════════════════════════════════════════════════════════════════════════
# MAIN RENDER
# ═════════════════════════════════════════════════════════════════════════════
def render_history_dashboard(username: str):
    # 1. Apply matching theme
    apply_advanced_theme()
    st.markdown(_EXTRA_CSS, unsafe_allow_html=True)

    # 2. Load data once
    df = get_session_records()
    stats = get_record_stats(df)
    has_data = not df.empty

    # 3. Hero header
    st.markdown("""
        <div class="adv-subtitle">⚕ CLINICAL INTELLIGENCE CENTER // AUDIT & ANALYTICS</div>
        <div class="adv-title">Clinical Records</div>
        <p style="color:#8ab4f8;margin-bottom:1.5rem;font-size:1rem;">
            Enterprise-grade audit analytics · Longitudinal risk tracking ·
            Downloadable clinical reports
        </p>""", unsafe_allow_html=True)

    # 4. KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    kpi_data = [
        (col1, "TOTAL QUERIES",   str(stats["total"]),      "#00f3ff", ""),
        (col2, "MODULES USED",    str(stats["modules"]),    "#8ab4f8", ""),
        (col3, "HIGH RISK",       str(stats["high_risk"]),  "#ff003c", "findings"),
        (col4, "MODERATE RISK",   str(stats["moderate_risk"]), "#ff9d00", "findings"),
        (col5, "AVG RISK SCORE",  f"{stats['avg_risk']:.1f}%", "#00e676", "session avg"),
    ]
    for col, label, value, color, sub in kpi_data:
        with col:
            st.markdown(_kpi(label, value, color, sub), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Tab layout
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋  Clinical Records",
        "📈  Analytics",
        "🏥  Patient Timeline",
        "🤖  AI Summary",
        "📥  Export Center",
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 — CLINICAL RECORDS (original audit log + search/filter)
    # ─────────────────────────────────────────────────────────────────────────
    with tab1:
        _section("🔍 SEARCH & FILTER")

        fc1, fc2, fc3, fc4 = st.columns([2, 1.5, 1.5, 2], vertical_alignment="bottom")
        with fc1:
            search_q = st.text_input("Keyword Search", placeholder="keyword…", key="hist_search")
        with fc2:
            mod_opts = ["All"] + stats["module_list"]
            sel_mod = st.selectbox("Module", mod_opts, key="hist_mod")
        with fc3:
            sel_sev = st.selectbox("Severity", ["All", "HIGH", "MODERATE", "LOW", "N/A"],
                                   key="hist_sev")
        with fc4:
            if st.button("⟳  Reset Filters", use_container_width=True, key="hist_reset"):
                for k in ["hist_search", "hist_mod", "hist_sev"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        _section("📋 AUDIT LOG TABLE")

        if not has_data:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <div class="empty-msg">NO RECORDS IN THIS SESSION YET<br>
                Run a prediction module to populate audit logs.</div>
            </div>""", unsafe_allow_html=True)
        else:
            filtered = filter_records(df, module=sel_mod, severity=sel_sev, search=search_q)
            display_cols = ["Timestamp", "Module", "Query Overview", "Outcome/Result", "Severity", "Risk %"]
            display_cols = [c for c in display_cols if c in filtered.columns]
            st.dataframe(
                filtered[display_cols].sort_values("Timestamp", ascending=False)
                if "Timestamp" in filtered.columns else filtered[display_cols],
                use_container_width=True,
                hide_index=True,
            )
            st.markdown(
                f"<div style='font-family:JetBrains Mono,monospace;font-size:0.72rem;"
                f"color:#8ab4f8;margin-top:0.4rem;'>"
                f"Showing {len(filtered)} of {len(df)} records · "
                f"Session encrypted · Demo data only</div>",
                unsafe_allow_html=True,
            )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 — ANALYTICS DASHBOARD
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:
        if not has_data:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <div class="empty-msg">NO DATA TO ANALYZE<br>
                Complete at least one prediction to unlock analytics.</div>
            </div>""", unsafe_allow_html=True)
        else:
            risk_prog_df = compute_risk_progression(df)

            # Row 1: gauge + risk progression
            _section("📈 RISK PROGRESSION & SESSION GAUGE")
            a1, a2 = st.columns([1, 2.5])
            with a1:
                st.plotly_chart(plot_avg_risk_gauge(stats["avg_risk"]),
                                use_container_width=True)
            with a2:
                st.plotly_chart(plot_risk_progression(risk_prog_df),
                                use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Row 2: module freq + donut
            _section("🏥 MODULE FREQUENCY & RISK DISTRIBUTION")
            b1, b2 = st.columns(2)
            with b1:
                st.plotly_chart(plot_module_frequency(df), use_container_width=True)
            with b2:
                st.plotly_chart(plot_risk_distribution(df), use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Row 3: activity timeline + heatmap
            _section("⏱ ACTIVITY TIMELINE & SEVERITY HEATMAP")
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(plot_activity_timeline(df), use_container_width=True)
            with c2:
                st.plotly_chart(plot_prediction_heatmap(df), use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 — PATIENT TIMELINE
    # ─────────────────────────────────────────────────────────────────────────
    with tab3:
        _section("🏥 CHRONOLOGICAL CLINICAL TIMELINE")

        if not has_data:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🕐</div>
                <div class="empty-msg">TIMELINE EMPTY<br>
                No clinical queries recorded this session.</div>
            </div>""", unsafe_allow_html=True)
        else:
            timeline_df = get_timeline_data(df)

            # Optional: filter by module for timeline
            tl_mods = ["All"] + stats["module_list"]
            tl_sel = st.selectbox("Filter Timeline by Module", tl_mods, key="tl_mod")
            if tl_sel != "All":
                timeline_df = timeline_df[timeline_df["Module"] == tl_sel]

            st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

            # Render timeline cards newest-first
            for _, row in timeline_df.iloc[::-1].iterrows():
                sev = row.get("Severity", "N/A")
                border_col = _SEV_COLORS.get(sev, "#8ab4f8")
                risk_val = row.get("Risk %", 0)
                risk_display = f"{risk_val:.1f}%" if risk_val > 0 else "—"

                st.markdown(f"""
                <div class="timeline-card" style="border-left-color:{border_col};">
                    <div class="timeline-ts">🕐 {row.get('Timestamp','—')}</div>
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.2rem;">
                        <div class="timeline-mod">{row.get('Module','Unknown')}</div>
                        {_badge(sev)}
                        <span style="font-family:JetBrains Mono,monospace;font-size:0.78rem;
                               color:{border_col};">● {risk_display}</span>
                    </div>
                    <div class="timeline-query">{row.get('Query Overview','—')}</div>
                    <div class="timeline-result">↳ {row.get('Outcome/Result','—')}</div>
                </div>""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 — AI CLINICAL SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    with tab4:
        _section("🤖 AI CLINICAL INTELLIGENCE SUMMARY")

        if not has_data:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🤖</div>
                <div class="empty-msg">NO SESSION DATA<br>
                Run predictions first to generate AI clinical summary.</div>
            </div>""", unsafe_allow_html=True)
        else:
            with st.spinner("Compiling clinical narrative…"):
                summary = generate_ai_summary(df, username)

            # Alert banner
            alert_col = summary["alert_color"]
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.35);border:1px solid {alert_col};
                        border-radius:12px;padding:1rem 1.25rem;margin-bottom:1.2rem;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                            color:{alert_col};letter-spacing:1px;margin-bottom:0.3rem;">
                    ⚠ CLINICAL ALERT STATUS
                </div>
                <div style="font-size:0.95rem;color:#e0f4f4;font-weight:600;">
                    {summary['alert']}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                            color:#8ab4f8;margin-top:0.4rem;">
                    Generated: {summary['generated_at']} · Session: {username}
                </div>
            </div>""", unsafe_allow_html=True)

            # Session overview
            s1, s2, s3 = st.columns(3)
            with s1:
                st.markdown(_kpi("RISK TREND", summary["trend"].upper(),
                                 "#00f3ff" if summary["trend"] == "stable" else
                                 ("#ff003c" if summary["trend"] == "increasing" else "#00e676")),
                            unsafe_allow_html=True)
            with s2:
                st.markdown(_kpi("MOST USED MODULE",
                                 summary["most_used_module"].split()[0][:12],
                                 "#8ab4f8"), unsafe_allow_html=True)
            with s3:
                st.markdown(_kpi("AVG RISK", f"{summary['stats']['avg_risk']:.1f}%",
                                 "#ff9d00" if summary['stats']['avg_risk'] > 30 else "#00e676"),
                            unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            _section("📋 MODULE-LEVEL FINDINGS")
            for finding in summary["module_findings"]:
                _insight("FINDING", finding, "#8ab4f8")

            st.markdown("<br>", unsafe_allow_html=True)
            _section("💊 AI CLINICAL RECOMMENDATIONS")
            for rec in summary["recommendations"]:
                priority = "HIGH" if "🔴" in rec else ("MODERATE" if "🟡" in rec else "ADVISORY")
                color = (
                    "#ff003c" if priority == "HIGH" else
                    "#ff9d00" if priority == "MODERATE" else "#00f3ff"
                )
                _insight(f"REC · {priority}", rec, color)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-family:JetBrains Mono,monospace;font-size:0.72rem;"
                "color:#8ab4f8;padding:0.5rem;border-top:1px solid rgba(0,243,255,0.1);'>"
                "⚠ AI-generated narrative from session data only. "
                "Not a substitute for licensed clinical judgment.</div>",
                unsafe_allow_html=True,
            )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 5 — EXPORT CENTER
    # ─────────────────────────────────────────────────────────────────────────
    with tab5:
        _section("📥 CLINICAL REPORT EXPORT CENTER")

        if not has_data:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📥</div>
                <div class="empty-msg">NO RECORDS TO EXPORT<br>
                Run predictions first to generate exportable data.</div>
            </div>""", unsafe_allow_html=True)
        else:
            ai_sum = generate_ai_summary(df, username)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            ex1, ex2, ex3 = st.columns(3)

            # PDF
            with ex1:
                st.markdown("""
                <div class="export-card">
                    <div class="export-icon">📄</div>
                    <div class="export-title">PDF CLINICAL REPORT</div>
                    <div class="export-desc">Professional branded report with KPIs,
                    module findings, AI recommendations and full audit trail.</div>
                </div>""", unsafe_allow_html=True)
                if st.button("⬇  Generate PDF", use_container_width=True, key="exp_pdf"):
                    with st.spinner("Compiling PDF report…"):
                        pdf_bytes = generate_pdf_report(df, username, ai_sum)
                    if pdf_bytes.startswith(b"reportlab"):
                        st.warning("⚠ reportlab not installed. Run: `pip install reportlab`")
                    else:
                        st.download_button(
                            "📄 Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"ClinicalAI_Report_{ts}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="dl_pdf",
                        )

            # CSV
            with ex2:
                st.markdown("""
                <div class="export-card">
                    <div class="export-icon">📊</div>
                    <div class="export-title">CSV DATA EXPORT</div>
                    <div class="export-desc">Structured comma-separated export of all
                    session records, risk scores, and severity classifications.</div>
                </div>""", unsafe_allow_html=True)
                csv_bytes = export_csv(df)
                st.download_button(
                    "⬇  Download CSV",
                    data=csv_bytes,
                    file_name=f"ClinicalAI_Records_{ts}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_csv",
                )

            # JSON
            with ex3:
                st.markdown("""
                <div class="export-card">
                    <div class="export-icon">🗄</div>
                    <div class="export-title">JSON DATA EXPORT</div>
                    <div class="export-desc">Machine-readable JSON export for EHR
                    integration, API consumption, or downstream analytics pipelines.</div>
                </div>""", unsafe_allow_html=True)
                json_bytes = export_json(df)
                st.download_button(
                    "⬇  Download JSON",
                    data=json_bytes,
                    file_name=f"ClinicalAI_Records_{ts}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_json",
                )

            # Report preview
            st.markdown("<br>", unsafe_allow_html=True)
            _section("👁 REPORT PREVIEW")
            with st.expander("Preview AI Summary (included in PDF)", expanded=False):
                st.markdown(f"**Generated:** {ai_sum['generated_at']}")
                st.markdown(f"**Alert:** {ai_sum['alert']}")
                st.markdown(f"**Risk Trend:** {ai_sum['trend'].upper()}")
                st.markdown("**Module Findings:**")
                for f in ai_sum["module_findings"]:
                    st.markdown(f"- {f}")
                st.markdown("**Recommendations:**")
                for r in ai_sum["recommendations"]:
                    st.markdown(f"- {r}")
