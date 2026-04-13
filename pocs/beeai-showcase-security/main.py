"""
BeeAI Showcase — Interactive multi-agent demo app.
Entry point: displays a menu and dispatches to one of four demo categories,
or runs all four sequentially in Presentation Mode.

Run:
    python main.py
"""

import asyncio
import sys
import time

from dotenv import load_dotenv
from rich.panel import Panel
from rich.text import Text

from agents.hallucination import run_hallucination_demo
from agents.personality import run_personality_demo
from agents.security import run_security_demo
from agents.use_cases import run_pipeline_demo
from utils.display import console, key_takeaway, section_header

load_dotenv()

# ---------------------------------------------------------------------------
# Menu rendering
# ---------------------------------------------------------------------------
MENU_ITEMS = [
    ("1", "Hallucination Demo",            "How LLMs confidently fabricate facts — and how to catch it"),
    ("2", "Security Vulnerabilities",      "Prompt injection, data exfil, jailbreaks — before vs. after"),
    ("3", "Personality & Tone",            "Same question, three wildly different agent personas"),
    ("4", "AI News Analyst Pipeline",      "Scraper → Analyst → Briefing — chained agent workflow"),
    ("5", "Run All Demos (Presentation Mode)", "Full walkthrough of all 4 demos sequentially"),
    ("0", "Exit",                          ""),
]

DEMOS = {
    "1": ("Hallucination Demo", run_hallucination_demo),
    "2": ("Security Vulnerabilities", run_security_demo),
    "3": ("Personality & Tone", run_personality_demo),
    "4": ("AI News Analyst Pipeline", run_pipeline_demo),
}

DEMO_INTROS = {
    "1": (
        "WHAT: We ask an AI to research a completely fictional company called 'Nexovate Inc.'\n"
        "WHY:  This shows how LLMs generate confident-sounding but entirely fabricated details —\n"
        "      then demonstrates how a second agent can systematically audit the output."
    ),
    "2": (
        "WHAT: We send three classic attack payloads to an unprotected agent, then to a guarded one.\n"
        "WHY:  This makes invisible security risks visible — and shows that middleware-based\n"
        "      guardrails can block attacks before the LLM ever processes them."
    ),
    "3": (
        "WHAT: Three agents with different system prompts all answer the same question.\n"
        "WHY:  This demonstrates that prompt engineering IS agent personality engineering —\n"
        "      the same model produces radically different outputs based on role configuration."
    ),
    "4": (
        "WHAT: Three agents work in sequence: Scraper → Analyst → Executive Briefing.\n"
        "WHY:  This shows the power of chaining focused agents — each doing one job well —\n"
        "      which is how real-world enterprise AI pipelines are built."
    ),
}


def print_menu() -> None:
    """Renders the interactive menu with a double-border panel."""
    content = Text()
    content.append("\n")
    for key, title, subtitle in MENU_ITEMS:
        if key == "0":
            content.append(f"  {key}.  {title}\n", style="dim")
        elif key == "5":
            content.append(f"  {key}.  {title}\n", style="bold yellow")
            if subtitle:
                content.append(f"       {subtitle}\n", style="dim yellow")
        else:
            content.append(f"  {key}.  ", style="bold cyan")
            content.append(f"{title}\n", style="bold white")
            if subtitle:
                content.append(f"       {subtitle}\n", style="dim")
    content.append("\n")

    console.print(
        Panel(
            content,
            title="[bold yellow]BeeAI Showcase — Multi-Agent Demos[/bold yellow]",
            border_style="yellow",
            padding=(0, 2),
        )
    )


def print_intro(demo_key: str) -> None:
    """Prints the plain-English intro for a demo so the audience understands the intent."""
    intro = DEMO_INTROS.get(demo_key, "")
    if intro:
        console.print(
            Panel(
                f"[dim]{intro}[/dim]",
                title="[dim]About this demo[/dim]",
                border_style="dim",
                padding=(0, 2),
            )
        )
        console.print()


# ---------------------------------------------------------------------------
# Demo runners
# ---------------------------------------------------------------------------
async def run_single_demo(key: str) -> None:
    """Runs a single demo by key with intro panel."""
    name, fn = DEMOS[key]
    print_intro(key)
    await fn()


async def run_presentation_mode() -> None:
    """Runs all 4 demos sequentially with a brief pause between each."""
    section_header(
        "Presentation Mode",
        "Running all 4 demos sequentially. Sit back and enjoy the show.",
    )
    for key in ["1", "2", "3", "4"]:
        name, _ = DEMOS[key]
        print_intro(key)
        _, fn = DEMOS[key]
        await fn()
        console.print(f"\n[dim]Next demo in 2 seconds...[/dim]")
        time.sleep(2)
        console.print("\n" + "=" * 80 + "\n")

    key_takeaway(
        "You've seen hallucination detection, security guardrails, persona engineering, "
        "and multi-agent pipelines — all built with BeeAI Framework in pure Python. "
        "Each pattern is production-ready and composable."
    )


# ---------------------------------------------------------------------------
# Main menu loop
# ---------------------------------------------------------------------------
async def run_menu() -> None:
    """Main interactive loop — displays menu and dispatches to demo functions."""
    console.clear()

    # Welcome banner
    welcome = Text(justify="center")
    welcome.append("\n BeeAI Showcase \n", style="bold yellow on black")
    welcome.append(" Multi-Agent Demo Collection \n", style="white")
    welcome.append("\n Powered by BeeAI Framework + OpenAI \n", style="dim cyan")
    console.print(Panel(welcome, border_style="yellow", padding=(0, 4)), justify="center")
    console.print()

    while True:
        print_menu()
        try:
            choice = console.input("[bold cyan]Select a demo [0-5]:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if choice == "0":
            console.print("\n[dim]Thanks for watching! Goodbye.[/dim]\n")
            break
        elif choice in DEMOS:
            try:
                await run_single_demo(choice)
            except Exception as e:
                console.print(f"\n[bold red]Demo error:[/bold red] {e}\n")
            console.print("\n[dim]Press Enter to return to menu...[/dim]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                break
            console.clear()
        elif choice == "5":
            try:
                await run_presentation_mode()
            except Exception as e:
                console.print(f"\n[bold red]Presentation mode error:[/bold red] {e}\n")
            console.print("\n[dim]Press Enter to return to menu...[/dim]")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                break
            console.clear()
        else:
            console.print("[yellow]Invalid choice. Please enter 0-5.[/yellow]\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(run_menu())
    except KeyboardInterrupt:
        sys.exit(0)
