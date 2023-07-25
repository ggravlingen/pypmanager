"""Tests for FastAPI server."""

from fastapi.testclient import TestClient

from pypmanager.server import app
import pytest

client = TestClient(app)


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test endpoint /."""
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_graphql_endpoint():
    """Test endpoint /graphql"""
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
