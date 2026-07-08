"""Application services."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.core.domain.entities import NodeLabel, NoteEntity, PersonEntity, RelationshipType
from app.core.exceptions import NotFoundError
from app.core.interfaces.repositories import GraphRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class PersonService:
    def __init__(self, graph: GraphRepository) -> None:
        self._graph = graph

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        entity = PersonEntity(name=data["name"], **{k: v for k, v in data.items() if k != "name"})
        props = entity.model_dump(mode="json")
        return await self._graph.create_node(NodeLabel.PERSON, props, merge_keys=["email"] if entity.email else ["name"])

    async def get(self, person_id: str) -> dict[str, Any]:
        profile = await self._graph.get_person_profile(person_id)
        if not profile:
            raise NotFoundError("Person", person_id)
        return profile

    async def update(self, person_id: str, data: dict[str, Any]) -> dict[str, Any]:
        existing = await self._graph.get_node_by_id(person_id)
        if not existing:
            raise NotFoundError("Person", person_id)
        data["updated_at"] = datetime.utcnow().isoformat()
        data["id"] = person_id
        return await self._graph.create_node(NodeLabel.PERSON, {**existing, **data})

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        return await self._graph.find_nodes(NodeLabel.PERSON, limit=limit, offset=offset)

    async def add_relationship(
        self,
        person_id: str,
        rel_type: str,
        target_label: str,
        target_name: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        target = await self._graph.create_node(
            NodeLabel(target_label),
            {"name": target_name},
            merge_keys=["name"],
        )
        return await self._graph.create_relationship(
            person_id,
            target["id"],
            RelationshipType(rel_type),
            properties,
        )


class CompanyService:
    def __init__(self, graph: GraphRepository) -> None:
        self._graph = graph

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._graph.create_node(NodeLabel.COMPANY, data, merge_keys=["name"])

    async def get(self, company_id: str) -> dict[str, Any]:
        node = await self._graph.get_node_by_id(company_id)
        if not node:
            raise NotFoundError("Company", company_id)
        return node

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        return await self._graph.find_nodes(NodeLabel.COMPANY, limit=limit, offset=offset)

    async def get_employees(self, company_id: str) -> list[dict[str, Any]]:
        cypher = """
        MATCH (p:Person)-[r:WORKS_AT|WORKED_AT]->(c:Company {id: $company_id})
        WHERE p.is_active IS NULL OR p.is_active = true
        RETURN p, type(r) AS relationship, properties(r) AS rel_props
        """
        return await self._graph.execute_read_query(cypher, {"company_id": company_id})


class SearchService:
    def __init__(self, graph: GraphRepository) -> None:
        self._graph = graph

    async def search(self, query: str, mode: str = "hybrid", limit: int = 20) -> dict[str, Any]:
        results: list[dict[str, Any]] = []

        if mode in ("fulltext", "hybrid"):
            ft_results = await self._graph.full_text_search(query, limit)
            results.extend(ft_results)

        if mode in ("graph", "hybrid"):
            cypher = """
            MATCH (n)
            WHERE (n.is_active IS NULL OR n.is_active = true)
              AND (toLower(n.name) CONTAINS toLower($query)
                   OR toLower(coalesce(n.title, '')) CONTAINS toLower($query)
                   OR toLower(coalesce(n.industry, '')) CONTAINS toLower($query))
            RETURN n, labels(n) AS labels
            LIMIT $limit
            """
            graph_results = await self._graph.execute_read_query(cypher, {"query": query, "limit": limit})
            for r in graph_results:
                node = dict(r["n"])
                node["_labels"] = r["labels"]
                node["score"] = 0.5
                if not any(existing.get("id") == node.get("id") for existing in results):
                    results.append(node)

        # Deduplicate and rank
        seen_ids: set[str] = set()
        unique: list[dict[str, Any]] = []
        for r in sorted(results, key=lambda x: x.get("score", 0), reverse=True):
            rid = r.get("id")
            if rid and rid in seen_ids:
                continue
            if rid:
                seen_ids.add(rid)
            unique.append(r)

        return {"results": unique[:limit], "total": len(unique), "mode": mode}


class NoteService:
    def __init__(self, graph: GraphRepository) -> None:
        self._graph = graph

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        note = NoteEntity(**data)
        props = note.model_dump(mode="json")
        node = await self._graph.create_node(NodeLabel.NOTE, props)

        if data.get("person_id"):
            await self._graph.create_relationship(
                data["person_id"],
                node["id"],
                RelationshipType.HAS_NOTE,
            )
        return node

    async def get_by_person(self, person_id: str) -> list[dict[str, Any]]:
        cypher = """
        MATCH (p {id: $person_id})-[:HAS_NOTE]->(n:Note)
        WHERE n.is_active IS NULL OR n.is_active = true
        RETURN n
        ORDER BY n.created_at DESC
        """
        results = await self._graph.execute_read_query(cypher, {"person_id": person_id})
        return [dict(r["n"]) for r in results]


class ConversationMemory:
    """In-memory conversation store (session history)."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[dict[str, str]]] = {}

    def get_or_create(self, conversation_id: str | None) -> str:
        cid = conversation_id or str(uuid4())
        if cid not in self._sessions:
            self._sessions[cid] = []
        return cid

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        if conversation_id not in self._sessions:
            self._sessions[conversation_id] = []
        self._sessions[conversation_id].append({"role": role, "content": content})
        # Keep last 50 messages
        self._sessions[conversation_id] = self._sessions[conversation_id][-50:]

    def get_history(self, conversation_id: str) -> list[dict[str, str]]:
        return self._sessions.get(conversation_id, [])

    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())
