import os
import hashlib
from datetime import datetime, timezone
from google.cloud import bigquery
from dotenv import load_dotenv
from extraction.extractor import EmailExtraction

load_dotenv()

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "maximal-arcade-488308-k6")
DATASET_ID = "email_pipeline"
TABLE_ID = "extracted_emails"
FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

def get_client():
    return bigquery.Client.from_service_account_json("gcp-credentials.json")


def generate_email_id(content: str) -> str:
    """Create a unique reproducible ID from email content."""
    return hashlib.md5(content.encode()).hexdigest()


def insert_email(filename: str, raw_content: str, extraction: EmailExtraction) -> bool:
    email_id = generate_email_id(raw_content)

    row = {
        "email_id": email_id,
        "filename": filename,
        "sender_name": extraction.sender_name,
        "sender_email": extraction.sender_email,
        "intent": extraction.intent,
        "key_entities": extraction.key_entities,
        "summary": extraction.summary,
        "processed_at": datetime.now(timezone.utc).isoformat()
    }

    errors = get_client().insert_rows_json(FULL_TABLE_ID, [row])

    if errors:
        print(f"BigQuery insert errors: {errors}")
        return False

    print(f"Inserted: {email_id} ({filename})")
    return True


def email_already_processed(raw_content: str) -> bool:
    """Prevent duplicate rows by checking if email was already inserted."""
    email_id = generate_email_id(raw_content)
    query = f"""
        SELECT COUNT(*) as count
        FROM `{FULL_TABLE_ID}`
        WHERE email_id = '{email_id}'
    """
    result = get_client().query(query).result()
    for row in result:
        return row.count > 0
    return False