"""JSON and Markdown import pipelines."""

import json
import re
from pathlib import Path
from typing import Any

import markdown

from app.etl.base import BaseETLPipeline


class JSONETLPipeline(BaseETLPipeline):
    @property
    def supported_extensions(self) -> list[str]:
        return [".json"]

    async def extract(self, file_path: str, **kwargs: Any) -> list[dict[str, Any]]:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "people" in data:
                return data["people"]
            if "records" in data:
                return data["records"]
            return [data]
        return []


class MarkdownETLPipeline(BaseETLPipeline):
    @property
    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown"]

    async def extract(self, file_path: str, **kwargs: Any) -> list[dict[str, Any]]:
        content = Path(file_path).read_text(encoding="utf-8")
        records: list[dict[str, Any]] = []

        # Parse YAML frontmatter if present
        frontmatter: dict[str, Any] = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].strip().splitlines():
                    if ":" in line:
                        key, val = line.split(":", 1)
                        frontmatter[key.strip()] = val.strip()
                content = parts[2]

        # Parse person sections: ## Name or # Name
        sections = re.split(r"\n(?=#{1,2}\s)", content)
        for section in sections:
            section = section.strip()
            if not section:
                continue

            header_match = re.match(r"^#{1,2}\s+(.+)$", section, re.MULTILINE)
            if not header_match:
                continue

            name = header_match.group(1).strip()
            record: dict[str, Any] = {"name": name, "relationships": [], **frontmatter}

            # Extract key: value pairs
            for match in re.finditer(r"^[-*]?\s*\*?\*?(\w[\w\s]*?)\*?\*?\s*:\s*(.+)$", section, re.MULTILINE):
                key = match.group(1).strip().lower().replace(" ", "_")
                value = match.group(2).strip()
                if key in ("company", "works_at", "employer"):
                    record["relationships"].append({
                        "type": "WORKS_AT",
                        "target_label": "Company",
                        "target_name": value,
                    })
                elif key in ("city", "location", "lives_in"):
                    record["relationships"].append({
                        "type": "LIVES_IN",
                        "target_label": "City",
                        "target_name": value,
                    })
                elif key in ("skills", "skill"):
                    for skill in value.split(","):
                        skill = skill.strip()
                        if skill:
                            record["relationships"].append({
                                "type": "HAS_SKILL",
                                "target_label": "Skill",
                                "target_name": skill,
                            })
                else:
                    record[key] = value

            record["bio"] = markdown.markdown(section)
            records.append(record)

        return records
