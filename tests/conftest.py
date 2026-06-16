import pytest
import os

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set mock environment variables for testing."""
    monkeypatch.setenv("GA4_PROPERTY_ID", "123456789")
    monkeypatch.setenv("CREDENTIALS_FILE", "mock_credentials.json")
