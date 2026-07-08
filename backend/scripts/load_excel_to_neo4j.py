"""Load an Excel file into Neo4j and build the graph schema for person records."""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure backend root is available on sys.path when running this script directly.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import get_settings
from app.etl.csv_excel import ExcelETLPipeline
from app.infrastructure.neo4j.connection import Neo4jConnection
from app.infrastructure.neo4j.repository import Neo4jGraphRepository


async def main() -> None:
    parser = argparse.ArgumentParser(description="Import person Excel data into Neo4j")
    parser.add_argument("file_path", nargs="?", default=None)
    parser.add_argument("--sheet", type=int, default=0)
    parser.add_argument("--no-merge", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    file_path = Path(args.file_path or settings.import_file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

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
