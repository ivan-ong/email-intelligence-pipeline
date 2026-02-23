from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_emails_returns_list():
    response = client.get("/emails")
    assert response.status_code == 200
    assert "emails" in response.json()
    assert "count" in response.json()


def test_get_emails_filter_by_valid_intent():
    response = client.get("/emails?intent=invoice")
    assert response.status_code == 200


def test_get_emails_filter_by_invalid_intent():
    response = client.get("/emails?intent=nonsense")
    assert response.status_code == 400


def test_get_email_by_invalid_id_returns_404():
    response = client.get("/emails/nonexistent-id-123")
    assert response.status_code == 404