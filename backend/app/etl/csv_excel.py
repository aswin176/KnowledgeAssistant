"""CSV and Excel import pipelines."""

from typing import Any

import pandas as pd

from app.etl.base import BaseETLPipeline

COLUMN_MAPPINGS = {
    "full_name": "name",
    "person_name": "name",
    "company_name": "name",
    "employer": "company",
    "organization": "company",
    "job_title": "title",
    "position": "title",
    "location": "city",
    "skills": "skills",
    "skill": "skills",
    "linkedin": "linkedin_url",
    "linkedin_url": "linkedin_url",
}


def _normalize_column_name(col: str) -> str:
    return col.strip().lower().replace(" ", "_")


def _parse_skills(value: Any) -> list[dict[str, Any]]:
    if not value or (isinstance(value, float) and pd.isna(value)):
        return []
    skills_str = str(value)
    skills = [s.strip() for s in skills_str.replace(";", ",").split(",") if s.strip()]
    return [{"type": "HAS_SKILL", "target_label": "Skill", "target_name": s} for s in skills]


def _parse_company(value: Any) -> list[dict[str, Any]]:
    if not value or (isinstance(value, float) and pd.isna(value)):
        return []
    return [{"type": "WORKS_AT", "target_label": "Company", "target_name": str(value).strip()}]


def _parse_city(value: Any) -> list[dict[str, Any]]:
    if not value or (isinstance(value, float) and pd.isna(value)):
        return []
    return [{"type": "LIVES_IN", "target_label": "City", "target_name": str(value).strip()}]


class TabularMixin:
    def _dataframe_to_records(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        df.columns = [_normalize_column_name(str(c)) for c in df.columns]
        df = df.rename(columns=COLUMN_MAPPINGS)
        records: list[dict[str, Any]] = []

        for _, row in df.iterrows():
            record: dict[str, Any] = {"relationships": []}
            for col, val in row.items():
                if pd.isna(val):
                    continue
                if col == "skills":
                    record["relationships"].extend(_parse_skills(val))
                elif col == "company":
                    record["relationships"].extend(_parse_company(val))
                elif col == "city":
                    record["relationships"].extend(_parse_city(val))
                elif col == "label":
                    record["label"] = str(val)
                else:
                    record[col] = val

            if record.get("name"):
                if not record.get("label"):
                    record["label"] = (
                        "Company" if "industry" in record and not record.get("title") else "Person"
                    )
                records.append(record)

        return records


class CSVETLPipeline(TabularMixin, BaseETLPipeline):
    @property
    def supported_extensions(self) -> list[str]:
        return [".csv"]

    async def extract(self, file_path: str, **kwargs: Any) -> list[dict[str, Any]]:
        df = pd.read_csv(file_path)
        return self._dataframe_to_records(df)


class ExcelETLPipeline(TabularMixin, BaseETLPipeline):
    @property
    def supported_extensions(self) -> list[str]:
        return [".xlsx", ".xls"]

    async def extract(self, file_path: str, **kwargs: Any) -> list[dict[str, Any]]:
        sheet = kwargs.get("sheet", 0)
        df = pd.read_excel(file_path, sheet_name=sheet)
        return self._dataframe_to_records(df)
