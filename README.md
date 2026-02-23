# Email Intelligence Pipeline

An end-to-end data pipeline that extracts structured information from raw emails using Google Gemini, stores it in BigQuery, and exposes it via a REST API.

## Architecture
```
Raw Emails → Ingestion → Gemini Extraction → BigQuery → FastAPI
```

## Tech Stack

- **Python 3.12**
- **Google Gemini 2.0 Flash** — LLM extraction via prompt engineering
- **Google BigQuery** — Cloud data warehouse
- **FastAPI** — REST API layer
- **Pydantic** — Data validation
- **Pytest** — Testing
- **GitHub Actions** — CI/CD

## Project Structure
```
email-intelligence-pipeline/
├── ingestion/        # Email file loader
├── extraction/       # Gemini prompt + data validation
├── database/         # BigQuery client
├── api/              # FastAPI endpoints
├── tests/            # Unit tests
├── data/             # Sample emails
├── main.py           # Pipeline orchestrator
└── .github/workflows # CI pipeline
```

## Setup

1. Clone the repo
2. Create and activate a virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Create a `.env` file:
```
   GEMINI_API_KEY=your_key_here
   GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials.json
```
5. Add your GCP service account credentials as `gcp-credentials.json`

## Running the Pipeline
```bash
python main.py
```

## Running the API
```bash
python -m uvicorn api.main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/emails` | List all extracted emails |
| GET | `/emails?intent=invoice` | Filter by intent |
| GET | `/emails/{email_id}` | Get a specific email |

## Running Tests
```bash
pytest tests/ -v
```

## Key Design Decisions

- **Idempotent inserts** — emails are hashed to prevent duplicate rows in BigQuery
- **Pydantic validation** — LLM output is validated before hitting the database
- **Prompt sanitization** — handles markdown code blocks that Gemini occasionally wraps around JSON responses
- **Mocked tests** — API tests mock BigQuery so CI runs without cloud credentials