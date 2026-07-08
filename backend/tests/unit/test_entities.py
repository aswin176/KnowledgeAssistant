"""Unit tests for domain entities."""

from app.core.domain.entities import NodeLabel, PersonEntity, RelationshipType


class TestDomainEntities:
    def test_person_entity_defaults(self):
        person = PersonEntity(name="John Doe")
        assert person.name == "John Doe"
        assert person.id is not None
        assert person.is_active is True
        assert person.confidence == 1.0
        assert person.source == "manual"

    def test_node_labels_complete(self):
        expected = {
            "Person", "Company", "City", "Address", "Class",
            "FamilyMember", "LinkedInProfile", "Note",
        }
        actual = {label.value for label in NodeLabel}
        assert expected.issubset(actual)

    def test_relationship_types(self):
        assert RelationshipType.WORKS_AT.value == "WORKS_AT"
        assert RelationshipType.HAS_SKILL.value == "HAS_SKILL"
        assert RelationshipType.FRIEND_OF.value == "FRIEND_OF"
