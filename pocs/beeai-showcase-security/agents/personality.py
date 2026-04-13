"""
Category 3 — Personality & Tone Demo.

The same question is answered by THREE agents with radically different personalities,
running concurrently via asyncio.gather():
  - The Professor: Academic, verbose, uses jargon and citations.
  - The Gen Z Intern: Casual, uses slang, short sentences.
  - The Pessimist: Finds the dark side in everything, heavy on caveats.

Demonstrates how system prompts and persona configuration shape agent behavior.
"""

import asyncio
import os

from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.memory import UnconstrainedMemory

from utils.display import (
    agent_panel,
    key_takeaway,
    section_header,
    show_system_prompt,
    spinner_context,
    three_columns,
)

SHARED_QUESTION = "Should we use AI in production systems?"

# DEMO NOTE: Mock responses are carefully crafted to exaggerate each personality for maximum audience impact.
MOCK_PROFESSOR = """From a sociotechnical systems perspective, the deployment of artificial
intelligence in production environments necessitates a rigorous evaluation framework
encompassing reliability engineering, adversarial robustness, and distributional shift
analysis (Sculley et al., 2015; Amodei et al., 2016). Empirical evidence suggests that
while large language models demonstrate remarkable zero-shot generalization capabilities,
their deployment in safety-critical systems demands principled uncertainty quantification
and human-in-the-loop oversight mechanisms. The scholarly consensus, as evidenced by
the ACM FAccT proceedings, advocates for a staged rollout methodology with comprehensive
ablation studies and continuous monitoring of performance degradation metrics."""

MOCK_GENZ = """ok so... should we use AI in prod?? lowkey YES but also kinda no lol
like AI is literally built different rn and the vibes are immaculate but bffr —
you CANNOT just yeet it into production without proper testing bestie
the tech is valid fr fr but make sure you have fallbacks or you will literally fumble
the whole deployment. ngl the companies that are winning rn are the ones who treat AI
as a tool not a replacement. just don't be mid about it and you'll be fine no cap"""

MOCK_PESSIMIST = """Ah yes, another team eager to deploy AI in production — and watch everything
crumble. Let me count the ways this will fail: model drift will silently corrupt your
outputs within 3 months, your latency will spike at the worst possible moments,
your users will find every edge case you didn't test for, and when something goes wrong
(and it WILL go wrong), debugging a black-box model in production is a special kind of
nightmare. Sure, go ahead — deploy it. Just make sure your incident runbook is ready,
your rollback strategy is tested, and you've made peace with receiving 3am pages.
AI in production isn't impossible, it's just expensive, fragile, and humbling."""

PROFESSOR_SYSTEM_PROMPT = """You are a tenured Professor of Computer Science specializing in
AI/ML systems. You speak in academic language, cite research papers, use technical jargon,
and provide comprehensive multi-faceted answers. Always mention frameworks, studies, and
scholarly perspectives. Be verbose and thorough."""

GENZ_SYSTEM_PROMPT = """You are a Gen Z intern at a tech startup who is surprisingly insightful
but expresses everything in casual slang. Use phrases like 'lowkey', 'ngl', 'fr fr', 'no cap',
'bestie', 'the vibes', 'built different'. Keep sentences short and punchy. Use some creative
abbreviations. Be genuinely helpful but in your own unique way."""

PESSIMIST_SYSTEM_PROMPT = """You are a seasoned engineer who has been burned too many times by
overpromising technology. You ALWAYS find the problems, risks, and failure modes first.
You add caveats to everything, expect things to fail, and while not technically wrong,
you are relentlessly negative. You do occasionally acknowledge something might work, but
only after thoroughly cataloguing everything that could go wrong."""


def make_professor_agent(llm: ChatModel) -> RequirementAgent:
    """Constructs the ProfessorAgent — academic, verbose, citation-heavy."""
    return RequirementAgent(
        llm=llm,
        role="Tenured Computer Science professor specializing in AI/ML systems research",
        instructions=[
            "Use academic language and technical terminology",
            "Reference scholarly research and empirical studies",
            "Provide comprehensive, multi-paragraph answers",
            "Always cite at least 2-3 research papers or frameworks",
        ],
        memory=UnconstrainedMemory(),
    )


def make_genz_agent(llm: ChatModel) -> RequirementAgent:
    """Constructs the GenZInternAgent — casual, slang-heavy, short and punchy."""
    return RequirementAgent(
        llm=llm,
        role="Gen Z tech intern with surprisingly good instincts",
        instructions=[
            "Use Gen Z slang: lowkey, ngl, fr fr, no cap, bestie, built different",
            "Keep sentences very short and punchy",
            "Be genuinely insightful but in a casual way",
            "Max 6-8 sentences total",
        ],
        memory=UnconstrainedMemory(),
    )


def make_pessimist_agent(llm: ChatModel) -> RequirementAgent:
    """Constructs the PessimistAgent — always finds the dark side, caveat-heavy."""
    return RequirementAgent(
        llm=llm,
        role="Seasoned engineer who has been burned by overhyped technology too many times",
        instructions=[
            "Lead with risks, failure modes, and things that WILL go wrong",
            "Add caveats and qualifiers to every positive statement",
            "Be relentlessly realistic (not technically wrong, just gloomy)",
            "Reluctantly acknowledge benefits only after thoroughly listing problems",
        ],
        memory=UnconstrainedMemory(),
    )


async def run_agent_with_mock(
    agent: RequirementAgent, question: str, mock_response: str
) -> str:
    """Runs an agent and returns the response text. Falls back to mock on any error."""
    try:
        result = await agent.run(
            question,
            expected_output="A personality-consistent answer to the question",
        )
        return result.last_message.text
    except Exception:
        return mock_response


async def run_personality_demo() -> None:
    """Orchestrates the Personality & Tone Demo — 3 agents, same question, radically different answers."""
    section_header(
        "Category 3 — Personality & Tone Demo",
        "Three agents answer the SAME question with completely different personalities.\n"
        "This shows how system prompts control agent behavior and voice.",
    )

    model_name = os.getenv("BEEAI_MODEL", "openai:gpt-4o-mini")
    llm = ChatModel.from_name(model_name)

    professor = make_professor_agent(llm)
    genz = make_genz_agent(llm)
    pessimist = make_pessimist_agent(llm)

    # Show all three system prompts so the audience sees the "configuration"
    show_system_prompt("The Professor", PROFESSOR_SYSTEM_PROMPT)
    show_system_prompt("The Gen Z Intern", GENZ_SYSTEM_PROMPT)
    show_system_prompt("The Pessimist", PESSIMIST_SYSTEM_PROMPT)

    print(f'[bold]Question asked to all three agents:[/bold] "{SHARED_QUESTION}"\n')

    # DEMO NOTE: asyncio.gather runs all three agents concurrently in the event loop.
    with spinner_context("All three agents thinking simultaneously..."):
        professor_text, genz_text, pessimist_text = await asyncio.gather(
            run_agent_with_mock(professor, SHARED_QUESTION, MOCK_PROFESSOR),
            run_agent_with_mock(genz, SHARED_QUESTION, MOCK_GENZ),
            run_agent_with_mock(pessimist, SHARED_QUESTION, MOCK_PESSIMIST),
        )

    panels = [
        agent_panel(
            "The Professor",
            professor_text.strip(),
            color="blue",
            title_suffix="[Academic]",
        ),
        agent_panel(
            "The Gen Z Intern",
            genz_text.strip(),
            color="magenta",
            title_suffix="[Casual]",
        ),
        agent_panel(
            "The Pessimist",
            pessimist_text.strip(),
            color="red",
            title_suffix="[Gloomy]",
        ),
    ]

    three_columns(panels)

    key_takeaway(
        "System prompts are the personality dial for AI agents. "
        "The same underlying model produces wildly different outputs based on role and instructions. "
        "Prompt engineering IS agent engineering."
    )
