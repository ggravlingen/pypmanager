"""Tests for FastAPI server endpoints."""

from fastapi.testclient import TestClient
import pytest

from pypmanager.api import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """Test endpoint /."""
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_favicon() -> None:
    """Test endpoint /favicon.ico."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
