# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run a single test
pytest tests/test_api.py::test_health_check -v

# Run the pipeline (processes emails in data/ and writes to BigQuery)
python main.py

# Run the API server
python -m uvicorn api.main:app --reload
```

## Before Committing

Always run Black before committing any new or modified Python file, otherwise the CI `black --check .` step will fail:

```bash
black .
```

## Architecture

This is a three-stage email intelligence pipeline:

1. **Extraction** (`extraction/extractor.py`): Reads raw `.txt` email files, sends them to Google Gemini 2.5 Flash with a fixed prompt, and parses the JSON response into a validated Pydantic `EmailExtraction` model. Valid `intent` values are: `invoice`, `complaint`, `inquiry`, `meeting_request`, `other`. Handles markdown code block wrapping in Gemini responses.

2. **Storage** (`database/bigquery_client.py`): Inserts extracted data into BigQuery (`email_pipeline.extracted_emails`). Deduplication is MD5-hash-based — `email_id` is derived from file content, and `email_already_processed()` is checked before each insert.

3. **API** (`api/main.py`): FastAPI server exposing `GET /emails` (with optional `intent` filter and `limit`) and `GET /emails/{email_id}`. Uses a `get_client()` factory function for BigQuery access, which enables mocking in tests.

**Orchestration** (`main.py`): Iterates over `data/*.txt`, skips already-processed files, extracts, and inserts.

## Testing Strategy

Tests run without GCP credentials by patching `api.main.get_client` with `unittest.mock`. `test_extractor.py` validates Pydantic model behavior. `test_api.py` tests endpoints with a mocked BigQuery client.

## Runtime Requirements

A `.env` file and `gcp-credentials.json` service account file are required for actual pipeline runs (not for tests):

```
GEMINI_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials.json
GCP_PROJECT_ID=maximal-arcade-488308-k6
```

`GCP_PROJECT_ID` defaults to `maximal-arcade-488308-k6` if not set.

## Prompt Evaluation

`compare_extractions.py` compares stored BigQuery results against a fresh re-extraction using the current Gemini prompt. Use this after modifying the prompt in `extraction/extractor.py` to see what changed without overwriting stored data.

Requires the API server to be running:
```bash
python -m uvicorn api.main:app --reload
# in a separate terminal:
python compare_extractions.py [--api-url http://localhost:8000] [--limit 100]
```

