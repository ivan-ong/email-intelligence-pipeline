import pytest
from extraction.extractor import EmailExtraction

def test_valid_extraction():
    data = {
        "sender_name": "John Smith",
        "sender_email": "john@acme.com",
        "intent": "invoice",
        "key_entities": ["Acme Corp", "$4,500"],
        "summary": "Invoice for October services."
    }
    result = EmailExtraction(**data)
    assert result.intent == "invoice"
    assert result.sender_email == "john@acme.com"

def test_invalid_intent_raises_error():
    data = {
        "sender_name": "John",
        "sender_email": "john@acme.com",
        "intent": "random_garbage",  # not allowed
        "key_entities": [],
        "summary": "Test."
    }
    with pytest.raises(Exception):
        EmailExtraction(**data)

def test_missing_optional_fields():
    data = {
        "intent": "other",
        "summary": "An email with no sender info."
    }
    result = EmailExtraction(**data)
    assert result.sender_name is None
    assert result.sender_email is None