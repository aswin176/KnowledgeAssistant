"""Unit tests for Cypher validator."""

import pytest

from app.graph.cypher_validator import validate_read_only_cypher


class TestCypherValidator:
    def test_valid_read_query(self):
        cypher = """
        MATCH (p:Person)-[:WORKS_AT]->(c:Company)
        WHERE toLower(c.name) CONTAINS 'google'
        RETURN p.name AS name
        LIMIT 50
        """
        is_safe, error = validate_read_only_cypher(cypher)
        assert is_safe is True
        assert error is None

    def test_rejects_create(self):
        cypher = "CREATE (n:Person {name: 'Test'}) RETURN n"
        is_safe, error = validate_read_only_cypher(cypher)
        assert is_safe is False
        assert "forbidden" in error.lower()

    def test_rejects_delete(self):
        cypher = "MATCH (n) DELETE n"
        is_safe, error = validate_read_only_cypher(cypher)
        assert is_safe is False

    def test_rejects_merge(self):
        cypher = "MERGE (n:Person {name: 'Test'}) RETURN n"
        is_safe, error = validate_read_only_cypher(cypher)
        assert is_safe is False

    def test_rejects_set(self):
        cypher = "MATCH (n) SET n.name = 'hack' RETURN n"
        is_safe, error = validate_read_only_cypher(cypher)
        assert is_safe is False

    def test_rejects_empty(self):
        is_safe, error = validate_read_only_cypher("")
        assert is_safe is False
        assert error == "Empty query"

    def test_rejects_drop(self):
        cypher = "DROP INDEX person_name"
        is_safe, error = validate_read_only_cypher(cypher)
        assert is_safe is False

    def test_allows_optional_match(self):
        cypher = """
        OPTIONAL MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
        RETURN p.name, s.name
        """
        is_safe, _ = validate_read_only_cypher(cypher)
        assert is_safe is True
