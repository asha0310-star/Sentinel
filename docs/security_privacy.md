# Security & Privacy
## Sentinel: Spend Anomaly & Forecast Intelligence Dashboard

---

## 1. Data Classification

| Data Type | Sensitivity | Examples |
|---|---|---|
| Financial transaction data | High | Vendor names, amounts, invoice numbers |
| Uploaded raw files | High | Original CSV/XLSX spend exports |
| AI-generated insights | Medium | Derived text — sensitivity inherited from source data |
| System/audit logs | Low–Medium | Timestamps, action types, actor IDs |

**Note:** No personally identifiable customer data or payment card data is collected by design. If real Averis data is used for testing, treat vendor/pricing data as confidential — do not commit it to the public hackathon GitHub repo.

---

## 2. Data Handling Rules

| Rule | Implementation |
|---|---|
| Never commit real spend data to GitHub | Use `.gitignore` for `/data/real/`; only synthetic/sample data in repo |
| API keys never hardcoded | Store in environment variables / GCP Secret Manager; `.env` excluded from version control |
| Uploaded files stored in private bucket | GCS bucket set to private (no public read access) |
| Database not publicly exposed | Cloud SQL configured with private IP / authorized networks only |

---

## 3. Authentication & Access Control

| Round | Approach |
|---|---|
| **Preliminary** | No auth required (single-user local demo) — acceptable for hackathon scope |
| **Final** | Basic API key or bearer token auth on all endpoints; scoped service account for Cloud Function → Cloud SQL access |

**Principle of least privilege:** The Cloud Function's service account should have write access only to the specific Cloud SQL instance and bucket it needs — not project-wide permissions.

---

## 4. Encryption

| Layer | Standard |
|---|---|
| Data in transit | HTTPS/TLS for all API calls (enforced by Cloud Run default) |
| Data at rest | GCS and Cloud SQL default encryption-at-rest (enabled by default on GCP) |
| Secrets | GCP Secret Manager (not environment files in production) |

---

## 5. Third-Party AI API Usage

| Concern | Mitigation |
|---|---|
| Sending transaction data to an external AI API | Strip/mask vendor names to generic labels ("Vendor A") if using real data in a public demo; use synthetic data for any recorded video |
| API key exposure | Backend-only calls to AI API — frontend never holds the key |
| Rate limiting / cost control | Set budget alerts on GCP; cache AI responses per anomaly to avoid redundant calls |
| Service unavailability | Graceful degradation — show cached/fallback explanation, never expose raw error/stack trace to the user |

---

## 6. Input Validation & Abuse Prevention

| Risk | Control |
|---|---|
| Malicious file upload (oversized, wrong type, malformed CSV) | File type/size validation before processing; row/column schema check |
| Injection via uploaded field values | Parameterized queries only — never string-concatenated SQL |
| Excessive/automated upload abuse | Basic rate limiting on `/upload` endpoint (final round) |

---

## 7. Compliance Considerations (Awareness, Not Full Implementation)

This is a hackathon prototype, not a production financial system. The following are noted for the roadmap/future-work section rather than required for submission:

- **PDPA (Malaysia) / data residency** — if deployed with real organizational data, storage region and consent handling would need review
- **Audit trail immutability** — the `audit_log` table (see Database Design) is a first step toward tamper-evident logging
- **Data retention policy** — uploaded files and derived data would need a defined retention/deletion schedule in production

---

## 8. Hackathon Demo Safety Checklist

- [ ] No real vendor/pricing data appears in the public GitHub repo
- [ ] No real vendor/pricing data appears in the recorded demo video (use synthetic/sample data)
- [ ] `.env` / API keys excluded via `.gitignore`
- [ ] GCS bucket and Cloud SQL instance are not publicly accessible
- [ ] Demo environment uses test/synthetic credentials only
