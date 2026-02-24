import logging
import os
from fastapi import FastAPI, HTTPException, Query
from google.cloud import bigquery
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Email Intelligence API",
    description="Query structured data extracted from emails",
    version="1.0.0",
)

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "maximal-arcade-488308-k6")
FULL_TABLE_ID = f"{PROJECT_ID}.email_pipeline.extracted_emails"


def get_client():
    """Create BigQuery client lazily so tests can mock it without needing credentials."""
    return bigquery.Client()


@app.get("/")
def health_check():
    try:
        get_client().query("SELECT 1").result()
        return {"status": "ok", "message": "Email Intelligence API is running"}
    except Exception as e:
        logger.error("Health check failed: %s", e)
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.get("/emails")
def get_emails(
    intent: Optional[str] = Query(None), limit: int = Query(10, ge=1, le=100)
):
    allowed = {"invoice", "complaint", "inquiry", "meeting_request", "other"}
    if intent and intent not in allowed:
        raise HTTPException(
            status_code=400, detail=f"Invalid intent. Must be one of: {allowed}"
        )

    where_clause = "WHERE intent = @intent" if intent else ""
    query = f"""
        SELECT *
        FROM `{FULL_TABLE_ID}`
        {where_clause}
        ORDER BY processed_at DESC
        LIMIT @limit
    """  # nosec B608 — only FULL_TABLE_ID (a constant) is interpolated; user input is parameterized
    params = [bigquery.ScalarQueryParameter("limit", "INT64", limit)]
    if intent:
        params.append(bigquery.ScalarQueryParameter("intent", "STRING", intent))
    job_config = bigquery.QueryJobConfig(query_parameters=params)

    client = get_client()
    results = client.query(query, job_config=job_config).result()
    emails = []
    for row in results:
        emails.append(
            {
                "email_id": row.email_id,
                "filename": row.filename,
                "sender_name": row.sender_name,
                "sender_email": row.sender_email,
                "intent": row.intent,
                "key_entities": list(row.key_entities),
                "summary": row.summary,
                "processed_at": row.processed_at.isoformat(),
            }
        )

    return {"count": len(emails), "emails": emails}


@app.get("/emails/{email_id}")
def get_email_by_id(email_id: str):
    query = f"""
        SELECT *
        FROM `{FULL_TABLE_ID}`
        WHERE email_id = @email_id
        LIMIT 1
    """  # nosec B608 — only FULL_TABLE_ID (a constant) is interpolated; user input is parameterized
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("email_id", "STRING", email_id)]
    )

    client = get_client()
    results = client.query(query, job_config=job_config).result()
    for row in results:
        return {
            "email_id": row.email_id,
            "filename": row.filename,
            "sender_name": row.sender_name,
            "sender_email": row.sender_email,
            "intent": row.intent,
            "key_entities": list(row.key_entities),
            "summary": row.summary,
            "processed_at": row.processed_at.isoformat(),
        }

    raise HTTPException(status_code=404, detail=f"Email with id '{email_id}' not found")
