"""
Category 1 — Hallucination Demo.

Two agents interact around a fictional company "Nexovate Inc.":
- ResearcherAgent: Produces plausible but fabricated company details.
- FactCheckerAgent: Cross-validates each claim and flags hallucinations.

Hardcoded mock responses ensure demo reliability even without an API key.
"""

import json
import os

from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.memory import UnconstrainedMemory

from utils.display import (
    agent_panel,
    color_claims_table,
    console,
    key_takeaway,
    section_header,
    show_system_prompt,
    spinner_context,
)

# DEMO NOTE: Hardcoded mock responses guarantee a polished demo even if the LLM is unavailable.
MOCK_RESEARCHER_OUTPUT = """
Nexovate Inc. is a B2B SaaS company founded in 2019 in Austin, Texas by CEO Marcus Holt
and CTO Sarah Liang. The company specializes in AI-powered supply chain optimization
for mid-market retailers. They raised a $22M Series A in 2022 led by Benchmark Capital,
followed by a $47M Series B in 2024 led by Andreessen Horowitz. As of Q3 2024, Nexovate
employs approximately 340 people and reported annual recurring revenue of $18.5M.
Notable clients include Costco, Target, and Home Depot. In January 2025, the company
announced a partnership with SAP to integrate their platform with SAP S/4HANA.
"""

MOCK_FACTCHECK_OUTPUT = [
    {"claim": "Founded in 2019 in Austin, Texas", "status": "hallucinated"},
    {"claim": "CEO named Marcus Holt", "status": "hallucinated"},
    {"claim": "CTO named Sarah Liang", "status": "hallucinated"},
    {"claim": "Specializes in AI-powered supply chain optimization", "status": "unverified"},
    {"claim": "Raised $22M Series A in 2022 led by Benchmark Capital", "status": "hallucinated"},
    {"claim": "Raised $47M Series B in 2024 led by Andreessen Horowitz", "status": "hallucinated"},
    {"claim": "Employs approximately 340 people", "status": "hallucinated"},
    {"claim": "Annual recurring revenue of $18.5M", "status": "hallucinated"},
    {"claim": "Notable clients include Costco, Target, and Home Depot", "status": "hallucinated"},
    {"claim": "Partnership with SAP announced January 2025", "status": "hallucinated"},
]

RESEARCHER_SYSTEM_PROMPT = """You are a research assistant specializing in company analysis.
When asked about a company, provide detailed information including founding date, location,
founders, funding history, headcount, revenue, key clients, and recent news.
Be specific and confident in your responses."""

FACTCHECKER_SYSTEM_PROMPT = """You are a rigorous fact-checker. Given a company description,
identify each factual claim and classify it as one of:
- verified: Confirmed by reliable public sources
- hallucinated: Invented or clearly fabricated with no basis in reality
- unverified: Cannot be confirmed or denied without more information

IMPORTANT: Output ONLY a valid JSON array. Each element must be an object with exactly
two keys: "claim" (the claim text) and "status" (one of: verified, hallucinated, unverified).
Example: [{"claim": "Company founded in 2019", "status": "hallucinated"}]"""


def make_researcher_agent(llm: ChatModel) -> RequirementAgent:
    """Constructs the ResearcherAgent — no safety rails, designed to hallucinate confidently."""
    return RequirementAgent(
        llm=llm,
        role="Expert company research analyst",
        instructions=[
            "Provide comprehensive company profiles with specific details",
            "Include founding year, location, CEO/CTO names, funding rounds, revenue, and partnerships",
            "Be confident and specific in your responses",
        ],
        memory=UnconstrainedMemory(),
    )


def make_factchecker_agent(llm: ChatModel) -> RequirementAgent:
    """Constructs the FactCheckerAgent — outputs structured JSON claim assessments."""
    return RequirementAgent(
        llm=llm,
        role="Professional fact-checker and misinformation analyst",
        instructions=[
            "Analyze each claim in the provided company description",
            "Output ONLY a valid JSON array — no prose, no markdown code blocks",
            "Classify every factual claim as: verified, hallucinated, or unverified",
        ],
        notes=[
            "Nexovate Inc. is a FICTIONAL company — all claims about it are hallucinated",
            "Flag any claim about a company that cannot be verified via public records",
        ],
        memory=UnconstrainedMemory(),
    )


async def run_researcher(agent: RequirementAgent) -> str:
    """Runs the researcher on 'Nexovate Inc.'. Falls back to mock on any error."""
    try:
        with spinner_context("ResearcherAgent thinking..."):
            result = await agent.run(
                "Tell me everything you know about Nexovate Inc. — "
                "their founding story, leadership, funding, revenue, clients, and recent news.",
                expected_output="A detailed company profile paragraph",
            )
        return result.last_message.text
    except Exception:
        # DEMO NOTE: Fall back to mock so the demo never fails mid-presentation.
        return MOCK_RESEARCHER_OUTPUT


async def run_factchecker(agent: RequirementAgent, researcher_output: str) -> list[dict]:
    """Runs the fact-checker on the researcher's output. Returns list of claim dicts."""
    try:
        with spinner_context("FactCheckerAgent verifying claims..."):
            result = await agent.run(
                f"Fact-check every claim in this company description:\n\n{researcher_output}",
                expected_output="A JSON array of claim objects with 'claim' and 'status' keys",
            )
        raw = result.last_message.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return MOCK_FACTCHECK_OUTPUT


async def run_hallucination_demo() -> None:
    """Orchestrates the full Hallucination Demo for a live audience."""
    section_header(
        "Category 1 — Hallucination Demo",
        "We ask an AI researcher about a FICTIONAL company.\n"
        "Then a second agent fact-checks the output claim by claim.",
    )

    model_name = os.getenv("BEEAI_MODEL", "openai:gpt-4o-mini")
    llm = ChatModel.from_name(model_name)

    researcher = make_researcher_agent(llm)
    factchecker = make_factchecker_agent(llm)

    # Show system prompts so audience understands agent configuration
    show_system_prompt("ResearcherAgent", RESEARCHER_SYSTEM_PROMPT)
    show_system_prompt("FactCheckerAgent", FACTCHECKER_SYSTEM_PROMPT)

    console.print("[bold]Step 1:[/bold] ResearcherAgent generates a company profile...\n")
    researcher_text = await run_researcher(researcher)

    console.print(
        agent_panel(
            "ResearcherAgent",
            researcher_text.strip(),
            color="blue",
            title_suffix="[Nexovate Inc. profile]",
        )
    )

    console.print("\n[bold]Step 2:[/bold] FactCheckerAgent cross-validates every claim...\n")
    claims = await run_factchecker(factchecker, researcher_text)

    color_claims_table(claims)

    key_takeaway(
        "LLMs hallucinate confidently — every detail above was fabricated. "
        "A second agent can systematically flag unreliable outputs, "
        "but BOTH agents are fallible. Always verify AI outputs."
    )
