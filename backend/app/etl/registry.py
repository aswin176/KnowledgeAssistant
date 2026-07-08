"""ETL pipeline registry and dispatcher."""

from pathlib import Path

from app.core.domain.entities import ImportRecord
from app.core.exceptions import ImportError as EutridatsImportError
from app.core.interfaces.repositories import GraphRepository
from app.etl.base import BaseETLPipeline
from app.etl.csv_excel import CSVETLPipeline, ExcelETLPipeline
from app.etl.json_markdown import JSONETLPipeline, MarkdownETLPipeline
from app.etl.pdf_docx import DocxETLPipeline, PDFETLPipeline


class ImportService:
    """Dispatches files to appropriate ETL pipeline."""

    def __init__(self, graph_repo: GraphRepository) -> None:
        self._graph = graph_repo
        self._pipelines: list[BaseETLPipeline] = [
            CSVETLPipeline(graph_repo),
            ExcelETLPipeline(graph_repo),
            JSONETLPipeline(graph_repo),
            MarkdownETLPipeline(graph_repo),
            PDFETLPipeline(graph_repo),
            DocxETLPipeline(graph_repo),
        ]
        self._import_history: list[ImportRecord] = []

    def _get_pipeline(self, file_path: str) -> BaseETLPipeline:
        ext = Path(file_path).suffix.lower()
        for pipeline in self._pipelines:
            if ext in pipeline.supported_extensions:
                return pipeline
        raise EutridatsImportError(f"Unsupported file type: {ext}")

    @property
    def supported_extensions(self) -> list[str]:
        exts: list[str] = []
        for p in self._pipelines:
            exts.extend(p.supported_extensions)
        return exts

    async def import_file(
        self,
        file_path: str,
        source: str = "upload",
        merge: bool = True,
        **kwargs,
    ) -> ImportRecord:
        pipeline = self._get_pipeline(file_path)
        record = await pipeline.run(file_path, source=source, merge=merge, **kwargs)
        self._import_history.append(record)
        return record

    async def list_imports(self, limit: int = 50) -> list[ImportRecord]:
        return self._import_history[-limit:][::-1]

    async def get_import(self, record_id: str) -> ImportRecord | None:
        for record in self._import_history:
            if record.id == record_id:
                return record
        return None
