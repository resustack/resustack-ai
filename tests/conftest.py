"""Pytest configuration and fixtures."""

import pytest
from backend.api.rest.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)
