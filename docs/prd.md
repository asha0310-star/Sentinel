# Product Requirements Document (PRD)
## Sentinel: Spend Anomaly & Forecast Intelligence Dashboard

**Version:** 1.0
**Event:** Averis x Monash Hackathon 2026
**Status:** Draft — Preliminary Round

---

## 1. Executive Summary

Sentinel is a data-driven solution designed to help finance and shared services teams proactively identify and address spending anomalies. Shared services and finance teams review spending reactively — problems are caught weeks after money has already been lost, and budgets are set by guesswork rather than evidence. This product ingests historical and incoming spend data, automatically detects unusual transactions, forecasts near-term spending, and uses AI to explain *why* something looks wrong and *what to do about it*.

**One-liner:** A dashboard that tells finance teams what's wrong today, what's coming next quarter, and why — before it costs them money.

---

## 2. Problem Statement

| Problem | Current State | Cost |
|---|---|---|
| Anomalous spend goes unnoticed | Manual, spot-check review | Duplicate payments, price creep, fraud |
| No forward visibility | Budgets set by last year + guesswork | Overspend surprises, poor negotiation timing |
| No "why" behind the numbers | Raw tables/spreadsheets | Analysts spend hours investigating manually |

---

## 3. Goals & Objectives

- **G1:** Automatically flag anomalous transactions with >90% precision on labeled test data
- **G2:** Forecast next-quarter spend with a clearly communicated confidence interval
- **G3:** Generate a plain-language, actionable explanation for every flagged anomaly
- **G4:** Present all of the above in a single, non-technical dashboard

**Non-goals (out of scope for hackathon):**
- Multi-tenant / multi-organization support
- Full accounting system integration (ERP write-back)
- Automated vendor negotiation or payment actions

---

## 4. Target Users

| Persona | Need |
|---|---|
| **Finance/Procurement Analyst** | Wants to catch bad invoices fast, without manually cross-checking spreadsheets |
| **Finance Manager** | Wants a forward-looking view of budget risk, not just historical reporting |
| **Shared Services Lead (Averis)** | Wants measurable reduction in audit hours and leakage (duplicate/overpaid spend) |

---

## 5. Key Features (Summary)

1. **Data Ingestion** — upload historical spend data (CSV/XLSX)
2. **Anomaly Detection** — ML-based outlier detection on transactions
3. **Forecasting** — time-series prediction of upcoming spend with confidence bands
4. **AI-Generated Insights** — natural-language explanation + recommendation per anomaly/trend
5. **Interactive Dashboard** — anomalies, forecast chart, insights feed, drill-down detail

*(Full breakdown in `02_Functional_Requirements.md`)*

---

## 6. Success Metrics

| Metric | Target (Prelim) | Target (Final) |
|---|---|---|
| Anomaly detection precision (on labeled sample) | ≥ 85% | ≥ 90% |
| Forecast generated for next period | Yes, with confidence band | Yes, with what-if scenarios |
| Explanation generated per flagged anomaly | Yes | Yes, with recommended action |
| Dashboard load time | < 3s for sample dataset | < 3s for full dataset |
| Judge-facing demo runs end-to-end without manual intervention | Yes | Yes |

---

## 7. Scope

### Preliminary Round
- Upload 2–3 quarters of sample spend data
- Run anomaly detection (Isolation Forest) on transactions
- Run forecast (Prophet) for next quarter
- Generate 3+ AI explanations via Gemini/Claude API
- Dashboard showing anomalies, forecast chart, and insights
- GitHub repo + README + 5-min video

### Final Round
- Persistent storage (Cloud SQL) with real ingestion pipeline
- Confidence-interval visualization + drill-down per anomaly
- "What-if" scenario simulation (e.g., vendor consolidation impact)
- Deployed, publicly accessible live demo

---

## 8. Assumptions & Constraints

- Sample or synthetic spend data will be used if real Averis data isn't available in time
- Forecasting accuracy is inherently probabilistic — communicated via confidence intervals, not false precision
- Hackathon timeline (36–48 hrs for prelim) limits model complexity — favor proven libraries (Prophet, scikit-learn) over custom models

---

## 9. Evaluation Alignment (Hackathon Rubric)

| Rubric Criterion | How This Product Addresses It |
|---|---|
| Working Core Prototype (25 pts) | End-to-end: upload → detect → forecast → explain → display |
| System Design & Architecture (15 pts) | Clear separation: ingestion, ML services, API, UI (see `system_architecture.md`) |
| Technology Integration (15 pts) | Native AI (Gemini/Claude) + Cloud (GCP) + ML (scikit-learn, Prophet) |
| Problem Understanding (10 pts) | Directly targets shared-services audit/budget pain points |
| Innovation (10 pts) | Combines anomaly detection + forecasting + NL explanation — not just rule-checking |
| Practical Value (10 pts) | Shifts finance teams from reactive to predictive |

---

