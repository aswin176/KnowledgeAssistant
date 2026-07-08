"""Seed sample data into Neo4j."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.core.domain.entities import NodeLabel, RelationshipType
from app.dependencies import Container


SAMPLE_DATA = [
    {
        "person": {"name": "Ravi Kumar", "title": "Senior Engineer", "email": "ravi@example.com"},
        "company": "Google",
        "city": "Bangalore",
        "skills": ["Kubernetes", "Python", "AWS"],
        "is_student": True,
    },
    {
        "person": {"name": "John Smith", "title": "Product Manager", "email": "john@example.com"},
        "company": "Microsoft",
        "city": "Seattle",
        "skills": ["Product Management", "Azure"],
        "marital_status": "married",
        "has_children": True,
    },
    {
        "person": {"name": "Priya Sharma", "title": "Data Scientist", "email": "priya@example.com"},
        "company": "Google",
        "city": "Bangalore",
        "skills": ["Machine Learning", "Python", "Kubernetes"],
        "is_student": True,
    },
    {
        "person": {"name": "Alex Chen", "title": "DevOps Lead", "email": "alex@example.com"},
        "company": "Stripe",
        "city": "San Francisco",
        "skills": ["Kubernetes", "Terraform", "AWS"],
    },
    {
        "person": {"name": "Maria Garcia", "title": "Software Engineer", "email": "maria@example.com"},
        "company": "Meta",
        "city": "Menlo Park",
        "skills": ["React", "GraphQL"],
        "marital_status": "married",
        "has_children": True,
    },
]


async def seed():
    settings = get_settings()
    container = Container(settings)
    await container.startup()

    print("Seeding sample data...")

    for entry in SAMPLE_DATA:
        label = NodeLabel.STUDENT if entry.get("is_student") else NodeLabel.PERSON
        person_data = {**entry["person"], "source": "seed"}
        if entry.get("marital_status"):
            person_data["marital_status"] = entry["marital_status"]
        if entry.get("has_children") is not None:
            person_data["has_children"] = entry["has_children"]

        person = await container.graph_repo.create_node(label, person_data, merge_keys=["email"])

        company = await container.graph_repo.create_node(
            NodeLabel.COMPANY,
            {"name": entry["company"], "source": "seed"},
            merge_keys=["name"],
        )
        await container.graph_repo.create_relationship(
            person["id"], company["id"], RelationshipType.WORKS_AT
        )

        city = await container.graph_repo.create_node(
            NodeLabel.CITY,
            {"name": entry["city"], "source": "seed"},
            merge_keys=["name"],
        )
        await container.graph_repo.create_relationship(
            person["id"], city["id"], RelationshipType.LIVES_IN
        )

        for skill_name in entry["skills"]:
            skill = await container.graph_repo.create_node(
                NodeLabel.SKILL,
                {"name": skill_name, "source": "seed"},
                merge_keys=["name"],
            )
            await container.graph_repo.create_relationship(
                person["id"], skill["id"], RelationshipType.HAS_SKILL
            )

        print(f"  Created: {person['name']}")

    # Create event
    event = await container.graph_repo.create_node(
        NodeLabel.EVENT,
        {"name": "Reunion 2025", "source": "seed"},
        merge_keys=["name"],
    )
    await container.graph_repo.create_relationship(
        (await container.graph_repo.find_nodes(NodeLabel.PERSON, {"name": "Ravi Kumar"}, limit=1))[0]["id"],
        event["id"],
        RelationshipType.ATTENDED,
    )

    # AWS certification for Alex
    cert = await container.graph_repo.create_node(
        NodeLabel.CERTIFICATION,
        {"name": "AWS Solutions Architect", "source": "seed"},
        merge_keys=["name"],
    )
    alex = (await container.graph_repo.find_nodes(NodeLabel.PERSON, {"name": "Alex Chen"}, limit=1))[0]
    await container.graph_repo.create_relationship(
        alex["id"], cert["id"], RelationshipType.HAS_CERTIFICATION
    )

    print(f"\nSeeded {len(SAMPLE_DATA)} people successfully!")
    await container.shutdown()


if __name__ == "__main__":
    asyncio.run(seed())
