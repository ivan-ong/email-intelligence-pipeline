import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_bq_client():
    mock_bq = MagicMock()
    with patch("api.main.get_client", return_value=mock_bq):
        yield mock_bq
