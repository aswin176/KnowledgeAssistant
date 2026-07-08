"""LangGraph agent for knowledge graph Q&A."""

import json
import re
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, StateGraph

from app.core.interfaces.repositories import GraphRepository, LLMService
from app.core.logging import get_logger
from app.graph.cypher_validator import validate_read_only_cypher

logger = get_logger(__name__)

CYPHER_SYSTEM_PROMPT = """You are a Neo4j Cypher query generator for a personal knowledge graph.

Node labels: Person, Student, Company, Skill, City, Country, University, Class, Project,
Technology, Award, Certification, Event, Interest, Language, Resume, LinkedInProfile,
GithubProfile, Website, Organization, FamilyMember, Photo, Document, Note

Relationship types: WORKS_AT, WORKED_AT, STUDIED_IN, HAS_SKILL, LIVES_IN, LOCATED_IN,
HAS_PROFILE, KNOWS, ATTENDED, HAS_DOCUMENT, HAS_CERTIFICATION, HAS_AWARD, USES_TECHNOLOGY,
PARTICIPATED_IN, MEMBER_OF, FRIEND_OF, CONNECTED_TO, HAS_NOTE

Rules:
1. Generate ONLY read-only Cypher (MATCH, OPTIONAL MATCH, WITH, RETURN, ORDER BY, LIMIT)
2. Never use CREATE, MERGE, DELETE, SET, REMOVE, DROP
3. Filter active nodes: WHERE n.is_active IS NULL OR n.is_active = true
4. Use case-insensitive matching with toLower() when searching names
5. Return relevant properties: name, id, title, email, and relationship details
6. Limit results to 50 unless asked for more
7. Respond with ONLY the Cypher query, no explanation

Example:
Question: Who works at Google?
Cypher:
MATCH (p:Person)-[:WORKS_AT]->(c:Company)
WHERE toLower(c.name) CONTAINS 'google'
  AND (p.is_active IS NULL OR p.is_active = true)
RETURN p.name AS name, p.id AS id, p.title AS title, c.name AS company
LIMIT 50
"""

SUMMARIZE_SYSTEM_PROMPT = """You are a helpful personal knowledge assistant.
Answer the user's question based on the graph query results provided.
Be concise, accurate, and conversational. Use markdown formatting when helpful.
If results are empty, say you couldn't find matching information.
Include entity names and key details. Do not mention Cypher or databases.
If appropriate, format results as a markdown table.
"""


class AgentState(TypedDict):
    question: str
    needs_graph: bool
    cypher: str
    graph_results: list[dict[str, Any]]
    answer: str
    sources: list[dict[str, Any]]
    reasoning_steps: list[str]
    error: str | None
    conversation_history: list[dict[str, str]]


class KnowledgeGraphAgent:
    """LangGraph agent for natural language graph queries."""

    def __init__(self, llm: LLMService, graph: GraphRepository) -> None:
        self._llm = llm
        self._graph = graph
        self._workflow = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow: StateGraph = StateGraph(AgentState)

        workflow.add_node("classify", self._classify_question)
        workflow.add_node("generate_cypher", self._generate_cypher)
        workflow.add_node("execute_cypher", self._execute_cypher)
        workflow.add_node("direct_answer", self._direct_answer)
        workflow.add_node("summarize", self._summarize)

        workflow.set_entry_point("classify")

        workflow.add_conditional_edges(
            "classify",
            self._route_after_classify,
            {"graph": "generate_cypher", "direct": "direct_answer"},
        )
        workflow.add_edge("generate_cypher", "execute_cypher")
        workflow.add_edge("execute_cypher", "summarize")
        workflow.add_edge("direct_answer", END)
        workflow.add_edge("summarize", END)

        return workflow.compile()

    async def _classify_question(self, state: AgentState) -> AgentState:
        question = state["question"]
        reasoning = state.get("reasoning_steps", [])

        graph_keywords = [
            "who", "which", "find", "show", "list", "search", "works at", "worked at",
            "lives in", "knows", "skill", "company", "classmate", "friend", "attended",
            "certification", "married", "children", "career", "connected", "profile",
        ]
        needs_graph = any(kw in question.lower() for kw in graph_keywords)

        reasoning.append(f"Classified question as {'graph' if needs_graph else 'direct'} query")
        return {**state, "needs_graph": needs_graph, "reasoning_steps": reasoning}

    def _route_after_classify(self, state: AgentState) -> str:
        return "graph" if state.get("needs_graph", True) else "direct"

    async def _generate_cypher(self, state: AgentState) -> AgentState:
        reasoning = state.get("reasoning_steps", [])
        question = state["question"]

        prompt = f"Generate a Cypher query for this question:\n{question}"
        raw = await self._llm.generate(prompt, system=CYPHER_SYSTEM_PROMPT)

        cypher = self._extract_cypher(raw)
        reasoning.append(f"Generated Cypher: {cypher[:100]}...")
        return {**state, "cypher": cypher, "reasoning_steps": reasoning}

    async def _execute_cypher(self, state: AgentState) -> AgentState:
        reasoning = state.get("reasoning_steps", [])
        cypher = state.get("cypher", "")

        is_safe, error_msg = validate_read_only_cypher(cypher)
        if not is_safe:
            reasoning.append(f"Cypher rejected: {error_msg}")
            return {
                **state,
                "graph_results": [],
                "error": error_msg,
                "reasoning_steps": reasoning,
            }

        try:
            results = await self._graph.execute_read_query(cypher)
            reasoning.append(f"Query returned {len(results)} results")
            sources = [
                {"id": r.get("id"), "name": r.get("name"), "type": r.get("_labels", ["Unknown"])[0] if isinstance(r.get("_labels"), list) else "Entity"}
                for r in results
                if r.get("id") or r.get("name")
            ]
            return {
                **state,
                "graph_results": results,
                "sources": sources[:20],
                "reasoning_steps": reasoning,
                "error": None,
            }
        except Exception as exc:
            reasoning.append(f"Query failed: {exc}")
            return {
                **state,
                "graph_results": [],
                "error": str(exc),
                "reasoning_steps": reasoning,
            }

    async def _summarize(self, state: AgentState) -> AgentState:
        reasoning = state.get("reasoning_steps", [])
        question = state["question"]
        results = state.get("graph_results", [])
        error = state.get("error")

        if error:
            answer = f"I encountered an issue searching the knowledge graph: {error}"
        else:
            context = json.dumps(results[:30], default=str, indent=2)
            prompt = f"""Question: {question}

Graph Results:
{context}

Provide a helpful answer based on these results."""

            answer = await self._llm.generate(prompt, system=SUMMARIZE_SYSTEM_PROMPT)

        reasoning.append("Generated summary answer")
        return {**state, "answer": answer, "reasoning_steps": reasoning}

    async def _direct_answer(self, state: AgentState) -> AgentState:
        reasoning = state.get("reasoning_steps", [])
        question = state["question"]
        history = state.get("conversation_history", [])

        history_text = ""
        if history:
            history_text = "\n".join(
                f"{m['role']}: {m['content']}" for m in history[-6:]
            )

        prompt = f"{history_text}\n\nUser: {question}" if history_text else question
        answer = await self._llm.generate(
            prompt,
            system="You are Eutridats, a personal knowledge graph assistant. Be helpful and concise.",
        )
        reasoning.append("Provided direct answer without graph query")
        return {**state, "answer": answer, "reasoning_steps": reasoning, "sources": []}

    def _extract_cypher(self, raw: str) -> str:
        # Extract from code blocks
        code_match = re.search(r"```(?:cypher)?\s*(.*?)```", raw, re.DOTALL | re.IGNORECASE)
        if code_match:
            return code_match.group(1).strip()

        # Find MATCH statement
        match = re.search(r"(MATCH[\s\S]+)", raw, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return raw.strip()

    async def ask(
        self,
        question: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        initial_state: AgentState = {
            "question": question,
            "needs_graph": True,
            "cypher": "",
            "graph_results": [],
            "answer": "",
            "sources": [],
            "reasoning_steps": [],
            "error": None,
            "conversation_history": conversation_history or [],
        }

        result = await self._workflow.ainvoke(initial_state)

        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "cypher": result.get("cypher"),
            "result_count": len(result.get("graph_results", [])),
            "reasoning_steps": result.get("reasoning_steps", []),
        }

    async def stream_answer(
        self,
        question: str,
        conversation_history: list[dict[str, str]] | None = None,
    ):
        """Run agent and stream the final answer."""
        result = await self.ask(question, conversation_history)
        answer = result["answer"]

        # Simulate streaming by yielding chunks
        chunk_size = 20
        for i in range(0, len(answer), chunk_size):
            yield answer[i : i + chunk_size]

        yield {"__meta__": result}
