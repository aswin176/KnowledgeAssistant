"""PDF and Word document import pipelines."""

import re
from typing import Any

from app.etl.base import BaseETLPipeline


class PDFETLPipeline(BaseETLPipeline):
    @property
    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    async def extract(self, file_path: str, **kwargs: Any) -> list[dict[str, Any]]:
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts)
        return self._parse_resume_text(full_text, source="pdf")

    def _parse_resume_text(self, text: str, source: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            return records

        # First non-empty line often name
        name = lines[0]
        record: dict[str, Any] = {
            "name": name,
            "bio": text[:5000],
            "relationships": [],
            "source": source,
        }

        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        if email_match:
            record["email"] = email_match.group()

        phone_match = re.search(r"\+?\d[\d\s\-()]{8,}\d", text)
        if phone_match:
            record["phone"] = phone_match.group().strip()

        # Skills section
        skills_match = re.search(
            r"(?:skills|technologies|technical skills)[:\s]*(.+?)(?:\n\n|\n[A-Z]|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if skills_match:
            skills = re.split(r"[,;|•\n]", skills_match.group(1))
            for skill in skills:
                skill = skill.strip()
                if skill and len(skill) < 50:
                    record["relationships"].append({
                        "type": "HAS_SKILL",
                        "target_label": "Skill",
                        "target_name": skill,
                    })

        # Experience / company patterns
        company_patterns = re.findall(
            r"(?:at|@)\s+([A-Z][A-Za-z0-9\s&.,]+?)(?:\s*[|\n]|$)",
            text,
        )
        for company in company_patterns[:5]:
            company = company.strip().rstrip(".,")
            if 2 < len(company) < 80:
                record["relationships"].append({
                    "type": "WORKED_AT",
                    "target_label": "Company",
                    "target_name": company,
                })

        records.append(record)
        return records


class DocxETLPipeline(BaseETLPipeline):
    @property
    def supported_extensions(self) -> list[str]:
        return [".docx"]

    async def extract(self, file_path: str, **kwargs: Any) -> list[dict[str, Any]]:
        from docx import Document

        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)

        pdf_pipeline = PDFETLPipeline(self._graph)
        return pdf_pipeline._parse_resume_text(full_text, source="docx")
