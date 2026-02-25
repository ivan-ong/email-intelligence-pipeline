# Email Intelligence Pipeline

An end-to-end data pipeline that extracts structured information from raw emails using Google Gemini, stores it in BigQuery, and exposes it via a REST API.

## Architecture
```
Raw Emails → Gemini Extraction → BigQuery → FastAPI
```

## Tech Stack

- **Python 3.12**
- **Google Gemini 2.5 Flash** — LLM extraction via prompt engineering
- **Google BigQuery** — Cloud data warehouse
- **FastAPI** — REST API layer
- **Pydantic** — Data validation
- **Pytest** — Testing
- **GitHub Actions** — CI/CD (formatting, security scan, tests)

## Project Structure
```
email-intelligence-pipeline/
├── extraction/           # Gemini prompt + Pydantic validation
├── database/             # BigQuery client
├── api/                  # FastAPI endpoints
├── tests/                # Unit tests
├── data/                 # Sample emails
├── main.py               # Pipeline orchestrator
├── compare_extractions.py # Prompt evaluation tool
└── .github/workflows/    # CI pipeline
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
GCP_PROJECT_ID=maximal-arcade-488308-k6
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
| GET | `/emails` | List extracted emails (optional `?intent=` filter, `?limit=`) |
| GET | `/emails/{email_id}` | Get a specific email by ID |

## Running Tests
```bash
pytest tests/ -v
```

## Prompt Evaluation

`compare_extractions.py` diffs stored BigQuery extractions against a fresh re-extraction using the current prompt. Use it after modifying `PROMPT_TEMPLATE` in `extraction/extractor.py` to see what changed.

Requires the API server to be running first:
```bash
# Terminal 1
python -m uvicorn api.main:app --reload

# Terminal 2
python compare_extractions.py
```

## Key Design Decisions

- **Idempotent inserts** — emails are MD5-hashed to prevent duplicate rows in BigQuery
- **Pydantic validation** — LLM output is validated before hitting the database
- **Lazy BigQuery client** — both `database/` and `api/` use a `get_client()` factory so tests can mock credentials
- **Prompt sanitisation** — handles markdown code blocks that Gemini occasionally wraps around JSON responses
- **Mocked tests** — API and database tests mock BigQuery so CI runs without cloud credentials

## Future Enhancements

### Quantitative Prompt Evaluation

`compare_extractions.py` currently shows a visual diff but produces no score. A planned improvement is a golden dataset + scoring mode:

1. **Generate a baseline** — run the current prompt on all emails and save outputs to `data/golden.json`
2. **Score against baseline** — after changing `PROMPT_TEMPLATE`, re-run scoring to measure how much output changed and in which direction

Proposed metrics per field:
- `intent` — exact match accuracy (0 or 1)
- `sender_name` / `sender_email` — exact match
- `key_entities` — F1 score (precision + recall over sets, giving partial credit)
- `summary` — character similarity via `difflib.SequenceMatcher`
- `overall` — weighted average (intent weighted highest at 0.30)

A higher score means the new prompt produces output closer to the baseline. A drop in a specific field pinpoints exactly what regressed.
