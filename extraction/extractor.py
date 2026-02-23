import os
import json
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
from typing import Optional

load_dotenv()

# Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --- Data Model ---
class EmailExtraction(BaseModel):
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    intent: str
    key_entities: list[str] = []
    summary: str

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, v):
        allowed = {"invoice", "complaint", "inquiry", "meeting_request", "other"}
        if v not in allowed:
            raise ValueError(f"Intent must be one of {allowed}, got '{v}'")
        return v


# --- Prompt Template ---
PROMPT_TEMPLATE = """
You are a data extraction assistant. Given the email below, extract the following fields and return ONLY a valid JSON object with no extra text, no markdown, no code blocks.

Fields to extract:
- sender_name: the name of the person who sent the email (string or null)
- sender_email: the email address of the sender (string or null)
- intent: classify the email as exactly one of: invoice, complaint, inquiry, meeting_request, other
- key_entities: a list of notable names, companies, amounts, dates, or order numbers mentioned
- summary: one sentence describing what the email is about

Email:
{email_text}
"""


# --- Extraction Function ---
def extract_from_email(email_text: str) -> EmailExtraction:
    prompt = PROMPT_TEMPLATE.format(email_text=email_text)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    raw_text = response.text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {raw_text}") from e

    return EmailExtraction(**data)