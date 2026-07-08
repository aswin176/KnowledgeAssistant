"""CSV and Excel import pipelines."""

import re
from typing import Any

import pandas as pd

from app.etl.base import BaseETLPipeline

COLUMN_MAPPINGS = {
    "roll_number": "roll_number",
    "name": "name",
    "class": "class",
    "father_name": "father_name",
    "dob": "dob",
    "address": "address",
    "hometown": "hometown",
    "mobile": "mobile",
    "email": "email",
    "7th_semester_employment": "7th_semester_employment",
    "10th_semester_employment": "10th_semester_employment",
    "current_employment": "current_employment",
    "relationship_status": "relationship_status",
    "marraige_date": "marriage_date",
    "marriage_date": "marriage_date",
    "kids": "kids",
    "spouse_roll_number_if_present_in_same_data": "spouse_roll_number",
    "spouse_roll_number": "spouse_roll_number",
    "spouse_name": "spouse_name",
    "linkedin_url": "linkedin_url",
    "current_city": "current_city",
}


def _normalize_column_name(col: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(col).strip().lower()).strip("_")


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


def _parse_person_relationships(record: dict[str, Any]) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []

    if record.get("class"):
        relationships.append(
            {"type": "BELONGS_TO_CLASS", "target_label": "Class", "target_name": str(record["class"]).strip()}
        )
    if record.get("current_city"):
        relationships.append(
            {"type": "LIVES_IN", "target_label": "City", "target_name": str(record["current_city"]).strip()}
        )
    if record.get("hometown"):
        relationships.append(
            {"type": "LIVES_IN", "target_label": "City", "target_name": str(record["hometown"]).strip()}
        )
    if record.get("address"):
        relationships.append(
            {"type": "LIVES_AT", "target_label": "Address", "target_name": str(record["address"]).strip()}
        )
    if record.get("father_name"):
        relationships.append(
            {"type": "HAS_FATHER", "target_label": "FamilyMember", "target_name": str(record["father_name"]).strip()}
        )
    if record.get("spouse_name"):
        relationships.append(
            {"type": "MARRIED_TO", "target_label": "Person", "target_name": str(record["spouse_name"]).strip()}
        )
    if record.get("7th_semester_employment"):
        relationships.append(
            {"type": "WORKED_AT", "target_label": "Company", "target_name": str(record["7th_semester_employment"]).strip()}
        )
    if record.get("10th_semester_employment"):
        relationships.append(
            {"type": "WORKED_AT", "target_label": "Company", "target_name": str(record["10th_semester_employment"]).strip()}
        )
    if record.get("current_employment"):
        relationships.append(
            {"type": "WORKS_AT", "target_label": "Company", "target_name": str(record["current_employment"]).strip()}
        )
    if record.get("linkedin_url"):
        relationships.append(
            {"type": "HAS_PROFILE", "target_label": "LinkedInProfile", "target_name": str(record["linkedin_url"]).strip()}
        )
    return relationships


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
                record["label"] = "Person"
                record["merge_keys"] = ["roll_number"] if record.get("roll_number") else ["email", "name"]
                record["relationships"].extend(_parse_person_relationships(record))
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
