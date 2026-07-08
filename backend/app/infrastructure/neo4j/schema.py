"""Neo4j schema definitions and initialization."""

SCHEMA_CONSTRAINTS = [
    "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (n:Person) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT person_roll_number IF NOT EXISTS FOR (n:Person) REQUIRE n.roll_number IS UNIQUE",
    "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (n:Company) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (n:Skill) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT city_id IF NOT EXISTS FOR (n:City) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT country_id IF NOT EXISTS FOR (n:Country) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT university_id IF NOT EXISTS FOR (n:University) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT class_id IF NOT EXISTS FOR (n:Class) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (n:Event) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT certification_id IF NOT EXISTS FOR (n:Certification) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT project_id IF NOT EXISTS FOR (n:Project) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT technology_id IF NOT EXISTS FOR (n:Technology) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT note_id IF NOT EXISTS FOR (n:Note) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (n:Document) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT linkedin_id IF NOT EXISTS FOR (n:LinkedInProfile) REQUIRE n.id IS UNIQUE",
]

SCHEMA_INDEXES = [
    "CREATE INDEX person_name IF NOT EXISTS FOR (n:Person) ON (n.name)",
    "CREATE INDEX person_email IF NOT EXISTS FOR (n:Person) ON (n.email)",
    "CREATE INDEX company_name IF NOT EXISTS FOR (n:Company) ON (n.name)",
    "CREATE INDEX skill_name IF NOT EXISTS FOR (n:Skill) ON (n.name)",
    "CREATE INDEX city_name IF NOT EXISTS FOR (n:City) ON (n.name)",
    "CREATE INDEX class_name IF NOT EXISTS FOR (n:Class) ON (n.name)",
    "CREATE INDEX event_name IF NOT EXISTS FOR (n:Event) ON (n.name)",
    "CREATE FULLTEXT INDEX entitySearch IF NOT EXISTS FOR (n:Person|Company|Skill|City|Event|University|Project|Technology|Certification|Class) ON EACH [n.name, n.title, n.description, n.bio, n.industry, n.email]",
]

NODE_LABELS = [
    "Person", "Company", "Skill", "City", "Country", "Address",
    "University", "Class", "Project", "Technology", "Award", "Certification",
    "Event", "Interest", "Language", "Resume", "LinkedInProfile", "GithubProfile",
    "Website", "Organization", "FamilyMember", "Photo", "Document", "Note",
]

RELATIONSHIP_TYPES = [
    "WORKS_AT", "WORKED_AT", "STUDIED_IN", "HAS_SKILL", "LIVES_IN", "LIVES_AT",
    "LOCATED_IN", "HAS_PROFILE", "KNOWS", "ATTENDED", "HAS_DOCUMENT", "HAS_CERTIFICATION",
    "HAS_AWARD", "USES_TECHNOLOGY", "PARTICIPATED_IN", "MEMBER_OF", "FRIEND_OF",
    "CONNECTED_TO", "HAS_NOTE", "RELATED_TO", "BELONGS_TO_CLASS", "MARRIED_TO", "HAS_FATHER",
]
