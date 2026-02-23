import os
from fastapi import FastAPI, HTTPException, Query
from google.cloud import bigquery
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI(
    title="Email Intelligence API",
    description="Query structured data extracted from emails",
    version="1.0.0"
)

client = bigquery.Client.from_service_account_json("gcp-credentials.json")

PROJECT_ID = "maximal-arcade-488308-k6"
FULL_TABLE_ID = f"{PROJECT_ID}.email_pipeline.extracted_emails"


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Email Intelligence API is running"}


@app.get("/emails")
def get_emails(
    intent: Optional[str] = Query(None, description="Filter by intent: invoice, complaint, inquiry, meeting_request, other"),
    limit: int = Query(10, description="Number of results to return", ge=1, le=100)
):
    where_clause = ""
    if intent:
        allowed = {"invoice", "complaint", "inquiry", "meeting_request", "other"}
        if intent not in allowed:
            raise HTTPException(status_code=400, detail=f"Invalid intent. Must be one of: {allowed}")
        where_clause = f"WHERE intent = '{intent}'"

    query = f"""
        SELECT *
        FROM `{FULL_TABLE_ID}`
        {where_clause}
        ORDER BY processed_at DESC
        LIMIT {limit}
    """

    results = client.query(query).result()
    emails = []
    for row in results:
        emails.append({
            "email_id": row.email_id,
            "filename": row.filename,
            "sender_name": row.sender_name,
            "sender_email": row.sender_email,
            "intent": row.intent,
            "key_entities": list(row.key_entities),
            "summary": row.summary,
            "processed_at": row.processed_at.isoformat()
        })

    return {"count": len(emails), "emails": emails}


@app.get("/emails/{email_id}")
def get_email_by_id(email_id: str):
    query = f"""
        SELECT *
        FROM `{FULL_TABLE_ID}`
        WHERE email_id = '{email_id}'
        LIMIT 1
    """

    results = client.query(query).result()
    for row in results:
        return {
            "email_id": row.email_id,
            "filename": row.filename,
            "sender_name": row.sender_name,
            "sender_email": row.sender_email,
            "intent": row.intent,
            "key_entities": list(row.key_entities),
            "summary": row.summary,
            "processed_at": row.processed_at.isoformat()
        }

    raise HTTPException(status_code=404, detail=f"Email with id '{email_id}' not found")