# Functional Requirements
## Sentinel: Spend Anomaly & Forecast Intelligence Dashboard

**Priority key:** 🔴 Must-have (prelim) · 🟡 Should-have (final) · 🟢 Could-have (stretch)

---

## FR-1: Data Ingestion

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1.1 | User can upload a CSV/XLSX file containing spend transactions | 🔴 | File uploads successfully; invalid formats show a clear error |
| FR-1.2 | System validates required columns exist (date, vendor, amount, category) | 🔴 | Missing/malformed columns produce a specific error message, not a crash |
| FR-1.3 | System parses and stores transactions in a normalized structure | 🔴 | Parsed records match source row count ± header/blank rows |
| FR-1.4 | System supports incremental upload (append new data without duplicating) | 🟡 | Re-uploading overlapping data does not create duplicate rows |
| FR-1.5 | System ingests via Cloud Storage trigger (event-driven) | 🟡 | New file in bucket triggers processing automatically, no manual step |

---

## FR-2: Anomaly Detection

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-2.1 | System runs an anomaly detection model (Isolation Forest) across ingested transactions | 🔴 | Model runs without error on sample dataset of 100+ rows |
| FR-2.2 | Each transaction receives an anomaly score and boolean flag | 🔴 | Score + flag stored per transaction and retrievable via API |
| FR-2.3 | System detects exact/near-duplicate transactions (same vendor, amount, ±3 days) | 🔴 | Known duplicate test case is correctly flagged |
| FR-2.4 | System validates math (line items sum to subtotal, tax calculation correct) | 🟡 | Test invoice with deliberate math error is flagged |
| FR-2.5 | Detection sensitivity (contamination rate) is configurable | 🟢 | Adjustable parameter changes number of flagged anomalies predictably |

---

## FR-3: Forecasting

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-3.1 | System generates a spend forecast for the next period using historical data | 🔴 | Forecast produced for ≥1 future period with no runtime error |
| FR-3.2 | Forecast includes confidence interval (upper/lower bound), not a single point estimate | 🔴 | Chart displays shaded confidence band alongside forecast line |
| FR-3.3 | Forecast is broken down by category/vendor where data supports it | 🟡 | User can filter forecast view by category |
| FR-3.4 | System supports "what-if" scenario adjustment (e.g., remove a vendor, see revised forecast) | 🟢 | Adjusting an input recalculates and re-renders the forecast |

---

## FR-4: AI-Generated Insights

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-4.1 | System generates a plain-language explanation for each flagged anomaly | 🔴 | Explanation references the specific transaction's data (vendor, amount, deviation) |
| FR-4.2 | System generates a plain-language summary of forecast trends | 🔴 | Summary mentions direction (up/down) and likely driver where inferable |
| FR-4.3 | System generates a recommended action per anomaly (e.g., "review", "renegotiate") | 🟡 | Recommendation is contextually relevant, not generic boilerplate |
| FR-4.4 | AI calls degrade gracefully if the API is unavailable | 🔴 | UI shows a fallback message instead of breaking the page |

---

## FR-5: Dashboard & Visualization

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-5.1 | Dashboard displays a list/table of flagged anomalies, highlighted visually | 🔴 | Anomalies are visually distinct (e.g., red highlight) from normal rows |
| FR-5.2 | Dashboard displays a forecast chart (line + confidence band) | 🔴 | Chart renders correctly with sample data |
| FR-5.3 | Dashboard displays an insights feed (AI explanations) | 🔴 | Each insight is linked to its source transaction/trend |
| FR-5.4 | User can click an anomaly to see full transaction detail | 🟡 | Detail view shows all original fields + reason for flag |
| FR-5.5 | Dashboard updates in near-real-time after new data is processed | 🟢 | New anomalies appear without a full page reload |

---

## FR-6: Notifications & Audit Trail

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-6.1 | System logs every anomaly detection event with timestamp | 🟡 | Audit log table contains one row per detection run |
| FR-6.2 | System sends a webhook/notification on high-severity anomalies | 🟢 | Configured webhook receives a POST with anomaly summary |

---

## Traceability to Evaluation Rubric

| Rubric Area | Related Requirements |
|---|---|
| Working Core Prototype | FR-1, FR-2, FR-3, FR-5 |
| System Design & Architecture | FR-1.5, FR-6.1 |
| Technology Integration | FR-2 (ML), FR-3 (ML), FR-4 (AI) |
| Innovation | FR-3.2 (confidence bands), FR-4 (explanations), FR-3.4 (what-if) |