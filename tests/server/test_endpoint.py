"""Tests for FastAPI server."""
from fastapi.testclient import TestClient
import pytest

from pypmanager.server import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test endpoint /."""
    response = client.get("/")
    assert response.status_code == 200  # noqa: PLR2004


@pytest.mark.asyncio
async def test_graphql_endpoint():
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
    assert response.status_code == 200  # noqa: PLR2004
