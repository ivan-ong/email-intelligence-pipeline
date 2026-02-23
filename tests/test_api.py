from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_emails_filter_by_invalid_intent():
    response = client.get("/emails?intent=nonsense")
    assert response.status_code == 400


def test_get_email_by_invalid_id_returns_404():
    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter([]))

    with patch("api.main.client") as mock_client:
        mock_client.query.return_value.result.return_value = mock_result
        response = client.get("/emails/nonexistent-id-123")
        assert response.status_code == 404


def test_get_emails_returns_list():
    mock_row = MagicMock()
    mock_row.email_id = "abc123"
    mock_row.filename = "email_001.txt"
    mock_row.sender_name = "John Smith"
    mock_row.sender_email = "john@acme.com"
    mock_row.intent = "invoice"
    mock_row.key_entities = ["Acme Corp", "$4,500"]
    mock_row.summary = "Invoice for October services."
    mock_row.processed_at.isoformat.return_value = "2024-01-01T00:00:00"

    mock_result = MagicMock()
    mock_result.__iter__ = MagicMock(return_value=iter([mock_row]))

    with patch("api.main.client") as mock_client:
        mock_client.query.return_value.result.return_value = mock_result
        response = client.get("/emails")
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert response.json()["emails"][0]["intent"] == "invoice"