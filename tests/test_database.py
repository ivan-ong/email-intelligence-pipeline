from unittest.mock import MagicMock, patch
from database.bigquery_client import generate_email_id, insert_email, email_already_processed
from extraction.extractor import EmailExtraction


def make_extraction(**overrides):
    defaults = {
        "sender_name": "Alice",
        "sender_email": "alice@example.com",
        "intent": "invoice",
        "key_entities": ["Acme Corp"],
        "summary": "Invoice for services.",
    }
    return EmailExtraction(**{**defaults, **overrides})


def test_generate_email_id_is_deterministic():
    # Same content should always produce the same ID
    assert generate_email_id("hello") == generate_email_id("hello")


def test_generate_email_id_differs_for_different_content():
    assert generate_email_id("hello") != generate_email_id("world")


def test_insert_email_success():
    mock_bq = MagicMock()
    mock_bq.insert_rows_json.return_value = []  # no errors

    with patch("database.bigquery_client.get_client", return_value=mock_bq):
        result = insert_email("email_001.txt", "raw content", make_extraction())

    assert result is True
    mock_bq.insert_rows_json.assert_called_once()


def test_insert_email_returns_false_on_bigquery_error():
    mock_bq = MagicMock()
    mock_bq.insert_rows_json.return_value = [{"error": "insert failed"}]

    with patch("database.bigquery_client.get_client", return_value=mock_bq):
        result = insert_email("email_001.txt", "raw content", make_extraction())

    assert result is False


def test_email_already_processed_true():
    mock_row = MagicMock()
    mock_row.count = 1

    mock_bq = MagicMock()
    mock_bq.query.return_value.result.return_value = iter([mock_row])

    with patch("database.bigquery_client.get_client", return_value=mock_bq):
        assert email_already_processed("some email content") is True


def test_email_already_processed_false():
    mock_row = MagicMock()
    mock_row.count = 0

    mock_bq = MagicMock()
    mock_bq.query.return_value.result.return_value = iter([mock_row])

    with patch("database.bigquery_client.get_client", return_value=mock_bq):
        assert email_already_processed("some email content") is False
