from __future__ import annotations

import pandas as pd
from google import genai


def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)


def explain_anomaly(row: dict, category_avg_amount: float, client) -> str:
    vendor = row.get("vendor", "unknown vendor")
    category = row.get("category", "unknown category")
    amount = row.get("amount", 0.0)
    date_value = row.get("date", "unknown date")
    anomaly_type = row.get("anomaly_type", "unknown")
    severity = row.get("severity", "unknown")

    prompt = (
        f"Explain in exactly 2-3 sentences why this transaction was flagged. "
        f"Vendor: {vendor}. Category: {category}. Amount: ${amount:.2f}. "
        f"Date: {date_value}. Category average amount: ${category_avg_amount:.2f}. "
        f"Anomaly type: {anomaly_type}. Severity: {severity}. "
        "Keep it plain-language and specific to this transaction."
    )

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except Exception:
        return (
            f"This {vendor} transaction of ${amount:.2f} was flagged as a {anomaly_type} "
            f"({severity} severity). AI explanation unavailable."
        )


def summarize_forecast_trend(monthly_forecast_df: pd.DataFrame, historical_monthly: pd.DataFrame, client) -> str:
    if monthly_forecast_df.empty or historical_monthly.empty:
        return "Forecast generated — AI summary unavailable"

    last_hist = historical_monthly.iloc[-1]["amount"] if "amount" in historical_monthly.columns else historical_monthly.iloc[-1].iloc[1]
    forecast_total = float(monthly_forecast_df["predicted_amount"].sum())
    change_pct = ((forecast_total - last_hist) / last_hist) * 100 if last_hist else 0.0
    direction = "up" if change_pct > 0 else "down" if change_pct < 0 else "flat"
    prompt = (
        "Write one sentence summarizing the spend forecast direction. "
        f"Compare the latest historical month (${last_hist:.2f}) to the forecast total (${forecast_total:.2f}), "
        f"which is approximately {abs(change_pct):.1f}% {direction}. "
        "Keep it plain-language and concise."
    )

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()
    except Exception:
        return f"Forecast generated — AI summary unavailable. Predicted total: ${forecast_total:.2f}."
