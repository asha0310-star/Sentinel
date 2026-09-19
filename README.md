# Sentinel

**Detect spending anomalies today. Forecast budget risk tomorrow. Act with intelligence.**

Sentinel is an AI-powered financial intelligence dashboard that automatically detects unusual transactions, predicts next-quarter spending, and explains why helping finance teams shift from reactive to proactive budget management.

---

## Quick Facts

- **What it does:** Ingests spend data → detects anomalies (ML) → forecasts future spend (time-series) → generates AI explanations
- **For whom:** Finance teams, shared services centers, procurement analysts
- **Built with:** Python (FastAPI), Google Cloud (GCS + Cloud Functions + Cloud SQL), Prophet, scikit-learn, Gemini/Claude API, Streamlit
- **Status:** Averis x Monash Hackathon 2026 submission

---

## Key Features

✨ **Anomaly Detection** — Automatically flags unusual transactions (outliers, duplicates, math errors) with explainable scores

📈 **Spend Forecasting** — Predicts next-period spend with confidence intervals, not guesses

🧠 **AI Insights** — Plain-language explanations + recommendations for every flagged issue

📊 **Interactive Dashboard** — Real-time anomalies, forecast charts, and actionable insights in one view

---

## Getting Started

### Prerequisites
- Python 3.9+
- Google Cloud SDK (optional for local dev; required for cloud deployment)
- API keys: Gemini or Claude (for AI explanations)

### Quick Start

```bash
# Clone repo
git clone https://github.com/yourusername/sentinel.git
cd sentinel

# Install dependencies
pip install streamlit pandas numpy scikit-learn prophet google-genai

# Run the Streamlit dashboard
streamlit run app.py
```

Visit `http://localhost:8501` to access the dashboard.

### Roadmap / Final Round

This repository still contains the original future-round architecture notes for a separate production system, but that is not the runnable MVP in this branch.

- Production direction: FastAPI + PostgreSQL + Google Cloud deployment
- Not part of the current single-file Streamlit build
- If you are working on the hackathon MVP, use only the Streamlit flow above

### Sample Data

If you don't have spend data, use the included synthetic dataset:

```bash
python scripts/generate_sample_data.py
```

This creates `sample_spend.csv` with realistic spend patterns and seeded anomalies for testing.
The dataset includes `seeded_anomaly`, `anomaly_type`, and `anomaly_group` columns so you can benchmark detection precision against known ground truth.

---

## Project Structure

```
sentinel/
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── .env.example                    # Environment template (copy to .env)
├── app.py                          # Streamlit dashboard
├── api/
│   ├── main.py                    # FastAPI server
│   ├── routes/
│   │   ├── upload.py
│   │   ├── anomalies.py
│   │   ├── forecasts.py
│   │   └── insights.py
│   └── models/
│       ├── anomaly_detector.py   # Isolation Forest wrapper
│       ├── forecaster.py         # Prophet wrapper
│       └── insight_generator.py  # Gemini/Claude integration
├── database/
│   ├── schema.sql                # PostgreSQL schema
│   └── models.py                 # SQLAlchemy ORM models
├── scripts/
│   ├── generate_sample_data.py
│   └── deploy_to_gcp.sh          # Cloud Run deployment script
└── docs/
    ├── prd.md
    ├── functional_requirements.md
    ├── system_architecture.md
    ├── database_design.md
    ├── api_specification.md
    ├── uiux_specification.md
    ├── security_privacy.md
```

---

## How It Works

1. **Upload** — Drag-and-drop your spend data (CSV/XLSX)
2. **Detect** — Isolation Forest identifies outlier transactions
3. **Forecast** — Prophet time-series model predicts next quarter's spending
4. **Explain** — Gemini/Claude API generates human-readable insights
5. **Act** — Dashboard shows flagged anomalies + recommendations

---

## Architecture

**Preliminary Round (Hackathon MVP):**
- Streamlit frontend (local or cloud-hosted)
- FastAPI backend (local or Cloud Run)
- In-memory/SQLite data store
- Public AI API calls (Gemini/Claude)

**Final Round (If selected):**
- Cloud SQL (PostgreSQL) for persistent storage
- Cloud Functions for event-driven processing
- Cloud Run for API deployment
- Fully serverless pipeline

See [`system_architecture.md`](docs/system_architecture.md) for details.

---

## API Endpoints

**Local dev (if running the backend):** `http://localhost:8000/api/v1`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/upload` | Upload spend data |
| GET | `/anomalies` | List flagged transactions |
| GET | `/anomalies/{id}` | Get anomaly detail + AI explanation |
| GET | `/forecasts` | Get next-period spend forecast |
| GET | `/health` | Health check |

See [`api_specification.md`](docs/api_specification.md) for full details.

---

## Configuration

Edit `.env` to set:

```bash
# AI API
GEMINI_API_KEY=<your-key>
# or
CLAUDE_API_KEY=<your-key>

# Google Cloud (optional, for deployed version)
GCP_PROJECT_ID=<your-project>
GCS_BUCKET_NAME=<bucket-name>

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost/sentinel
```

---

## Key Technologies

- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Frontend:** Streamlit (with Vega-Lite charts)
- **ML/Forecasting:** scikit-learn (Isolation Forest), Prophet
- **AI Explanations:** Gemini or Claude API
- **Cloud:** Google Cloud Platform (GCS, Cloud SQL, Cloud Functions, Cloud Run)
- **Database:** PostgreSQL (production) / SQLite (dev)

---

## Testing

```bash
# Run unit tests
pytest tests/

# Test anomaly detection
python -m pytest tests/test_anomaly_detector.py -v

# Test forecasting
python -m pytest tests/test_forecaster.py -v
```

---

## Deployment (Final Round)

### To Google Cloud Run (Production-Ready)

```bash
# Build Docker image
docker build -t sentinel:latest .

# Deploy to Cloud Run
gcloud run deploy sentinel \
  --image sentinel:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY

# Deploy Streamlit frontend
streamlit run app.py --server.address 0.0.0.0 --server.port 8080
```

See [`scripts/deploy_to_gcp.sh`](scripts/deploy_to_gcp.sh) for automated deployment.

---

## Demo Video

See the 5-minute demo walkthrough in the [hackathon submission](link-to-video).

---

## Documentation

- **Product & Design:** See [`docs/`](docs/) for full specifications (PRD, architecture, database schema, API, UI/UX, security,)
- **Functional Requirements:** [`functional_requirements.md`](docs/02_Functional_Requirements.md)
- **System Architecture:** [`system_Architecture.md`](docs/03_System_Architecture.md)

---

## Team

**Averis x Monash Hackathon 2026 Submission**

| Role | Name |
|------|------|
| ML / Algorithms Lead | Abdul hakim shaon |
| Backend / Cloud | Sumaiya rana ridy and Abdul Hakim Shaon |
| Frontend / Visualization | Sumaiya rana ridy |

---

## License

MIT License — See LICENSE file for details.

---

## Feedback & Issues

Found a bug? Have a feature request? Open an issue on GitHub or reach out to the team on Discord during the hackathon.

---

## Acknowledgments

- Prophet (Meta) for time-series forecasting
- scikit-learn for anomaly detection
- Google Cloud for serverless infrastructure
- Gemini/Claude for AI-powered insights
