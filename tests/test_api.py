from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from api.main import app

client = TestClient(app)


def test_health_check(mock_bq_client):
    # Verify the root endpoint returns a 200 with the expected status field
    mock_bq_client.query.return_value.result.return_value = iter([])
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_emails_filter_by_invalid_intent():
    # Intent values are restricted to the allowed set; anything else should return 400
    response = client.get("/emails?intent=nonsense")
    assert response.status_code == 400


def test_get_email_by_invalid_id_returns_404(mock_bq_client):
    # Mock BigQuery to return an empty result set, simulating a missing email ID
    mock_bq_client.query.return_value.result.return_value = iter([])
    response = client.get("/emails/nonexistent-id-123")
    assert response.status_code == 404


def test_get_emails_returns_list(mock_bq_client):
    # Build a fake BigQuery row with all fields the API reads
    mock_row = MagicMock()
    mock_row.email_id = "abc123"
    mock_row.filename = "email_001.txt"
    mock_row.sender_name = "John Smith"
    mock_row.sender_email = "john@acme.com"
    mock_row.intent = "invoice"
    mock_row.key_entities = ["Acme Corp", "$4,500"]
    mock_row.summary = "Invoice for October services."
    mock_row.processed_at.isoformat.return_value = "2024-01-01T00:00:00"

    # Wire the fake row into the mock BigQuery client
    mock_bq_client.query.return_value.result.return_value = iter([mock_row])

    response = client.get("/emails")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["emails"][0]["intent"] == "invoice"
