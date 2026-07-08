"""Generic connector interface and implementations."""

from typing import Any

from app.core.interfaces.repositories import ConnectorInterface
from app.core.logging import get_logger

logger = get_logger(__name__)


class ManualNotesConnector(ConnectorInterface):
    @property
    def name(self) -> str:
        return "manual_notes"

    async def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        content = kwargs.get("content", "")
        title = kwargs.get("title", "Untitled Note")
        return [{"name": title, "bio": content, "source": "manual_notes"}]

    async def validate_config(self, config: dict[str, Any]) -> bool:
        return "content" in config


class CSVConnector(ConnectorInterface):
    @property
    def name(self) -> str:
        return "csv"

    async def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        file_path = kwargs.get("file_path", "")
        if not file_path:
            return []
        from app.etl.csv_excel import CSVETLPipeline
        from app.infrastructure.neo4j.connection import Neo4jConnection
        from app.infrastructure.neo4j.repository import Neo4jGraphRepository
        from app.config import get_settings

        settings = get_settings()
        conn = Neo4jConnection(settings)
        repo = Neo4jGraphRepository(conn)
        pipeline = CSVETLPipeline(repo)
        return await pipeline.extract(file_path)

    async def validate_config(self, config: dict[str, Any]) -> bool:
        return "file_path" in config


class LinkedInConnector(ConnectorInterface):
    """Generic LinkedIn connector - stores URL and snapshot without tight coupling."""

    @property
    def name(self) -> str:
        return "linkedin"

    async def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        url = kwargs.get("url", "")
        snapshot = kwargs.get("snapshot", {})
        if not url:
            return []
        return [{
            "label": "Person",
            "name": snapshot.get("name", "Unknown"),
            "linkedin_url": url,
            "title": snapshot.get("headline"),
            "bio": snapshot.get("summary"),
            "source": "linkedin",
            "relationships": [
                {
                    "type": "HAS_PROFILE",
                    "target_label": "LinkedInProfile",
                    "target_name": url,
                    "properties": {"url": url, "snapshot": snapshot},
                }
            ],
        }]

    async def validate_config(self, config: dict[str, Any]) -> bool:
        return "url" in config


CONNECTOR_REGISTRY: dict[str, ConnectorInterface] = {
    "manual_notes": ManualNotesConnector(),
    "csv": CSVConnector(),
    "linkedin": LinkedInConnector(),
}


def get_connector(name: str) -> ConnectorInterface | None:
    return CONNECTOR_REGISTRY.get(name)
