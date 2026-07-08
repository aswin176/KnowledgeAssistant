"""Neo4j database connection manager."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from app.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Neo4jConnection:
    """Manages Neo4j driver lifecycle."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        if self._driver is not None:
            return
        self._driver = AsyncGraphDatabase.driver(
            self._settings.neo4j_uri,
            auth=(self._settings.neo4j_user, self._settings.neo4j_password),
        )
        await self._driver.verify_connectivity()
        logger.info("neo4j_connected", uri=self._settings.neo4j_uri)

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("neo4j_disconnected")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._driver is None:
            await self.connect()
        assert self._driver is not None
        session = self._driver.session(database=self._settings.neo4j_database)
        try:
            yield session
        finally:
            await session.close()

    async def execute_read(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        async with self.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def execute_write(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        async with self.session() as session:
            result = await session.execute_write(
                lambda tx: tx.run(query, parameters or {})
            )
            records = await result.data()
            return records

    async def health_check(self) -> bool:
        try:
            await self.execute_read("RETURN 1 AS ok")
            return True
        except Exception as exc:
            logger.error("neo4j_health_check_failed", error=str(exc))
            return False
