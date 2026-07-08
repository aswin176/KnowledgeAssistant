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

PERSON_ATTRIBUTE_KEYS = {
    "roll_number",
    "name",
    "dob",
    "mobile",
    "email",
    "relationship_status",
    "kids",
}

RELATIONSHIP_SOURCE_KEYS = {
    "class",
    "father_name",
    "address",
    "hometown",
    "current_city",
    "7th_semester_employment",
    "10th_semester_employment",
    "current_employment",
    "marriage_date",
    "spouse_roll_number",
    "spouse_name",
    "linkedin_url",
}

SUPPORTED_PERSON_COLUMNS = PERSON_ATTRIBUTE_KEYS | RELATIONSHIP_SOURCE_KEYS


def _normalize_column_name(col: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(col).strip().lower()).strip("_")


def _clean_value(value: Any) -> Any:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return value


def _clean_string(value: Any) -> str | None:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    return str(cleaned).strip() or None


def _clean_integer(value: Any) -> int | None:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    if isinstance(cleaned, int):
        return cleaned
    if isinstance(cleaned, float):
        return int(cleaned)
    text = str(cleaned).strip()
    if not text:
        return None
    return int(float(text))


def _parse_person_relationships(record: dict[str, Any]) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []

    def add_relationship(
        rel_type: str,
        target_label: str,
        target_name: str | None,
        *,
        properties: dict[str, Any] | None = None,
        target_properties: dict[str, Any] | None = None,
        target_merge_keys: list[str] | None = None,
    ) -> None:
        if not target_name:
            return
        relationship: dict[str, Any] = {
            "type": rel_type,
            "target_label": target_label,
            "target_name": target_name,
        }
        if properties:
            relationship["properties"] = properties
        if target_properties:
            relationship["target_properties"] = target_properties
        if target_merge_keys:
            relationship["target_merge_keys"] = target_merge_keys
        relationships.append(relationship)

    if record.get("class"):
        add_relationship("BELONGS_TO_CLASS", "Class", _clean_string(record["class"]))
    if record.get("current_city"):
        add_relationship(
            "LIVES_IN",
            "City",
            _clean_string(record["current_city"]),
            properties={"kind": "current_city"},
        )
    if record.get("hometown"):
        add_relationship(
            "LIVES_IN",
            "City",
            _clean_string(record["hometown"]),
            properties={"kind": "hometown"},
        )
    if record.get("address"):
        add_relationship("LIVES_AT", "Address", _clean_string(record["address"]))
    if record.get("father_name"):
        add_relationship("HAS_FATHER", "FamilyMember", _clean_string(record["father_name"]))
    if record.get("spouse_name") or record.get("spouse_roll_number"):
        spouse_name = _clean_string(record.get("spouse_name"))
        spouse_roll_number = _clean_string(record.get("spouse_roll_number"))
        spouse_properties = {
            "name": spouse_name or f"Spouse {spouse_roll_number}",
        }
        if spouse_roll_number:
            spouse_properties["roll_number"] = spouse_roll_number
        marriage_properties = {
            "marriage_date": _clean_string(record.get("marriage_date")),
        }
        marriage_properties = {
            key: value for key, value in marriage_properties.items() if value is not None
        }
        add_relationship(
            "MARRIED_TO",
            "Person",
            spouse_properties["name"],
            properties=marriage_properties or None,
            target_properties=spouse_properties,
            target_merge_keys=["roll_number"] if spouse_roll_number else ["name"],
        )
    if record.get("7th_semester_employment"):
        add_relationship(
            "WORKED_AT",
            "Company",
            _clean_string(record["7th_semester_employment"]),
            properties={"stage": "7th_semester"},
        )
    if record.get("10th_semester_employment"):
        add_relationship(
            "WORKED_AT",
            "Company",
            _clean_string(record["10th_semester_employment"]),
            properties={"stage": "10th_semester"},
        )
    if record.get("current_employment"):
        add_relationship(
            "WORKS_AT",
            "Company",
            _clean_string(record["current_employment"]),
            properties={"stage": "current"},
        )
    if record.get("linkedin_url"):
        linkedin_url = _clean_string(record["linkedin_url"])
        add_relationship(
            "HAS_PROFILE",
            "LinkedInProfile",
            linkedin_url,
            target_properties={"name": linkedin_url, "url": linkedin_url},
            target_merge_keys=["url"],
        )
    return relationships


class TabularMixin:
    def _dataframe_to_records(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        df.columns = [_normalize_column_name(str(c)) for c in df.columns]
        df = df.rename(columns=COLUMN_MAPPINGS)
        records: list[dict[str, Any]] = []

        for _, row in df.iterrows():
            normalized_row: dict[str, Any] = {}
            for col, val in row.items():
                if col not in SUPPORTED_PERSON_COLUMNS:
                    continue
                cleaned = _clean_integer(val) if col == "kids" else _clean_value(val)
                if cleaned is None:
                    continue
                normalized_row[col] = cleaned

            if normalized_row.get("name"):
                record: dict[str, Any] = {
                    "relationships": _parse_person_relationships(normalized_row),
                }
                for key in PERSON_ATTRIBUTE_KEYS:
                    if key in normalized_row:
                        record[key] = normalized_row[key]
                record["label"] = "Person"
                if record.get("roll_number"):
                    record["merge_keys"] = ["roll_number"]
                elif record.get("email"):
                    record["merge_keys"] = ["email"]
                else:
                    record["merge_keys"] = ["name"]
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
