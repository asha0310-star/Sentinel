from __future__ import annotations

import pandas as pd
from prophet import Prophet


def generate_monthly_forecast(df: pd.DataFrame, periods: int = 3) -> pd.DataFrame | None:
    monthly = df[["date", "amount"]].copy()
    monthly["date"] = pd.to_datetime(monthly["date"]).dt.to_period("M").dt.to_timestamp()
    monthly = monthly.groupby("date", as_index=False)["amount"].sum()
    monthly = monthly.rename(columns={"date": "ds", "amount": "y"})

    if monthly["ds"].nunique() < 4:
        return None

    prophet_model = Prophet()
    prophet_model.fit(monthly)
    future = prophet_model.make_future_dataframe(periods=periods, freq="M")
    forecast = prophet_model.predict(future)
    last_history = monthly["ds"].max()
    future_rows = forecast[forecast["ds"] > last_history].copy().tail(periods).reset_index(drop=True)

    result = pd.DataFrame({
        "period": future_rows["ds"].dt.strftime("%Y-%m"),
        "predicted_amount": future_rows["yhat"].astype(float),
        "lower_bound": future_rows["yhat_lower"].astype(float),
        "upper_bound": future_rows["yhat_upper"].astype(float),
    })
    return result


def summarize_quarter_forecast(monthly_forecast_df: pd.DataFrame) -> dict:
    return {
        "predicted_amount": float(monthly_forecast_df["predicted_amount"].sum()),
        "lower_bound": float(monthly_forecast_df["lower_bound"].sum()),
        "upper_bound": float(monthly_forecast_df["upper_bound"].sum()),
    }
