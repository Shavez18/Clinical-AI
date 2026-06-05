"""
export_engine.py
──────────────────────────────────────────────────────────────────────────────
Export Engine — PDF (reportlab), CSV, and JSON clinical report generation.
Gracefully degrades if reportlab is not installed.
"""
import io
import json
import datetime
import pandas as pd


# ── CSV Export ────────────────────────────────────────────────────────────────
def export_csv(df: pd.DataFrame) -> bytes:
    """Return a CSV bytes object from the records DataFrame."""
    # Drop internal helper columns
    export_df = df.drop(columns=[c for c in ["_ts", "Date", "Hour"] if c in df.columns], errors="ignore")
    return export_df.to_csv(index=False).encode("utf-8")


# ── JSON Export ───────────────────────────────────────────────────────────────
def export_json(df: pd.DataFrame) -> bytes:
    """Return a JSON bytes object from the records DataFrame."""
    export_df = df.drop(columns=[c for c in ["_ts", "Date", "Hour"] if c in df.columns], errors="ignore")
    return export_df.to_json(orient="records", indent=2).encode("utf-8")


# ── PDF Export ────────────────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    has_matplotlib = True
except ImportError:
    has_matplotlib = False


def _render_matplotlib_progression(df: pd.DataFrame) -> bytes:
    import io
    fig, ax = plt.subplots(figsize=(7, 3.5), dpi=200)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#f8fafc')

    if df.empty or "Risk %" not in df.columns:
        ax.text(0.5, 0.5, "No risk data available yet.", ha='center', va='center', color='#94a3b8', fontsize=10)
        ax.set_axis_off()
    else:
        risk_df = df[df["Risk %"] > 0].copy()
        if risk_df.empty:
            ax.text(0.5, 0.5, "No risk scores recorded yet.", ha='center', va='center', color='#94a3b8', fontsize=10)
            ax.set_axis_off()
        else:
            risk_df = risk_df.sort_values("_ts")
            x_vals = risk_df["Timestamp"].tolist()
            y_vals = risk_df["Risk %"].tolist()
            
            ax.plot(x_vals, y_vals, color='#0e8c8c', linewidth=2, marker='o', markersize=5, label="Risk %")
            ax.fill_between(x_vals, y_vals, color='#0e8c8c', alpha=0.1)

            ax.axhline(70, color='#b91c1c', linestyle='--', linewidth=0.8, alpha=0.8)
            ax.text(0.98, 71, "High Risk (70%)", color='#b91c1c', fontsize=7, fontweight='bold', ha='right', transform=ax.get_yaxis_transform())
            ax.axhline(30, color='#b45309', linestyle='--', linewidth=0.8, alpha=0.8)
            ax.text(0.98, 31, "Moderate (30%)", color='#b45309', fontsize=7, fontweight='bold', ha='right', transform=ax.get_yaxis_transform())

            ax.set_ylabel("Risk Score (%)", fontsize=8, color='#0b2545', fontweight='bold')
            ax.tick_params(axis='x', rotation=15, labelsize=7, colors='#0b2545')
            ax.tick_params(axis='y', labelsize=7, colors='#0b2545')
            ax.set_ylim(0, 105)

            for spine in ["top", "right"]:
                ax.spines[spine].set_visible(False)
            ax.spines["left"].set_color("#cbd5e1")
            ax.spines["bottom"].set_color("#cbd5e1")
            ax.grid(True, linestyle=':', alpha=0.5, color="#cbd5e1")

    ax.set_title("Risk Progression Over Time", fontsize=10, fontweight='bold', color='#0b2545', pad=10)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    return buf.getvalue()


def _render_matplotlib_module_freq(df: pd.DataFrame) -> bytes:
    import io
    fig, ax = plt.subplots(figsize=(4, 4), dpi=200)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#f8fafc')

    if df.empty or "Module" not in df.columns:
        ax.text(0.5, 0.5, "No module data available yet.", ha='center', va='center', color='#94a3b8', fontsize=9)
        ax.set_axis_off()
    else:
        counts = df["Module"].value_counts().sort_values(ascending=True)
        colors = ['#00b4cc', '#0e8c8c', '#0b2545', '#94a3b8', '#cbd5e1']
        colors = [colors[i % len(colors)] for i in range(len(counts))]
        
        bars = ax.barh(counts.index, counts.values, color=colors, height=0.55, edgecolor='none')
        
        max_val = counts.max() if not counts.empty else 1
        for bar in bars:
            width = bar.get_width()
            ax.text(width + (max_val * 0.02), bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                    va='center', ha='left', fontsize=7, color='#0b2545', fontweight='bold')
                    
        ax.tick_params(axis='x', labelsize=7, colors='#0b2545')
        ax.tick_params(axis='y', labelsize=7, colors='#0b2545')
        ax.set_xlabel("Number of Queries", fontsize=8, color='#0b2545', fontweight='bold')
        
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#cbd5e1")
        ax.spines["bottom"].set_color("#cbd5e1")
        ax.grid(True, axis='x', linestyle=':', alpha=0.5, color="#cbd5e1")
        ax.set_xlim(0, max_val * 1.15)

    ax.set_title("Module Query Frequency", fontsize=9, fontweight='bold', color='#0b2545', pad=10)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    return buf.getvalue()


def _render_matplotlib_risk_dist(df: pd.DataFrame) -> bytes:
    import io
    fig, ax = plt.subplots(figsize=(4, 4), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    if df.empty or "Severity" not in df.columns:
        ax.text(0.5, 0.5, "No severity data available yet.", ha='center', va='center', color='#94a3b8', fontsize=9)
        ax.set_axis_off()
    else:
        counts = df["Severity"].value_counts()
        labels = counts.index.tolist()
        values = counts.values.tolist()
        
        sev_colors = {
            "HIGH": "#b91c1c",
            "MODERATE": "#b45309",
            "LOW": "#0d7d5b",
            "N/A": "#94a3b8"
        }
        colors = [sev_colors.get(l, "#94a3b8") for l in labels]
        
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors, autopct='%1.0f%%',
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2.0)
        )
        
        for text in texts:
            text.set_color('#0b2545')
            text.set_fontsize(7.5)
            text.set_weight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(7.5)
            autotext.set_weight('bold')
            
        ax.text(0, 0, f"Total\n{sum(values)}", ha='center', va='center', 
                fontsize=9, fontweight='bold', color='#0b2545')

    ax.set_title("Prediction Risk Distribution", fontsize=9, fontweight='bold', color='#0b2545', pad=10)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    return buf.getvalue()


def generate_pdf_report(df: pd.DataFrame, username: str, ai_summary: dict) -> bytes:
    """
    Generate a professional PDF clinical summary report using reportlab.
    Returns raw bytes. Falls back to a stub bytes string if reportlab absent.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether, Image
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        return b"reportlab not installed. Run: pip install reportlab"

    try:
        from analytics.clinical_analytics import (
            plot_risk_progression, plot_module_frequency, plot_risk_distribution, plot_avg_risk_gauge
        )
        has_analytics = True
    except ImportError:
        has_analytics = False

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # ── Colour Palette (matching the neon theme via muted professional tones) ──
    NAVY   = colors.HexColor("#0b2545")
    TEAL   = colors.HexColor("#0e8c8c")
    CYAN   = colors.HexColor("#00b4cc")
    LGRAY  = colors.HexColor("#e8eef5")
    MGRAY  = colors.HexColor("#94a3b8")
    RED    = colors.HexColor("#b91c1c")
    AMBER  = colors.HexColor("#b45309")
    GREEN  = colors.HexColor("#0d7d5b")
    WHITE  = colors.white
    BLACK  = colors.HexColor("#0d1f35")

    styles = getSampleStyleSheet()

    # Custom styles
    H1 = ParagraphStyle("H1", parent=styles["Normal"],
                         fontName="Helvetica-Bold", fontSize=22, leading=28,
                         textColor=WHITE, alignment=TA_CENTER, spaceAfter=4)
    H2 = ParagraphStyle("H2", parent=styles["Normal"],
                         fontName="Helvetica-Bold", fontSize=13,
                         textColor=TEAL, spaceBefore=14, spaceAfter=6)
    H3 = ParagraphStyle("H3", parent=styles["Normal"],
                         fontName="Helvetica-Bold", fontSize=10,
                         textColor=NAVY, spaceBefore=8, spaceAfter=4)
    BODY = ParagraphStyle("BODY", parent=styles["Normal"],
                           fontName="Helvetica", fontSize=9,
                           textColor=BLACK, leading=14, spaceAfter=4)
    MONO = ParagraphStyle("MONO", parent=styles["Normal"],
                           fontName="Courier", fontSize=8,
                           textColor=colors.HexColor("#3d5a7a"), leading=12)
    SMALL = ParagraphStyle("SMALL", parent=styles["Normal"],
                            fontName="Helvetica", fontSize=8,
                            textColor=MGRAY, leading=11)
    ALERT_HIGH = ParagraphStyle("ALERT", parent=styles["Normal"],
                                 fontName="Helvetica-Bold", fontSize=9,
                                 textColor=RED, leading=12)
    ALERT_OK   = ParagraphStyle("ALERT_OK", parent=styles["Normal"],
                                 fontName="Helvetica-Bold", fontSize=9,
                                 textColor=GREEN, leading=12)

    story = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = ai_summary.get("stats", {})

    # ── Cover Banner ──────────────────────────────────────────────────────────
    banner_data = [[Paragraph("⚕  ClinicalAI  —  Clinical Records Report", H1)]]
    banner = Table(banner_data, colWidths=[17 * cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story.append(banner)
    story.append(Spacer(1, 0.4 * cm))

    # Sub-header row
    meta_data = [[
        Paragraph(f"<b>Patient / Clinician:</b> {username}", BODY),
        Paragraph(f"<b>Report Generated:</b> {now}", BODY),
        Paragraph(f"<b>Total Records:</b> {stats.get('total', 0)}", BODY),
    ]]
    meta_tbl = Table(meta_data, colWidths=[5.7 * cm, 5.7 * cm, 5.6 * cm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LGRAY),
        ("ROWPADDING", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, MGRAY),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL))
    story.append(Spacer(1, 0.3 * cm))

    # ── Executive Summary ─────────────────────────────────────────────────────
    story.append(Paragraph("1. Executive Summary", H2))
    alert_txt = ai_summary.get("alert", "N/A")
    alert_style = ALERT_HIGH if "HIGH" in alert_txt.upper() or "ELEVATED" in alert_txt.upper() else ALERT_OK
    story.append(Paragraph(f"Clinical Alert Status: {alert_txt}", alert_style))
    story.append(Spacer(1, 0.2 * cm))

    trend = ai_summary.get("trend", "stable").upper()
    story.append(Paragraph(
        f"Risk Trend: <b>{trend}</b>  |  Most Used Module: <b>{ai_summary.get('most_used_module', 'N/A')}</b>  |  "
        f"Avg Risk Score: <b>{stats.get('avg_risk', 0):.1f}%</b>", BODY))
    story.append(Spacer(1, 0.3 * cm))

    # KPI Grid
    kpi_data = [
        ["Metric", "Value"],
        ["Total Queries", str(stats.get("total", 0))],
        ["Modules Used", str(stats.get("modules", 0))],
        ["High Risk Findings", str(stats.get("high_risk", 0))],
        ["Moderate Risk Findings", str(stats.get("moderate_risk", 0))],
        ["Low Risk Findings", str(stats.get("low_risk", 0))],
        ["Average Risk Score", f"{stats.get('avg_risk', 0):.1f}%"],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[10 * cm, 7 * cm])
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, MGRAY),
        ("ROWPADDING", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # ── Visual Analytics ──────────────────────────────────────────────────────
    if has_analytics and not df.empty:
        try:
            story.append(HRFlowable(width="100%", thickness=0.5, color=MGRAY))
            story.append(Paragraph("2. Clinical Analytics Visuals", H2))
            
            if has_matplotlib:
                img_bytes_prog = _render_matplotlib_progression(df)
                img_bytes_mod = _render_matplotlib_module_freq(df)
                img_bytes_dist = _render_matplotlib_risk_dist(df)
            else:
                # Fallback if matplotlib is absent
                fig_prog = plot_risk_progression(df)
                img_bytes_prog = fig_prog.to_image(format="png", width=700, height=350, scale=2)
                
                fig_mod = plot_module_frequency(df)
                img_bytes_mod = fig_mod.to_image(format="png", width=350, height=350, scale=2)
                
                fig_dist = plot_risk_distribution(df)
                img_bytes_dist = fig_dist.to_image(format="png", width=350, height=350, scale=2)

            story.append(Image(io.BytesIO(img_bytes_prog), width=17*cm, height=8.5*cm))
            story.append(Spacer(1, 0.4 * cm))

            chart_tbl = Table([[
                Image(io.BytesIO(img_bytes_mod), width=8*cm, height=8*cm),
                Image(io.BytesIO(img_bytes_dist), width=8*cm, height=8*cm)
            ]], colWidths=[8.5*cm, 8.5*cm])
            chart_tbl.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(chart_tbl)
            story.append(Spacer(1, 0.4 * cm))
        except Exception as e:
            # Fallback if image generation fails
            pass

    # ── Module Findings ───────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MGRAY))
    story.append(Paragraph("3. Module-Level Findings", H2))
    for finding in ai_summary.get("module_findings", []):
        story.append(Paragraph(f"• {finding}", BODY))
    story.append(Spacer(1, 0.3 * cm))

    # ── AI Recommendations ────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MGRAY))
    story.append(Paragraph("4. AI Clinical Recommendations", H2))
    for rec in ai_summary.get("recommendations", []):
        story.append(Paragraph(rec, BODY))
    story.append(Spacer(1, 0.3 * cm))

    # ── Diagnosis / Query Log Table ───────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MGRAY))
    story.append(Paragraph("5. Detailed Audit Trail", H2))

    if not df.empty:
        display_cols = ["Timestamp", "Module", "Query Overview", "Outcome/Result", "Severity"]
        display_cols = [c for c in display_cols if c in df.columns]
        table_df = df[display_cols].tail(50)  # cap at 50 rows for PDF

        headers_row = [Paragraph(f"<b>{c}</b>", SMALL) for c in display_cols]
        table_data = [headers_row]
        for _, row in table_df.iterrows():
            table_data.append([Paragraph(str(row[c]), MONO) for c in display_cols])

        col_widths = {
            "Timestamp": 3.0 * cm,
            "Module": 2.8 * cm,
            "Query Overview": 5.5 * cm,
            "Outcome/Result": 4.5 * cm,
            "Severity": 1.2 * cm,
        }
        col_w = [col_widths.get(c, 3.4 * cm) for c in display_cols]

        audit_tbl = Table(table_data, colWidths=col_w, repeatRows=1)
        sev_idx = display_cols.index("Severity") if "Severity" in display_cols else None
        tbl_style = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
            ("GRID", (0, 0), (-1, -1), 0.3, MGRAY),
            ("ROWPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        audit_tbl.setStyle(TableStyle(tbl_style))
        story.append(audit_tbl)
    else:
        story.append(Paragraph("No records available for this session.", BODY))

    # ── Risk-Based Care Plan & Specialist Recommendations ────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MGRAY))
    story.append(Paragraph("6. Risk-Based Care Plan & Specialist Recommendations", H2))
    story.append(Paragraph(
        "The following care plans are generated by the ClinicalAI Recommendation Engine "
        "based on prediction outputs from this session. They are advisory only.",
        BODY
    ))
    story.append(Spacer(1, 0.25 * cm))

    try:
        import streamlit as st
        cp_entries = st.session_state.get("pdf_care_plans", [])
    except Exception:
        cp_entries = []

    if not cp_entries:
        story.append(Paragraph(
            "No care plan data available. Run a prediction module to generate recommendations.",
            SMALL
        ))
    else:
        _risk_colors = {
            "low":      colors.HexColor("#0d7d5b"),
            "moderate": colors.HexColor("#b45309"),
            "high":     colors.HexColor("#b91c1c"),
        }
        _risk_bg = {
            "low":      colors.HexColor("#d1fae5"),
            "moderate": colors.HexColor("#fef3c7"),
            "high":     colors.HexColor("#fee2e2"),
        }
        REC_H3 = ParagraphStyle("REC_H3", parent=styles["Normal"],
                                fontName="Helvetica-Bold", fontSize=9,
                                textColor=NAVY, spaceBefore=6, spaceAfter=3)
        PILL = ParagraphStyle("PILL", parent=styles["Normal"],
                              fontName="Helvetica-Bold", fontSize=10,
                              leading=14, alignment=TA_CENTER)
        SPEC = ParagraphStyle("SPEC", parent=styles["Normal"],
                              fontName="Helvetica-Bold", fontSize=9,
                              textColor=TEAL, leading=12)
        SPEC_ROLE = ParagraphStyle("SPEC_ROLE", parent=styles["Normal"],
                                   fontName="Helvetica", fontSize=8,
                                   textColor=BLACK, leading=11)
        FU = ParagraphStyle("FU", parent=styles["Normal"],
                            fontName="Courier", fontSize=7.5,
                            textColor=colors.HexColor("#065f46"), leading=11)

        for idx, entry in enumerate(cp_entries):
            module_name = entry.get("module", f"Module {idx+1}")
            risk_label  = entry.get("risk_label", "N/A")
            tier        = entry.get("tier", "low")
            care_plan   = entry.get("care_plan", {})
            specialist  = entry.get("specialist", {})
            wellness    = entry.get("wellness", [])

            rc = _risk_colors.get(tier, NAVY)
            rb = _risk_bg.get(tier, LGRAY)

            # ── Module sub-header
            story.append(Paragraph(f"{module_name}", H3))

            # ── Risk badge row
            badge_tbl = Table(
                [[Paragraph(f"Risk Level: {risk_label}", PILL)]],
                colWidths=[17 * cm]
            )
            badge_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), rb),
                ("TEXTCOLOR",  (0, 0), (-1, -1), rc),
                ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 0.5, rc),
                ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ]))
            story.append(badge_tbl)
            story.append(Spacer(1, 0.2 * cm))

            # ── Two-column: Risk Factors + Recommended Actions
            rf_items  = care_plan.get("risk_factors", [])
            act_items = care_plan.get("actions", [])

            rf_paras  = [Paragraph(f"• {r}", BODY) for r in rf_items]  or [Paragraph("—", BODY)]
            act_paras = [Paragraph(f"• {a}", BODY) for a in act_items] or [Paragraph("—", BODY)]

            left_cell  = [Paragraph("Key Risk Factors", REC_H3)] + rf_paras
            right_cell = [Paragraph("Recommended Actions", REC_H3)] + act_paras

            two_col = Table([[left_cell, right_cell]], colWidths=[8.25 * cm, 8.75 * cm])
            two_col.setStyle(TableStyle([
                ("VALIGN",     (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING",(0, 0), (-1, -1), 6),
                ("RIGHTPADDING",(0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("BOX",        (0, 0), (-1, -1), 0.3, MGRAY),
                ("LINEBEFORE", (1, 0), (1, -1), 0.3, MGRAY),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE]),
            ]))
            story.append(two_col)
            story.append(Spacer(1, 0.2 * cm))

            # ── Specialist Card
            if specialist:
                spec_icon    = specialist.get("icon",     "⚕")
                spec_name    = specialist.get("specialty", "Specialist")
                spec_role    = specialist.get("role",     "")
                spec_reason  = specialist.get("reason",   "")
                spec_step    = specialist.get("next_step","")
                spec_block   = [
                    Paragraph(f"{spec_icon}  {spec_name}", SPEC),
                    Paragraph(spec_role, SPEC_ROLE),
                    Paragraph(f"Reason: {spec_reason}", SPEC_ROLE),
                    Paragraph(f"→ {spec_step}", SPEC),
                ]
                spec_tbl = Table([[spec_block]], colWidths=[17 * cm])
                spec_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#eef9ff")),
                    ("BOX",           (0, 0), (-1, -1), 0.5, CYAN),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                    ("TOPPADDING",    (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]))
                story.append(spec_tbl)
                story.append(Spacer(1, 0.15 * cm))

            # ── Follow-Up Timeline
            fu_items = care_plan.get("follow_up", [])
            timeline = care_plan.get("timeline", "As directed")
            if fu_items:
                fu_header = [[Paragraph(f"Follow-Up Timeline  ·  Target: {timeline}", FU)]]
                fu_rows   = [[Paragraph(f"→  {f}", FU)] for f in fu_items]
                fu_tbl    = Table(fu_header + fu_rows, colWidths=[17 * cm])
                fu_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#ecfdf5")),
                    ("BACKGROUND",    (0, 1), (-1, -1), WHITE),
                    ("BOX",           (0, 0), (-1, -1), 0.3, colors.HexColor("#10b981")),
                    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, colors.HexColor("#f0fdf4")]),
                    ("GRID",          (0, 0), (-1, -1), 0.2, MGRAY),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("TOPPADDING",    (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(fu_tbl)
                story.append(Spacer(1, 0.15 * cm))

            # ── Wellness Guidance
            if wellness:
                well_header = [[Paragraph("Wellness Guidance", REC_H3)]]
                well_rows   = [[Paragraph(f"{w['icon']}  [{w['tip']}]  {w['detail']}", BODY)] for w in wellness]
                well_tbl    = Table(well_header + well_rows, colWidths=[17 * cm])
                well_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, 0), LGRAY),
                    ("BOX",           (0, 0), (-1, -1), 0.3, MGRAY),
                    ("GRID",          (0, 0), (-1, -1), 0.2, MGRAY),
                    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("TOPPADDING",    (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(well_tbl)

            story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(
        "AI Model: ClinicalAI Decision Support Engine  ·  "
        "Prediction Models: XGBoost (Diabetes), Logistic Regression (Heart Risk), "
        "SpaCy NLP (Differential Diagnosis), OpenFDA API (Pharmacovigilance)",
        SMALL
    ))
    story.append(Spacer(1, 0.2 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "⚠  This report is generated by ClinicalAI — an experimental prototype. "
        "It is NOT intended for production clinical use without validated regulatory approval. "
        "All data shown is session-specific and for demonstration purposes only.",
        SMALL,
    ))
    story.append(Paragraph(
        f"Report ID: CAI-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}  |  "
        f"Confidential — Authorized Personnel Only",
        SMALL,
    ))

    doc.build(story)
    return buf.getvalue()
