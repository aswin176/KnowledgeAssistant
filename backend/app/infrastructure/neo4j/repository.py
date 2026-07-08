"""Neo4j graph repository implementation."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.core.domain.entities import NodeLabel, RelationshipType
from app.core.exceptions import GraphQueryError, NotFoundError
from app.core.interfaces.repositories import GraphRepository
from app.core.logging import get_logger
from app.infrastructure.neo4j.connection import Neo4jConnection
from app.infrastructure.neo4j.schema import SCHEMA_CONSTRAINTS, SCHEMA_INDEXES

logger = get_logger(__name__)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _node_to_dict(node: Any) -> dict[str, Any]:
    if node is None:
        return {}
    data = dict(node)
    for key, val in data.items():
        data[key] = _serialize_value(val)
    labels = list(node.labels) if hasattr(node, "labels") else []
    data["_labels"] = labels
    return data


class Neo4jGraphRepository(GraphRepository):
    """Concrete Neo4j implementation of graph operations."""

    def __init__(self, connection: Neo4jConnection) -> None:
        self._conn = connection

    async def initialize_schema(self) -> None:
        for stmt in SCHEMA_CONSTRAINTS + SCHEMA_INDEXES:
            try:
                await self._conn.execute_write(stmt)
            except Exception as exc:
                logger.warning("schema_init_warning", statement=stmt, error=str(exc))
        logger.info("schema_initialized")

    async def create_node(
        self,
        label: NodeLabel,
        properties: dict[str, Any],
        merge_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        now = datetime.utcnow().isoformat()
        props = {
            **properties,
            "id": properties.get("id", str(uuid4())),
            "created_at": properties.get("created_at", now),
            "updated_at": now,
            "is_active": properties.get("is_active", True),
            "version": properties.get("version", 1),
            "source": properties.get("source", "manual"),
            "confidence": properties.get("confidence", 1.0),
        }

        label_str = label.value

        if merge_keys:
            merge_clause = ", ".join(f"n.{k} = $props.{k}" for k in merge_keys)
            query = f"""
            MERGE (n:{label_str} {{{merge_clause}}})
            ON CREATE SET n = $props
            ON MATCH SET n += $props, n.updated_at = $now, n.version = n.version + 1
            RETURN n
            """
            result = await self._conn.execute_write(query, {"props": props, "now": now})
        else:
            query = f"""
            CREATE (n:{label_str})
            SET n = $props
            RETURN n
            """
            result = await self._conn.execute_write(query, {"props": props})

        if not result:
            raise GraphQueryError("Failed to create node")
        return _node_to_dict(result[0]["n"])

    async def get_node_by_id(self, node_id: str) -> dict[str, Any] | None:
        query = """
        MATCH (n {id: $id})
        WHERE n.is_active IS NULL OR n.is_active = true
        RETURN n
        LIMIT 1
        """
        result = await self._conn.execute_read(query, {"id": node_id})
        if not result:
            return None
        return _node_to_dict(result[0]["n"])

    async def find_nodes(
        self,
        label: NodeLabel | None,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        label_clause = f":{label.value}" if label else ""
        where_parts = ["(n.is_active IS NULL OR n.is_active = true)"]
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if filters:
            for i, (key, value) in enumerate(filters.items()):
                param_key = f"f{i}"
                if isinstance(value, str) and "*" in value:
                    where_parts.append(f"n.{key} =~ ${param_key}")
                    params[param_key] = value.replace("*", ".*")
                else:
                    where_parts.append(f"n.{key} = ${param_key}")
                    params[param_key] = value

        where_clause = " AND ".join(where_parts)
        query = f"""
        MATCH (n{label_clause})
        WHERE {where_clause}
        RETURN n
        ORDER BY n.updated_at DESC
        SKIP $offset
        LIMIT $limit
        """
        result = await self._conn.execute_read(query, params)
        return [_node_to_dict(r["n"]) for r in result]

    async def create_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: RelationshipType,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = datetime.utcnow().isoformat()
        props = {
            **(properties or {}),
            "id": str(uuid4()),
            "created_at": now,
            "updated_at": now,
            "source": (properties or {}).get("source", "manual"),
            "confidence": (properties or {}).get("confidence", 1.0),
            "is_active": True,
        }
        query = f"""
        MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
        MERGE (a)-[r:{rel_type.value}]->(b)
        ON CREATE SET r = $props
        ON MATCH SET r += $props, r.updated_at = $now, r.version = coalesce(r.version, 0) + 1
        RETURN r, type(r) AS rel_type, a.id AS from_id, b.id AS to_id
        """
        result = await self._conn.execute_write(
            query, {"from_id": from_id, "to_id": to_id, "props": props, "now": now}
        )
        if not result:
            raise GraphQueryError(f"Failed to create relationship {rel_type.value}")
        row = result[0]
        rel_data = dict(row["r"])
        rel_data["type"] = row["rel_type"]
        rel_data["from_id"] = row["from_id"]
        rel_data["to_id"] = row["to_id"]
        return rel_data

    async def execute_read_query(
        self,
        cypher: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        try:
            return await self._conn.execute_read(cypher, params)
        except Exception as exc:
            logger.error("cypher_read_failed", error=str(exc), query=cypher[:200])
            raise GraphQueryError(f"Query execution failed: {exc}") from exc

    async def full_text_search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        cypher = """
        CALL db.index.fulltext.queryNodes('entitySearch', $query)
        YIELD node, score
        WHERE node.is_active IS NULL OR node.is_active = true
        RETURN node, score, labels(node) AS labels
        ORDER BY score DESC
        LIMIT $limit
        """
        try:
            results = await self._conn.execute_read(cypher, {"query": query, "limit": limit})
        except Exception:
            # Fallback to CONTAINS search if fulltext index unavailable
            cypher_fallback = """
            MATCH (n)
            WHERE (n.is_active IS NULL OR n.is_active = true)
              AND (toLower(n.name) CONTAINS toLower($query)
                   OR toLower(coalesce(n.title, '')) CONTAINS toLower($query)
                   OR toLower(coalesce(n.email, '')) CONTAINS toLower($query))
            RETURN n AS node, 1.0 AS score, labels(n) AS labels
            LIMIT $limit
            """
            results = await self._conn.execute_read(cypher_fallback, {"query": query, "limit": limit})

        return [
            {
                **_node_to_dict(r["node"]),
                "score": r["score"],
                "labels": r["labels"],
            }
            for r in results
        ]

    async def get_person_profile(self, person_id: str) -> dict[str, Any] | None:
        query = """
        MATCH (p {id: $person_id})
        WHERE 'Person' IN labels(p) OR 'Student' IN labels(p)
        OPTIONAL MATCH (p)-[r]->(related)
        WHERE r.is_active IS NULL OR r.is_active = true
        RETURN p,
               collect(DISTINCT {
                   type: type(r),
                   properties: properties(r),
                   node: properties(related),
                   labels: labels(related)
               }) AS relationships
        """
        result = await self._conn.execute_read(query, {"person_id": person_id})
        if not result:
            return None
        row = result[0]
        return {
            "person": _node_to_dict(row["p"]),
            "relationships": row["relationships"],
        }

    async def get_subgraph(self, node_id: str, depth: int = 2) -> dict[str, Any]:
        query = """
        MATCH path = (center {id: $node_id})-[*1..$depth]-(connected)
        WHERE all(r IN relationships(path) WHERE r.is_active IS NULL OR r.is_active = true)
        WITH center, collect(DISTINCT connected) AS nodes, collect(DISTINCT relationships(path)) AS rels
        RETURN center, nodes, rels
        """
        result = await self._conn.execute_read(query, {"node_id": node_id, "depth": depth})
        if not result:
            node = await self.get_node_by_id(node_id)
            if not node:
                raise NotFoundError("Node", node_id)
            return {"nodes": [node], "relationships": [], "center_id": node_id}

        row = result[0]
        center = _node_to_dict(row["center"])
        nodes = [_node_to_dict(n) for n in row["nodes"]]
        all_nodes = [center] + [n for n in nodes if n.get("id") != center.get("id")]

        relationships = []
        for rel_list in row["rels"]:
            for rel in rel_list:
                relationships.append({
                    "type": rel.type,
                    "properties": dict(rel),
                    "start": rel.start_node.get("id"),
                    "end": rel.end_node.get("id"),
                })

        return {
            "nodes": all_nodes,
            "relationships": relationships,
            "center_id": node_id,
        }

    async def merge_duplicate_nodes(
        self,
        primary_id: str,
        duplicate_id: str,
    ) -> dict[str, Any]:
        """Merge duplicate into primary without deleting history."""
        now = datetime.utcnow().isoformat()
        query = """
        MATCH (primary {id: $primary_id}), (duplicate {id: $duplicate_id})
        SET duplicate.is_active = false,
            duplicate.merged_into = $primary_id,
            duplicate.updated_at = $now
        WITH primary, duplicate
        MATCH (duplicate)-[r]->(target)
        MERGE (primary)-[new_r:type(r)]->(target)
        ON CREATE SET new_r = properties(r)
        WITH primary, duplicate, collect(r) AS out_rels
        MATCH (source)-[r2]->(duplicate)
        MERGE (source)-[new_r2:type(r2)]->(primary)
        ON CREATE SET new_r2 = properties(r2)
        RETURN primary, duplicate
        """
        result = await self._conn.execute_write(
            query,
            {"primary_id": primary_id, "duplicate_id": duplicate_id, "now": now},
        )
        if not result:
            raise GraphQueryError("Merge failed")
        return {
            "primary": _node_to_dict(result[0]["primary"]),
            "duplicate": _node_to_dict(result[0]["duplicate"]),
        }

    async def health_check(self) -> bool:
        return await self._conn.health_check()
