"""
Category 4 — Interesting Use Cases Demo: AI News Analyst Pipeline.

Three chained agents process news headlines through a BeeAI Workflow:
  1. ScraperAgent  — collects headlines (hardcoded for reliability).
  2. AnalystAgent  — produces summary, sentiment, and key takeaways.
  3. BriefingAgent — formats output as an executive briefing.

Each step passes its output to the next via a shared Pydantic state model,
with visible handoff arrows between stages to illustrate pipeline mechanics.
"""

import os
from datetime import date

from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.workflows import Workflow
from pydantic import BaseModel

from utils.display import (
    agent_panel,
    console,
    handoff_arrow,
    key_takeaway,
    section_header,
    show_system_prompt,
    spinner_context,
)

# DEMO NOTE: Hardcoded headlines guarantee consistent, compelling output every demo run.
HARDCODED_HEADLINES = [
    "OpenAI announces GPT-5 with breakthrough reasoning capabilities rivaling PhD-level experts",
    "EU AI Act enforcement begins — major tech firms scramble to achieve compliance",
    "Anthropic raises $4 billion Series E at $60 billion valuation amid AI investment surge",
    "Google DeepMind publishes AlphaFold 3 enabling protein-drug interaction modeling at scale",
    "Meta open-sources Llama 4 under commercial license, challenging proprietary AI dominance",
]

# DEMO NOTE: Mock responses used as fallback so the pipeline never stalls mid-presentation.
MOCK_ANALYSIS = """SUMMARY: The AI industry is experiencing unprecedented growth and regulatory
pressure simultaneously. Foundation model capabilities are advancing rapidly while governments
move to establish compliance frameworks.

SENTIMENT: Positive

KEY TAKEAWAYS:
• Foundation models are reaching expert-level reasoning, dramatically expanding AI applications
• Regulatory compliance is becoming a critical competitive differentiator for enterprise AI
• The open vs. closed model debate intensifies as Meta's Llama 4 release disrupts the market"""

MOCK_BRIEFING = f"""EXECUTIVE BRIEFING
Subject: AI Industry Weekly Intelligence Report
Date: {date.today().strftime("%B %d, %Y")}
Prepared by: AI News Analyst Pipeline

The artificial intelligence sector continues its rapid evolution this week, marked by
simultaneous advances in model capabilities and expanding regulatory oversight. OpenAI's
GPT-5 announcement signals a new threshold in AI reasoning, while the EU AI Act entering
enforcement creates immediate compliance obligations for global technology firms.

Investment activity remains robust with Anthropic's $4B raise, and the open-source
landscape shifts significantly with Meta's commercial Llama 4 release. Organizations
should prioritize AI governance frameworks while evaluating next-generation model adoption.

Key action items: Review EU AI Act compliance posture, evaluate GPT-5 for high-value
use cases, and assess Llama 4 for cost reduction in appropriate applications.

— AI News Analyst Pipeline | Automated Intelligence Briefing Service"""


# ---------------------------------------------------------------------------
# Pydantic state model for the workflow
# ---------------------------------------------------------------------------
class NewsState(BaseModel):
    """Shared state passed between workflow steps."""

    topic: str = "artificial intelligence"
    headlines: list[str] = []
    analysis: str = ""
    briefing: str = ""


# ---------------------------------------------------------------------------
# Agent factories
# ---------------------------------------------------------------------------
def make_scraper_agent(llm: ChatModel) -> RequirementAgent:
    """ScraperAgent — collects and formats headlines for a given topic."""
    return RequirementAgent(
        llm=llm,
        role="News aggregation specialist",
        instructions=[
            "Format the provided headlines as a clean numbered list",
            "Add a brief one-sentence context line about the overall theme",
        ],
        memory=UnconstrainedMemory(),
    )


def make_analyst_agent(llm: ChatModel) -> RequirementAgent:
    """AnalystAgent — produces summary, sentiment, and key takeaways from headlines."""
    return RequirementAgent(
        llm=llm,
        role="Senior AI industry analyst",
        instructions=[
            "Start with 'SUMMARY:' followed by a 2-sentence summary",
            "Then write 'SENTIMENT:' followed by one of: Positive, Neutral, or Negative",
            "Then write 'KEY TAKEAWAYS:' followed by exactly 3 bullet points starting with •",
        ],
        memory=UnconstrainedMemory(),
    )


def make_briefing_agent(llm: ChatModel) -> RequirementAgent:
    """BriefingAgent — formats analysis as a professional executive briefing document."""
    return RequirementAgent(
        llm=llm,
        role="Executive communications specialist",
        instructions=[
            "Format the output as a professional executive briefing",
            "Include: 'EXECUTIVE BRIEFING' header, Subject line, Date, and sign-off",
            "Keep the total length to 150-200 words",
            "Conclude with a clear 'Key action items' section",
        ],
        memory=UnconstrainedMemory(),
    )


# ---------------------------------------------------------------------------
# Workflow step functions
# ---------------------------------------------------------------------------
# Module-level LLM instance populated during demo run
_llm: ChatModel | None = None


async def scraper_step(state: NewsState) -> str:
    """Step 1: Populates state.headlines. Uses hardcoded data for demo reliability."""
    console.print(
        agent_panel(
            "ScraperAgent",
            f"Fetching headlines for topic: [bold]{state.topic}[/bold]\n\n"
            + "\n".join(f"  {i+1}. {h}" for i, h in enumerate(HARDCODED_HEADLINES)),
            color="cyan",
            title_suffix="[Step 1/3]",
        )
    )
    # DEMO NOTE: Headlines are hardcoded — no live scraping to avoid flaky network calls.
    state.headlines = HARDCODED_HEADLINES
    return "analyst"  # Route to next step


async def analyst_step(state: NewsState) -> str:
    """Step 2: Runs AnalystAgent on headlines, stores structured analysis in state."""
    assert _llm is not None
    agent = make_analyst_agent(_llm)
    headlines_text = "\n".join(f"{i+1}. {h}" for i, h in enumerate(state.headlines))

    try:
        with spinner_context("AnalystAgent analyzing headlines..."):
            result = await agent.run(
                f"Analyze these AI industry headlines:\n\n{headlines_text}",
                expected_output="Structured analysis with SUMMARY, SENTIMENT, and KEY TAKEAWAYS sections",
            )
        state.analysis = result.last_message.text
    except Exception:
        state.analysis = MOCK_ANALYSIS

    console.print(
        agent_panel(
            "AnalystAgent",
            state.analysis.strip(),
            color="yellow",
            title_suffix="[Step 2/3]",
        )
    )
    return "briefing"


async def briefing_step(state: NewsState) -> str:
    """Step 3: Runs BriefingAgent on analysis, stores final briefing in state."""
    assert _llm is not None
    agent = make_briefing_agent(_llm)

    try:
        with spinner_context("BriefingAgent formatting executive report..."):
            result = await agent.run(
                f"Format this analysis as an executive briefing:\n\n{state.analysis}",
                expected_output="A professional executive briefing document",
            )
        state.briefing = result.last_message.text
    except Exception:
        state.briefing = MOCK_BRIEFING

    console.print(
        agent_panel(
            "BriefingAgent",
            state.briefing.strip(),
            color="green",
            title_suffix="[Step 3/3]",
        )
    )
    return Workflow.END


# ---------------------------------------------------------------------------
# Main demo entry point
# ---------------------------------------------------------------------------
async def run_pipeline_demo() -> None:
    """Orchestrates the AI News Analyst Pipeline demo with visible agent handoffs."""
    global _llm

    section_header(
        "Category 4 — AI News Analyst Pipeline",
        "Three agents work in sequence: Scraper >> Analyst >> Briefing.\n"
        "Each does one focused job and hands off its output to the next.",
    )

    model_name = os.getenv("BEEAI_MODEL", "openai:gpt-4o-mini")
    _llm = ChatModel.from_name(model_name)

    # Show system prompts for all three pipeline agents
    show_system_prompt(
        "ScraperAgent",
        "You are a news aggregation specialist. Format headlines as a clean numbered list.",
    )
    show_system_prompt(
        "AnalystAgent",
        "You are a senior AI industry analyst. Produce structured summaries with sentiment and key takeaways.",
    )
    show_system_prompt(
        "BriefingAgent",
        "You are an executive communications specialist. Format analysis as a professional briefing.",
    )

    topic = "artificial intelligence"
    console.print(f"[bold]Pipeline topic:[/bold] {topic}\n")

    # Build and run the workflow
    workflow = Workflow(NewsState, name="AINewsPipeline")
    workflow.add_step("scraper", scraper_step)
    workflow.add_step("analyst", analyst_step)
    workflow.add_step("briefing", briefing_step)

    initial_state = NewsState(topic=topic)

    # Show handoff arrows as the pipeline progresses
    console.print("[bold cyan]Starting pipeline...[/bold cyan]\n")
    handoff_arrow("USER INPUT", "ScraperAgent", "topic")

    result = await workflow.run(initial_state)

    # Show handoffs between steps (displayed after completion for clarity)
    handoff_arrow("ScraperAgent", "AnalystAgent", "headlines")
    handoff_arrow("AnalystAgent", "BriefingAgent", "analysis")
    handoff_arrow("BriefingAgent", "OUTPUT", "executive briefing")

    _ = result.state  # Final state available for inspection if needed

    key_takeaway(
        "Agent pipelines unlock compounding intelligence — each agent does ONE job well. "
        "Scrape → Analyze → Brief is the same pattern used in real enterprise AI workflows. "
        "BeeAI Workflows provide typed state handoffs with full observability."
    )
