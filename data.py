import numpy as np
import pandas as pd


def generate_sample_data(n_transactions: int = 400, seed: int = 42) -> pd.DataFrame:
    n_transactions = max(int(n_transactions), 13)
    # Assumption: keep at least 3 normal rows so the 3 duplicate-seed copies can be generated without violating the total row count.
    rng = np.random.default_rng(seed)
    normal_count = n_transactions - 10
    category_order = [
        "Office Supplies",
        "Travel",
        "Software",
        "Facilities",
        "Professional Services",
    ]
    vendor_map = {
        "Office Supplies": ["Northwind Office", "Summit Stationery", "Redwood Print House", "Lark & Ledger"],
        "Travel": ["AeroRoute", "Harbor & Pine Travel", "Summit Airways", "Compass Transit"],
        "Software": ["NovaStack", "Cloudpeak", "SignalForge", "Bluebird Apps"],
        "Facilities": ["Metro Facilities", "Hearth & Stone", "Northline Maintenance", "Cedar Works"],
        "Professional Services": ["Brightline Advisory", "Oak & Stone Consulting", "Pioneer Legal", "Verve Strategy"],
    }
    category_prefix = {
        "Office Supplies": "OFF",
        "Travel": "TRV",
        "Software": "SW",
        "Facilities": "FAC",
        "Professional Services": "PS",
    }
    category_amount_ranges = {
        "Office Supplies": (55.0, 210.0),
        "Travel": (180.0, 950.0),
        "Software": (30.0, 170.0),
        "Facilities": (120.0, 520.0),
        "Professional Services": (220.0, 850.0),
    }
    tax_ranges = {
        "Office Supplies": (0.07, 0.12),
        "Travel": (0.08, 0.15),
        "Software": (0.06, 0.10),
        "Facilities": (0.08, 0.13),
        "Professional Services": (0.07, 0.11),
    }
    today = pd.Timestamp.today().normalize()
    earliest_date = today - pd.DateOffset(months=9)
    rows = []

    for i in range(normal_count):
        category = rng.choice(category_order)
        vendor = rng.choice(vendor_map[category])
        day_offset = int(rng.integers(0, (today - earliest_date).days + 1))
        date_value = earliest_date + pd.to_timedelta(day_offset, unit="D")
        low, high = category_amount_ranges[category]
        trend_factor = 1.0 + 0.35 * (i / max(normal_count - 1, 1))
        seasonality_factor = 1.0
        if category == "Travel":
            if date_value.month in (10, 11, 12):
                seasonality_factor += 0.35
            if date_value.month in (6, 7):
                seasonality_factor += 0.18
        elif category == "Software":
            if date_value.month in (1, 2, 3):
                seasonality_factor += 0.2
        elif category == "Facilities":
            if date_value.month in (4, 5, 6):
                seasonality_factor += 0.25
        elif category == "Professional Services":
            if date_value.month in (7, 8, 9):
                seasonality_factor += 0.18
        amount = round(float(rng.uniform(low, high)) * trend_factor * seasonality_factor * float(rng.uniform(0.9, 1.1)), 2)
        tax_rate = float(rng.uniform(*tax_ranges[category]))
        subtotal = round(amount / (1.0 + tax_rate), 2)
        tax_amount = round(amount - subtotal, 2)
        invoice_number = f"{category_prefix[category]}{i + 1:05d}"
        rows.append(
            {
                "transaction_id": None,
                "date": pd.Timestamp(date_value),
                "vendor": vendor,
                "category": category,
                "amount": float(amount),
                "subtotal": float(subtotal),
                "tax_amount": float(tax_amount),
                "invoice_number": invoice_number,
                "is_seeded_anomaly": False,
            }
        )

    duplicate_original_indices = rng.choice(len(rows), size=3, replace=False)
    for duplicate_index in duplicate_original_indices:
        source_row = rows[int(duplicate_index)].copy()
        duplicated_row = source_row.copy()
        duplicate_offset = int(rng.integers(1, 3))
        duplicated_row["date"] = pd.Timestamp(source_row["date"]) + pd.Timedelta(days=duplicate_offset)
        duplicated_row["invoice_number"] = f"DUP{len(rows) + 1:05d}"
        duplicated_row["is_seeded_anomaly"] = True
        rows.append(duplicated_row)

    for outlier_number in range(4):
        category = rng.choice(category_order)
        vendor = rng.choice(vendor_map[category])
        day_offset = int(rng.integers(0, (today - earliest_date).days + 1))
        date_value = earliest_date + pd.to_timedelta(day_offset, unit="D")
        low, high = category_amount_ranges[category]
        typical_amount = float(rng.uniform(low, high))
        amount = round(typical_amount * float(rng.uniform(5.0, 10.0)), 2)
        tax_rate = float(rng.uniform(*tax_ranges[category]))
        subtotal = round(amount / (1.0 + tax_rate), 2)
        tax_amount = round(amount - subtotal, 2)
        rows.append(
            {
                "transaction_id": None,
                "date": pd.Timestamp(date_value),
                "vendor": vendor,
                "category": category,
                "amount": float(amount),
                "subtotal": float(subtotal),
                "tax_amount": float(tax_amount),
                "invoice_number": f"OUT{outlier_number + 1:05d}",
                "is_seeded_anomaly": True,
            }
        )

    for math_error_number in range(3):
        category = rng.choice(category_order)
        vendor = rng.choice(vendor_map[category])
        day_offset = int(rng.integers(0, (today - earliest_date).days + 1))
        date_value = earliest_date + pd.to_timedelta(day_offset, unit="D")
        low, high = category_amount_ranges[category]
        amount = round(float(rng.uniform(low, high)) * float(rng.uniform(0.8, 1.6)), 2)
        tax_rate = float(rng.uniform(*tax_ranges[category]))
        subtotal = round(amount / (1.0 + tax_rate), 2)
        tax_amount = round(amount - subtotal, 2)
        delta = round(float(rng.uniform(6.0, 25.0)), 2)
        incorrect_amount = round(subtotal + tax_amount + delta, 2)
        rows.append(
            {
                "transaction_id": None,
                "date": pd.Timestamp(date_value),
                "vendor": vendor,
                "category": category,
                "amount": float(incorrect_amount),
                "subtotal": float(subtotal),
                "tax_amount": float(tax_amount),
                "invoice_number": f"ERR{math_error_number + 1:05d}",
                "is_seeded_anomaly": True,
            }
        )

    df = pd.DataFrame(rows, columns=[
        "transaction_id",
        "date",
        "vendor",
        "category",
        "amount",
        "subtotal",
        "tax_amount",
        "invoice_number",
        "is_seeded_anomaly",
    ])
    df["transaction_id"] = np.arange(len(df), dtype=int)
    return df


if __name__ == "__main__":
    sample_df = generate_sample_data()
    sample_df.to_csv("sample_spend.csv", index=False)
