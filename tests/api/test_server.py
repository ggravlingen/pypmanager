"""Tests for FastAPI server endpoints."""

import asyncio

from fastapi.testclient import TestClient
import pytest

from pypmanager.api import app
from pypmanager.api.scheduler import scheduler
from pypmanager.api.server import async_lifespan
from pypmanager.const import HttpStatusCodes

client = TestClient(app)


@pytest.mark.asyncio
async def test_async_lifespan() -> None:
    """Test the async_lifespan function."""
    async with async_lifespan(app):
        # Wait a moment to ensure the scheduler has started
        await asyncio.sleep(1)
        assert scheduler.running

    # Wait a moment to ensure the scheduler has shut down
    await asyncio.sleep(1)
    # Check if the scheduler has shut down
    assert not scheduler.running


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
