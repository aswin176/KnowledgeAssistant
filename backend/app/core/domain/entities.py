"""Domain entities and value objects."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class NodeLabel(str, Enum):
    STUDENT = "Student"
    PERSON = "Person"
    COMPANY = "Company"
    SKILL = "Skill"
    CITY = "City"
    COUNTRY = "Country"
    ADDRESS = "Address"
    UNIVERSITY = "University"
    CLASS = "Class"
    PROJECT = "Project"
    TECHNOLOGY = "Technology"
    AWARD = "Award"
    CERTIFICATION = "Certification"
    EVENT = "Event"
    INTEREST = "Interest"
    LANGUAGE = "Language"
    RESUME = "Resume"
    LINKEDIN_PROFILE = "LinkedInProfile"
    GITHUB_PROFILE = "GithubProfile"
    WEBSITE = "Website"
    ORGANIZATION = "Organization"
    FAMILY_MEMBER = "FamilyMember"
    PHOTO = "Photo"
    DOCUMENT = "Document"
    NOTE = "Note"


class RelationshipType(str, Enum):
    WORKS_AT = "WORKS_AT"
    WORKED_AT = "WORKED_AT"
    STUDIED_IN = "STUDIED_IN"
    HAS_SKILL = "HAS_SKILL"
    LIVES_IN = "LIVES_IN"
    LIVES_AT = "LIVES_AT"
    LOCATED_IN = "LOCATED_IN"
    HAS_PROFILE = "HAS_PROFILE"
    KNOWS = "KNOWS"
    ATTENDED = "ATTENDED"
    HAS_DOCUMENT = "HAS_DOCUMENT"
    HAS_CERTIFICATION = "HAS_CERTIFICATION"
    HAS_AWARD = "HAS_AWARD"
    USES_TECHNOLOGY = "USES_TECHNOLOGY"
    PARTICIPATED_IN = "PARTICIPATED_IN"
    MEMBER_OF = "MEMBER_OF"
    FRIEND_OF = "FRIEND_OF"
    CONNECTED_TO = "CONNECTED_TO"
    HAS_NOTE = "HAS_NOTE"
    RELATED_TO = "RELATED_TO"
    BELONGS_TO_CLASS = "BELONGS_TO_CLASS"
    MARRIED_TO = "MARRIED_TO"
    HAS_FATHER = "HAS_FATHER"


class MetadataMixin(BaseModel):
    """Common metadata for all graph entities."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "manual"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    last_verified: datetime | None = None
    is_active: bool = True
    version: int = 1


class PersonEntity(MetadataMixin):
    model_config = ConfigDict(extra="ignore")

    name: str
    roll_number: str | None = None
    father_name: str | None = None
    dob: str | None = None
    address: str | None = None
    hometown: str | None = None
    mobile: str | None = None
    email: str | None = None
    class_name: str | None = Field(default=None, alias="class")
    current_employment: str | None = None
    relationship_status: str | None = None
    marriage_date: str | None = None
    kids: int | None = None
    spouse_roll_number: str | None = None
    spouse_name: str | None = None
    linkedin_url: str | None = None
    current_city: str | None = None


class CompanyEntity(MetadataMixin):
    name: str
    industry: str | None = None
    website: str | None = None
    description: str | None = None
    founded_year: int | None = None
    size: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class RelationshipEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: RelationshipType
    from_id: str
    to_id: str
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "manual"
    confidence: float = 1.0
    is_active: bool = True
    start_date: str | None = None
    end_date: str | None = None


class NoteEntity(MetadataMixin):
    title: str
    content: str
    content_type: str = "markdown"
    person_id: str | None = None
    attachments: list[str] = Field(default_factory=list)


class ImportRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    file_type: str
    status: str = "pending"
    records_processed: int = 0
    records_created: int = 0
    records_merged: int = 0
    errors: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    source: str = "upload"
