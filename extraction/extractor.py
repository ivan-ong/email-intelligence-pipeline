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
You are a data extraction assistant. Given the email below, extract the following
fields and return ONLY a valid JSON object with no extra text, no markdown, no code blocks.

Fields to extract:
- sender_name:    the name of the person who sent the email (string or null).
                  If the email is automated or a forwarded chain, use the original
                  human sender if clearly identifiable, otherwise use the From field.
- sender_email:   the email address of the sender (string or null).
                  If the email is automated or a forwarded chain, use the original
                  human sender if clearly identifiable, otherwise use the From field.
- intent:         classify as exactly one of the following:
                    invoice         — a vendor requesting payment or referencing a bill
                    complaint       — expressing dissatisfaction, disputing, or demanding resolution
                    inquiry         — asking questions or requesting information before a decision
                    meeting_request — proposing or scheduling a call, meeting, or demo
                    other           — none of the above
- key_entities:   a list of people, companies, monetary amounts, order/invoice/case
                  numbers, and specific dates mentioned. Omit generic time zones,
                  URLs, and phone numbers.
- summary:        one sentence stating who is writing, to whom, and what action
                  or response they are requesting

Email:
{email_text}
"""


# --- Extraction Function ---
def extract_from_email(email_text: str) -> EmailExtraction:
    prompt = PROMPT_TEMPLATE.format(email_text=email_text)

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw_text = response.text.strip()

    # Strip markdown code blocks if Gemini wraps the response
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {raw_text}") from e

    return EmailExtraction(**data)
