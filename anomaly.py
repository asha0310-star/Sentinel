import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["anomaly_score"] = 0.0
    result["is_anomaly"] = False
    result["anomaly_type"] = "none"
    result["severity"] = "none"

    iso = IsolationForest(contamination=0.05, random_state=42)
    amount_values = result["amount"].to_numpy().reshape(-1, 1)
    iso.fit(amount_values)
    result["anomaly_score"] = -iso.decision_function(amount_values)

    math_mask = np.abs((result["subtotal"] + result["tax_amount"]) - result["amount"]) > 0.01
    result.loc[math_mask, "anomaly_type"] = "math_error"
    result.loc[math_mask, "is_anomaly"] = True

    duplicate_candidates = result.loc[~result["anomaly_type"].eq("math_error"), ["vendor", "amount", "date", "invoice_number"]].copy()
    for _, group in duplicate_candidates.groupby(["vendor", "amount"], sort=False):
        ordered = group.sort_values("date")
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                left = ordered.iloc[i]
                right = ordered.iloc[j]
                if left["invoice_number"] == right["invoice_number"]:
                    continue
                if abs((right["date"] - left["date"]).days) <= 3:
                    result.loc[right.name, "anomaly_type"] = "duplicate"
                    result.loc[right.name, "is_anomaly"] = True
                    break

    unflagged_mask = result["anomaly_type"].eq("none")
    if unflagged_mask.any():
        unflagged_amounts = result.loc[unflagged_mask, "amount"].to_numpy().reshape(-1, 1)
        unflagged_model = IsolationForest(contamination=0.05, random_state=42)
        unflagged_model.fit(unflagged_amounts)
        unflagged_predictions = unflagged_model.predict(unflagged_amounts)
        flagged_outliers = result.index[unflagged_mask][unflagged_predictions == -1]
        result.loc[flagged_outliers, "anomaly_type"] = "outlier"
        result.loc[flagged_outliers, "is_anomaly"] = True

    result.loc[result["anomaly_type"].eq("none"), "is_anomaly"] = False
    result.loc[result["anomaly_type"].eq("none"), "severity"] = "none"

    flagged_rows = result[result["is_anomaly"]].copy()
    if not flagged_rows.empty:
        rule_threshold = flagged_rows["anomaly_score"].quantile(2 / 3)
        outlier_threshold_1 = flagged_rows["anomaly_score"].quantile(1 / 3)
        outlier_threshold_2 = flagged_rows["anomaly_score"].quantile(2 / 3)

        for idx, row in flagged_rows.iterrows():
            if row["anomaly_type"] in ("math_error", "duplicate"):
                result.loc[idx, "severity"] = "high" if row["anomaly_score"] >= rule_threshold else "medium"
            elif row["anomaly_type"] == "outlier":
                if row["anomaly_score"] >= outlier_threshold_2:
                    result.loc[idx, "severity"] = "high"
                elif row["anomaly_score"] >= outlier_threshold_1:
                    result.loc[idx, "severity"] = "medium"
                else:
                    result.loc[idx, "severity"] = "low"

    result["is_anomaly"] = result["anomaly_type"].ne("none")
    result["severity"] = result["severity"].fillna("none")
    return result
