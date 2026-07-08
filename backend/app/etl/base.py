"""Base ETL pipeline and duplicate detection."""

from abc import ABC, abstractmethod
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any
from uuid import uuid4

from app.core.domain.entities import ImportRecord, NodeLabel
from app.core.interfaces.repositories import GraphRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseETLPipeline(ABC):
    """Base class for all import pipelines."""

    def __init__(self, graph_repo: GraphRepository) -> None:
        self._graph = graph_repo

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        ...

    @abstractmethod
    async def extract(self, file_path: str, **kwargs: Any) -> list[dict[str, Any]]:
        ...

    async def transform(self, records: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
        """Normalize records to graph-ready format."""
        transformed = []
        now = datetime.utcnow().isoformat()
        for record in records:
            normalized = {
                "label": record.get("label", NodeLabel.PERSON.value),
                "properties": {
                    "id": record.get("id", str(uuid4())),
                    "name": record.get("name", "").strip(),
                    "source": source,
                    "created_at": now,
                    "updated_at": now,
                    "confidence": record.get("confidence", 0.8),
                    "is_active": True,
                    "version": 1,
                },
                "relationships": record.get("relationships", []),
                "merge_keys": record.get("merge_keys", ["name"]),
            }
            for key, value in record.items():
                if key not in ("label", "relationships", "merge_keys", "id"):
                    if value is not None and str(value).strip():
                        normalized["properties"][key] = value
            if normalized["properties"]["name"]:
                transformed.append(normalized)
        return transformed

    async def load(
        self,
        records: list[dict[str, Any]],
        merge: bool = True,
    ) -> tuple[int, int, list[str]]:
        """Load records into graph. Returns (created, merged, errors)."""
        created = 0
        merged = 0
        errors: list[str] = []

        for record in records:
            try:
                label = NodeLabel(record["label"]) if record.get("label") else NodeLabel.PERSON
                props = record["properties"]

                duplicate = await self._find_duplicate(label, props)
                if duplicate and merge:
                    props["id"] = duplicate["id"]
                    merged += 1
                else:
                    created += 1

                node = await self._graph.create_node(
                    label=label,
                    properties=props,
                    merge_keys=record.get("merge_keys") if merge else None,
                )

                for rel in record.get("relationships", []):
                    await self._ensure_related_and_link(node, rel)

            except Exception as exc:
                errors.append(f"Record {record.get('properties', {}).get('name', '?')}: {exc}")
                logger.error("etl_load_error", error=str(exc))

        return created, merged, errors

    async def _find_duplicate(
        self,
        label: NodeLabel,
        props: dict[str, Any],
    ) -> dict[str, Any] | None:
        name = props.get("name", "")
        if not name:
            return None

        candidates = await self._graph.find_nodes(label, {"name": name}, limit=5)
        for candidate in candidates:
            score = SequenceMatcher(None, name.lower(), candidate.get("name", "").lower()).ratio()
            if score >= 0.95:
                return candidate

        email = props.get("email")
        if email:
            email_matches = await self._graph.find_nodes(label, {"email": email}, limit=1)
            if email_matches:
                return email_matches[0]

        return None

    async def _ensure_related_and_link(
        self,
        source_node: dict[str, Any],
        rel_spec: dict[str, Any],
    ) -> None:
        from app.core.domain.entities import RelationshipType

        rel_type = RelationshipType(rel_spec["type"])
        target_label = NodeLabel(rel_spec.get("target_label", NodeLabel.COMPANY.value))
        target_name = rel_spec.get("target_name", "")
        if not target_name:
            return

        target = await self._graph.create_node(
            label=target_label,
            properties={"name": target_name, "source": source_node.get("source", "import")},
            merge_keys=["name"],
        )

        await self._graph.create_relationship(
            from_id=source_node["id"],
            to_id=target["id"],
            rel_type=rel_type,
            properties=rel_spec.get("properties"),
        )

    async def run(
        self,
        file_path: str,
        source: str = "import",
        merge: bool = True,
        **kwargs: Any,
    ) -> ImportRecord:
        record = ImportRecord(
            filename=file_path.split("/")[-1],
            file_type=self.supported_extensions[0].lstrip("."),
            source=source,
            status="processing",
        )

        try:
            raw = await self.extract(file_path, **kwargs)
            record.records_processed = len(raw)
            transformed = await self.transform(raw, source)
            created, merged_count, errors = await self.load(transformed, merge=merge)
            record.records_created = created
            record.records_merged = merged_count
            record.errors = errors
            record.status = "completed" if not errors else "completed_with_errors"
            record.completed_at = datetime.utcnow()
        except Exception as exc:
            record.status = "failed"
            record.errors.append(str(exc))
            record.completed_at = datetime.utcnow()
            logger.error("etl_pipeline_failed", file=file_path, error=str(exc))

        return record
