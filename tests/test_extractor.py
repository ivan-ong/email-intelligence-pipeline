import pytest
from extraction.extractor import EmailExtraction


def test_valid_extraction():
    # Confirm a fully-populated extraction is accepted and fields are set correctly
    data = {
        "sender_name": "John Smith",
        "sender_email": "john@acme.com",
        "intent": "invoice",
        "key_entities": ["Acme Corp", "$4,500"],
        "summary": "Invoice for October services.",
    }
    result = EmailExtraction(**data)
    assert result.intent == "invoice"
    assert result.sender_email == "john@acme.com"


def test_invalid_intent_raises_error():
    # Intent must be one of the allowed values; Pydantic should reject anything else
    data = {
        "sender_name": "John",
        "sender_email": "john@acme.com",
        "intent": "random_garbage",  # not allowed
        "key_entities": [],
        "summary": "Test.",
    }
    with pytest.raises(Exception):
        EmailExtraction(**data)


def test_missing_optional_fields():
    # sender_name and sender_email are optional and should default to None
    data = {"intent": "other", "summary": "An email with no sender info."}
    result = EmailExtraction(**data)
    assert result.sender_name is None
    assert result.sender_email is None
