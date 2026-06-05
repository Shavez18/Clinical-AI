"""
clinical_records.py
──────────────────────────────────────────────────────────────────────────────
Clinical Records Manager — data access, filtering, and risk computation layer.
Works exclusively with st.session_state.audit_logs to preserve the existing
session workflow without touching any backend or model code.
"""
import pandas as pd
import datetime
import re
import streamlit as st


# ── Severity Mapping ──────────────────────────────────────────────────────────
def _extract_risk_pct(outcome_str: str) -> float:
    """Parse risk percentage from an audit log 'Outcome/Result' string."""
    if not isinstance(outcome_str, str):
        return 0.0
    match = re.search(r"([\d.]+)\s*%", outcome_str)
    return float(match.group(1)) if match else 0.0


def _classify_severity(risk_pct: float) -> str:
    if risk_pct >= 70:
        return "HIGH"
    elif risk_pct >= 30:
        return "MODERATE"
    elif risk_pct > 0:
        return "LOW"
    return "N/A"


# ── Core Data Access ──────────────────────────────────────────────────────────
def get_session_records() -> pd.DataFrame:
    """
    Return the full audit log as a DataFrame with enriched columns.
    Preserves all original columns from the existing audit_logs list.
    """
    logs = st.session_state.get("audit_logs", [])
    # Filter out pure string logs (like auth logs)
    dict_logs = [log for log in logs if isinstance(log, dict)]
    
    if not dict_logs:
        return pd.DataFrame()

    df = pd.DataFrame(dict_logs)

    # Ensure expected columns exist with defaults
    if "Timestamp" not in df.columns:
        df["Timestamp"] = ""
    if "Module" not in df.columns:
        df["Module"] = "Unknown"
    if "Query Overview" not in df.columns:
        df["Query Overview"] = ""
    if "Outcome/Result" not in df.columns:
        df["Outcome/Result"] = ""

    # Parse timestamps
    df["_ts"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Enrich with computed columns
    df["Risk %"] = df["Outcome/Result"].apply(_extract_risk_pct)
    df["Severity"] = df["Risk %"].apply(_classify_severity)
    df["Date"] = df["_ts"].dt.date
    df["Hour"] = df["_ts"].dt.hour

    return df.reset_index(drop=True)


def get_record_stats(df: pd.DataFrame) -> dict:
    """Compute summary statistics for the KPI cards."""
    if df.empty:
        return {
            "total": 0,
            "modules": 0,
            "high_risk": 0,
            "moderate_risk": 0,
            "low_risk": 0,
            "avg_risk": 0.0,
            "module_list": [],
        }

    risk_df = df[df["Risk %"] > 0]
    return {
        "total": len(df),
        "modules": df["Module"].nunique(),
        "high_risk": int((df["Severity"] == "HIGH").sum()),
        "moderate_risk": int((df["Severity"] == "MODERATE").sum()),
        "low_risk": int((df["Severity"] == "LOW").sum()),
        "avg_risk": float(risk_df["Risk %"].mean()) if not risk_df.empty else 0.0,
        "module_list": sorted(df["Module"].dropna().unique().tolist()),
    }


def filter_records(
    df: pd.DataFrame,
    module: str = "All",
    severity: str = "All",
    search: str = "",
    date_range=None,
) -> pd.DataFrame:
    """Apply filter & search to the records DataFrame."""
    if df.empty:
        return df

    filtered = df.copy()

    if module != "All":
        filtered = filtered[filtered["Module"] == module]

    if severity != "All":
        filtered = filtered[filtered["Severity"] == severity]

    if search:
        mask = (
            filtered["Query Overview"].str.contains(search, case=False, na=False)
            | filtered["Module"].str.contains(search, case=False, na=False)
            | filtered["Outcome/Result"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    if date_range and len(date_range) == 2 and date_range[0] and date_range[1]:
        start = pd.Timestamp(date_range[0])
        end = pd.Timestamp(date_range[1])
        filtered = filtered[
            (filtered["_ts"] >= start) & (filtered["_ts"] <= end)
        ]

    return filtered.reset_index(drop=True)


def get_timeline_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return timeline-formatted data sorted oldest→newest."""
    if df.empty:
        return df
    return df.sort_values("_ts", ascending=True).reset_index(drop=True)


def compute_risk_progression(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract rows that have a numeric risk score and return them sorted by
    timestamp — used to draw the longitudinal risk trend line.
    """
    if df.empty:
        return df
    risk_df = df[df["Risk %"] > 0].copy()
    risk_df = risk_df.sort_values("_ts", ascending=True).reset_index(drop=True)
    return risk_df


def generate_ai_summary(df: pd.DataFrame, username: str) -> dict:
    """
    Rule-based clinical narrative generator — no LLM required.
    Returns a dict of narrative sections ready for display.
    """
    stats = get_record_stats(df)
    risk_df = compute_risk_progression(df)

    # Trend detection
    trend = "stable"
    if len(risk_df) >= 3:
        recent = risk_df["Risk %"].iloc[-3:].mean()
        earlier = risk_df["Risk %"].iloc[:-3].mean() if len(risk_df) > 3 else recent
        if recent > earlier + 10:
            trend = "increasing"
        elif recent < earlier - 10:
            trend = "decreasing"

    most_used = (
        df["Module"].value_counts().index[0] if not df.empty else "N/A"
    )

    # Build alert level
    if stats["high_risk"] > 0:
        alert = "ELEVATED — High-risk predictions detected. Immediate clinical review recommended."
        alert_color = "#ff003c"
    elif stats["moderate_risk"] > 0:
        alert = "ADVISORY — Moderate risk profiles present. Longitudinal monitoring advised."
        alert_color = "#ff9d00"
    else:
        alert = "NOMINAL — All queries resolved within low-risk thresholds."
        alert_color = "#00f3ff"

    # Module-specific findings
    module_findings = []
    for mod in df["Module"].unique():
        mod_df = df[df["Module"] == mod]
        avg = mod_df["Risk %"].mean() if mod_df["Risk %"].max() > 0 else None
        if avg is not None:
            module_findings.append(
                f"{mod}: {len(mod_df)} query{'ies' if len(mod_df)>1 else 'y'} — avg risk {avg:.1f}%"
            )
        else:
            module_findings.append(f"{mod}: {len(mod_df)} query{'ies' if len(mod_df)>1 else 'y'}")

    recommendations = []
    if stats["high_risk"] > 0:
        recommendations.append("🔴 Schedule urgent clinical consultation for high-risk patients.")
    if stats["avg_risk"] > 50:
        recommendations.append("🟡 Consider repeat biomarker testing within 30 days.")
    if trend == "increasing":
        recommendations.append("📈 Risk scores trending upward — escalation protocol recommended.")
    if "Diabetes" in df["Module"].values or "Diabetes ADVANCED" in df["Module"].values:
        recommendations.append("💉 Validate fasting glucose and HbA1c with laboratory confirmation.")
    if "Heart" in " ".join(df["Module"].values):
        recommendations.append("❤️ Cardiac risk flagged — ECG and lipid panel advised.")
    if not recommendations:
        recommendations.append("✅ No immediate escalation required. Routine monitoring protocol.")

    return {
        "username": username,
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert": alert,
        "alert_color": alert_color,
        "trend": trend,
        "most_used_module": most_used,
        "stats": stats,
        "module_findings": module_findings,
        "recommendations": recommendations,
    }
