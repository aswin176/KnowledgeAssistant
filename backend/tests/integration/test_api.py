"""Integration tests for API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.dependencies import Container, override_container
from app.main import app


class MockGraphRepository:
    async def initialize_schema(self):
        pass

    async def create_node(self, label, properties, merge_keys=None):
        return {"id": "test-id", "name": properties.get("name", ""), **properties}

    async def get_node_by_id(self, node_id):
        if node_id == "exists":
            return {"id": "exists", "name": "Test Person"}
        return None

    async def find_nodes(self, label=None, filters=None, limit=50, offset=0):
        return [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]

    async def create_relationship(self, from_id, to_id, rel_type, properties=None):
        return {"type": rel_type.value, "from_id": from_id, "to_id": to_id}

    async def execute_read_query(self, cypher, params=None):
        return [{"name": "Alice", "id": "1"}]

    async def full_text_search(self, query, limit=20):
        return [{"id": "1", "name": "Alice", "score": 1.0, "labels": ["Person"]}]

    async def get_person_profile(self, person_id):
        if person_id == "exists":
            return {"person": {"id": "exists", "name": "Test"}, "relationships": []}
        return None

    async def get_subgraph(self, node_id, depth=2):
        return {"nodes": [{"id": node_id, "name": "Center"}], "relationships": [], "center_id": node_id}

    async def merge_duplicate_nodes(self, primary_id, duplicate_id):
        return {"primary": {"id": primary_id}, "duplicate": {"id": duplicate_id}}

    async def health_check(self):
        return True


class MockLLM:
    async def generate(self, prompt, system=None):
        if "Cypher" in (system or ""):
            return "MATCH (p:Person) RETURN p.name AS name LIMIT 10"
        return "Here are the results based on your knowledge graph."

    async def stream(self, prompt, system=None):
        yield "Hello"
        yield " World"

    async def health_check(self):
        return True


@pytest.fixture
async def client():
    settings = Settings(
        admin_username="admin",
        admin_password="admin123",
        jwt_secret_key="test-secret",
        app_env="testing",
    )
    container = Container(settings)
    container.graph_repo = MockGraphRepository()  # type: ignore[assignment]
    container.llm = MockLLM()  # type: ignore[assignment]
    container.agent = __import__("app.agent.graph_agent", fromlist=["KnowledgeGraphAgent"]).KnowledgeGraphAgent(
        container.llm, container.graph_repo
    )
    override_container(container)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client):
    response = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAPI:
    @pytest.mark.asyncio
    async def test_root(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        assert "Eutridats" in response.json()["name"]

    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["neo4j"] is True

    @pytest.mark.asyncio
    async def test_login(self, client):
        response = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_invalid(self, client):
        response = await client.post("/api/v1/auth/login", json={"username": "bad", "password": "bad"})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_chat(self, client, auth_headers):
        response = await client.post(
            "/api/v1/chat",
            json={"message": "Who works at Google?"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "conversation_id" in data

    @pytest.mark.asyncio
    async def test_search(self, client, auth_headers):
        response = await client.post(
            "/api/v1/search",
            json={"query": "Alice", "mode": "hybrid"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 0

    @pytest.mark.asyncio
    async def test_create_person(self, client, auth_headers):
        response = await client.post(
            "/api/v1/person",
            json={"name": "John Doe", "email": "john@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_unauthorized(self, client):
        response = await client.post("/api/v1/chat", json={"message": "test"})
        assert response.status_code == 401
