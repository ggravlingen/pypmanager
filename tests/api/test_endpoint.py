"""Tests for FastAPI server endpoints."""

from fastapi.testclient import TestClient
import pytest

from pypmanager.api import app
from pypmanager.const import HttpStatusCodes

client = TestClient(app)


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    """Test endpoint /."""
    response = client.get("/")
    assert response.status_code == HttpStatusCodes.OK


@pytest.mark.asyncio
async def test_favicon() -> None:
    """Test endpoint /favicon.ico."""
    response = client.get("/favicon.ico")
    assert response.status_code == HttpStatusCodes.OK


def test_endpoint_status() -> None:
    """Test endpoint /status."""
    response = client.get("/status")
    assert response.status_code == HttpStatusCodes.OK
