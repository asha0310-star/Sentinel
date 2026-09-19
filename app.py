import pandas as pd
import streamlit as st

from anomaly import detect_anomalies
from data import generate_sample_data
from forecast import generate_monthly_forecast, summarize_quarter_forecast
from insights import explain_anomaly, get_gemini_client, summarize_forecast_trend


def get_vendor_forecast(df: pd.DataFrame, vendor: str, periods: int = 3) -> pd.DataFrame | None:
    if vendor in (None, "None"):
        return None
    vendor_df = df[df["vendor"] == vendor].copy()
    if vendor_df.empty:
        return None
    vendor_forecast = generate_monthly_forecast(vendor_df, periods=periods)
    if vendor_forecast is None:
        return None
    vendor_forecast = vendor_forecast.rename(columns={"predicted_amount": f"{vendor} forecast"})
    return vendor_forecast[["period", f"{vendor} forecast"]]


st.set_page_config(page_title="Sentinel Spend Monitor", layout="wide")


use_sample_key = "use_sample_data"
file_key = "uploaded_file"
transactions_key = "transactions"
api_key_key = "gemini_api_key"
client_key = "gemini_client"


if use_sample_key not in st.session_state:
    st.session_state[use_sample_key] = False
if file_key not in st.session_state:
    st.session_state[file_key] = None
if transactions_key not in st.session_state:
    st.session_state[transactions_key] = None
if api_key_key not in st.session_state:
    st.session_state[api_key_key] = st.text_input("Gemini API key", type="password")
if client_key not in st.session_state or st.session_state[client_key] is None:
    if st.session_state[api_key_key]:
        st.session_state[client_key] = get_gemini_client(st.session_state[api_key_key])


uploaded_file = st.file_uploader("Upload spend CSV", type=["csv"])
use_sample = st.button("Use sample data")

if uploaded_file is not None:
    current_upload_id = uploaded_file.name + "|" + str(uploaded_file.size)
else:
    current_upload_id = None

should_process = False
if uploaded_file is not None and st.session_state.get(file_key) != current_upload_id:
    should_process = True
    st.session_state[file_key] = current_upload_id
    st.session_state[use_sample_key] = False
elif use_sample and not st.session_state.get(use_sample_key, False):
    should_process = True
    st.session_state[use_sample_key] = True
    st.session_state[file_key] = None

if should_process:
    with st.spinner("Processing data..."):
        if use_sample:
            transactions = generate_sample_data()
        else:
            try:
                transactions = pd.read_csv(uploaded_file)
            except Exception:
                st.error("Could not read the uploaded CSV. Please upload a valid CSV file.")
                st.stop()
            required_columns = ["date", "vendor", "amount", "category"]
            missing_columns = [col for col in required_columns if col not in transactions.columns]
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                st.stop()
        transactions["date"] = pd.to_datetime(transactions["date"])
        anomalies_df = detect_anomalies(transactions)
        forecast_df = generate_monthly_forecast(transactions)
    st.session_state["transactions"] = transactions
    st.session_state["anomalies_df"] = anomalies_df
    st.session_state["forecast_df"] = forecast_df
    st.session_state["anomaly_explanations"] = {}
    st.session_state["forecast_summary"] = None
    st.session_state["insight_feed"] = []

if "transactions" not in st.session_state or st.session_state["transactions"] is None:
    st.write("Upload a CSV or use the sample data to start the analysis.")
    st.stop()

if "insight_feed" not in st.session_state:
    st.session_state["insight_feed"] = []

transactions = st.session_state["transactions"]
anomalies_df = st.session_state["anomalies_df"]
forecast_df = st.session_state["forecast_df"]

flagged = anomalies_df[anomalies_df["is_anomaly"] == True].sort_values("anomaly_score", ascending=False)
flagged_summary = flagged["severity"].value_counts().to_dict()

if forecast_df is None:
    next_period_text = "Insufficient data"
    forecast_metric_value = "Insufficient data"
else:
    forecast_summary = summarize_quarter_forecast(forecast_df)
    next_period_text = f"${forecast_summary['predicted_amount']:,.0f}"
    forecast_metric_value = f"${forecast_summary['predicted_amount']:,.0f}"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total transactions", len(anomalies_df), delta=f"{flagged_summary.get('high', 0)} high / {flagged_summary.get('medium', 0)} medium / {flagged_summary.get('low', 0)} low")
with col2:
    st.metric("Anomalies found", int(flagged.shape[0]), delta=f"{flagged_summary.get('high', 0)} high / {flagged_summary.get('medium', 0)} medium / {flagged_summary.get('low', 0)} low")
with col3:
    st.metric("Next-period forecast", forecast_metric_value if forecast_df is not None else "Insufficient data")
with col4:
    if "is_seeded_anomaly" in anomalies_df.columns:
        seeded_total = int((anomalies_df["is_seeded_anomaly"] == True).sum())
        if seeded_total > 0:
            caught = int(anomalies_df.loc[anomalies_df["is_seeded_anomaly"] == True, "is_anomaly"].sum())
            precision_text = f"Caught {caught}/{seeded_total} seeded anomalies ({(caught / seeded_total * 100):.0f}%)"
            st.metric("Self-validation precision", precision_text)

anomalies_tab, forecast_tab, insights_tab = st.tabs(["Anomalies", "Forecast", "Insights"])

with anomalies_tab:
    if flagged.empty:
        st.write("No anomalies detected.")
    else:
        anomaly_type_counts = flagged["anomaly_type"].value_counts().rename_axis("anomaly_type").reset_index(name="count")
        if not anomaly_type_counts.empty:
            st.bar_chart(anomaly_type_counts.set_index("anomaly_type"))

        display_df = flagged[["vendor", "date", "amount", "category", "anomaly_type", "severity"]].copy()

        def style_severity(row):
            severity = row["severity"]
            if severity == "high":
                color = "#f4cccc"
            elif severity == "medium":
                color = "#fce5cd"
            else:
                color = "#d9d9d9"
            return [f"background-color: {color}; color: #111111"] * len(row)

        st.dataframe(display_df.style.apply(style_severity, axis=1), use_container_width=True)
        category_avg = anomalies_df.groupby("category")["amount"].mean()
        for _, row in flagged.iterrows():
            key = row["transaction_id"]
            if key not in st.session_state.get("anomaly_explanations", {}):
                with st.spinner("Generating anomaly explanation..."):
                    explanation = explain_anomaly(
                        row.to_dict(),
                        category_avg.get(row["category"], 0.0),
                        st.session_state.get("gemini_client"),
                    )
                st.session_state["anomaly_explanations"][key] = explanation
                st.session_state["insight_feed"].append({"icon": "⚠️", "text": explanation})
            with st.expander(f"{row['vendor']} - ${row['amount']:.2f}"):
                st.write(f"Vendor: {row['vendor']}")
                st.write(f"Date: {row['date']}")
                st.write(f"Category: {row['category']}")
                st.write(f"Amount: ${row['amount']:.2f}")
                st.write(f"Anomaly type: {row['anomaly_type']}")
                st.write(f"Severity: {row['severity']}")
                st.write(st.session_state["anomaly_explanations"][key])

with forecast_tab:
    if forecast_df is None:
        st.info("Insufficient data for monthly forecasting.")
    else:
        monthly_history = transactions[["date", "amount"]].copy()
        monthly_history["date"] = pd.to_datetime(monthly_history["date"]).dt.to_period("M").dt.to_timestamp()
        monthly_history = monthly_history.groupby("date", as_index=False)["amount"].sum()
        monthly_history = monthly_history.rename(columns={"date": "period", "amount": "historical_amount"})
        monthly_history["period"] = monthly_history["period"].dt.strftime("%Y-%m")

        chart_df = monthly_history.merge(
            forecast_df[["period", "predicted_amount", "lower_bound", "upper_bound"]],
            on="period",
            how="outer"
        ).sort_values("period")
        chart_df["historical_amount"] = chart_df["historical_amount"].fillna(0.0)
        chart_df["predicted_amount"] = chart_df["predicted_amount"].fillna(0.0)
        chart_df["lower_bound"] = chart_df["lower_bound"].fillna(0.0)
        chart_df["upper_bound"] = chart_df["upper_bound"].fillna(0.0)

        vendor_options = ["None"] + sorted(transactions["vendor"].dropna().unique().tolist())
        selected_vendor = st.selectbox("Overlay vendor forecast", vendor_options, index=0)

        chart_df = chart_df.set_index("period")
        chart_series = chart_df[["historical_amount", "predicted_amount", "lower_bound", "upper_bound"]].copy()

        if selected_vendor != "None":
            vendor_forecast = get_vendor_forecast(transactions, selected_vendor)
            if vendor_forecast is not None:
                vendor_chart = vendor_forecast.merge(chart_df.reset_index()[['period']], on='period', how='right')
                vendor_chart = vendor_chart.set_index('period')
                vendor_chart[f"{selected_vendor} forecast"] = vendor_chart[f"{selected_vendor} forecast"].fillna(method='ffill').fillna(0.0)
                chart_series = chart_series.join(vendor_chart[[f"{selected_vendor} forecast"]])

        st.line_chart(chart_series)

        if st.session_state.get("forecast_summary") is None:
            with st.spinner("Generating forecast summary..."):
                st.session_state["forecast_summary"] = summarize_forecast_trend(
                    forecast_df,
                    monthly_history,
                    st.session_state.get("gemini_client"),
                )
            st.session_state["insight_feed"].append({"icon": "📈", "text": st.session_state["forecast_summary"]})
        st.write(st.session_state["forecast_summary"])

with insights_tab:
    if not st.session_state.get("insight_feed"):
        st.write("No insights available yet.")
    else:
        with st.container():
            for item in st.session_state["insight_feed"]:
                st.write(f"{item['icon']} {item['text']}")
