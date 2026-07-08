"""Load an Excel file into Neo4j and build the graph schema for person records."""

import argparse
import asyncio
from pathlib import Path

from app.config import get_settings
from app.etl.csv_excel import ExcelETLPipeline
from app.infrastructure.neo4j.connection import Neo4jConnection
from app.infrastructure.neo4j.repository import Neo4jGraphRepository


async def main() -> None:
    parser = argparse.ArgumentParser(description="Import person Excel data into Neo4j")
    parser.add_argument("file_path", nargs="?", default="./uploads/students.xlsx")
    parser.add_argument("--sheet", type=int, default=0)
    parser.add_argument("--no-merge", action="store_true")
    args = parser.parse_args()

    file_path = Path(args.file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    settings = get_settings()
    conn = Neo4jConnection(settings)
    await conn.connect()
    repo = Neo4jGraphRepository(conn)
    await repo.initialize_schema()

    pipeline = ExcelETLPipeline(repo)
    records = await pipeline.extract(str(file_path), sheet=args.sheet)
    transformed = await pipeline.transform(records, source="excel_import")
    created, merged, errors = await pipeline.load(transformed, merge=not args.no_merge)

    print(f"Loaded {len(transformed)} records into Neo4j")
    print(f"Created nodes: {created}")
    print(f"Merged nodes: {merged}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
