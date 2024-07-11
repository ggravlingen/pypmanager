"""Tests for FastAPI server."""

from fastapi.testclient import TestClient
import pytest

from pypmanager.server import app

client = TestClient(app)


@pytest.mark.asyncio()
async def test_root_endpoint() -> None:
    """Test endpoint /."""
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio()
async def test_favicon() -> None:
    """Test endpoint /favicon.ico."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200


@pytest.mark.asyncio()
async def test_graphql_endpoint() -> None:
    """Test endpoint /graphql."""
    query = """
    {
        allGeneralLedger {
            date
            broker
            source
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
