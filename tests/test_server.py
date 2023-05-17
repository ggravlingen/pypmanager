"""Tests for FastAPI server."""

from fastapi.testclient import TestClient
from pypmanager.server import app

client = TestClient(app)


def test_root_endpoint():
    """Test endpoint /."""
    response = client.get("/")
    assert response.status_code == 200
