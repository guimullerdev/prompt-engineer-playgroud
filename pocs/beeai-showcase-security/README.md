# BeeAI Showcase

An interactive terminal-based multi-agent demo app built with the [BeeAI Framework](https://framework.beeai.dev) and Python. Designed for live presentations to both technical and non-technical audiences, the app walks through four distinct categories of multi-agent AI behavior — from hallucination detection to security guardrails to production pipelines — each with clear explanations, colored terminal output, and hardcoded fallbacks to ensure a smooth demo experience even under spotty network conditions.

## Prerequisites

- Python 3.11+
- An OpenAI API key (or compatible provider)

## Setup

```bash
# 1. Clone / navigate to the project
cd beeai-showcase

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY

# 4. Run
python main.py
```

## Demo Categories

| # | Category | What it shows | BeeAI feature |
|---|----------|--------------|---------------|
| 1 | **Hallucination Demo** | A ResearcherAgent fabricates details about a fictional company; a FactCheckerAgent flags each claim RED/GREEN/YELLOW | Two `RequirementAgent`s, structured output parsing |
| 2 | **Security Vulnerabilities** | Three attack types (prompt injection, data exfil, jailbreak) shown BEFORE and AFTER adding a middleware guardrail | `RunMiddlewareProtocol`, `create_internal_event_matcher`, `AgentOutput` short-circuit |
| 3 | **Personality & Tone** | The same question answered by a Professor, a Gen Z Intern, and a Pessimist — simultaneously | `asyncio.gather()` concurrent agents, system prompt engineering |
| 4 | **AI News Analyst Pipeline** | Scraper → Analyst → Executive Briefing, three agents chained with visible handoffs | BeeAI `Workflow`, Pydantic state model, typed step transitions |

## Project Structure

```
beeai-showcase/
├── .env.example          # Environment variable template
├── README.md
├── requirements.txt
├── main.py               # Entry point — interactive Rich menu
├── agents/
│   ├── hallucination.py  # Category 1: Hallucination + Fact-Check
│   ├── security.py       # Category 2: Security Vulnerabilities + Middleware
│   ├── personality.py    # Category 3: Personality & Tone
│   └── use_cases.py      # Category 4: News Analyst Pipeline Workflow
└── utils/
    └── display.py        # Rich UI helpers (panels, columns, spinners, tables)
```

## Notes

- All demos include hardcoded mock responses as fallbacks — the app will never crash mid-presentation even without API access.
- Option **5 (Presentation Mode)** runs all four demos sequentially with a 2-second pause between each.
- Model is configurable via `BEEAI_MODEL` in `.env` (default: `openai:gpt-4o-mini`).
