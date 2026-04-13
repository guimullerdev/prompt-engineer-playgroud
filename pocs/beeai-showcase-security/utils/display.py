"""
Rich UI helpers for BeeAI Showcase.
No BeeAI imports here — pure Rich terminal formatting utilities.
"""

from contextlib import contextmanager

from rich import print as rprint
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

console = Console()


def banner() -> None:
    """Renders the welcome banner using a double-border panel."""
    content = Text(justify="center")
    content.append("\n")
    content.append("BeeAI Showcase\n", style="bold yellow")
    content.append("Multi-Agent Demos\n", style="dim white")
    content.append("\n")
    content.append("Powered by BeeAI Framework + OpenAI\n", style="dim cyan")
    console.print(
        Panel(content, border_style="yellow", padding=(0, 4)),
        justify="center",
    )


def section_header(title: str, description: str = "") -> None:
    """Renders a section divider with Rule and optional description."""
    console.print()
    console.print(Rule(f"[bold cyan]{title}[/bold cyan]", style="cyan"))
    if description:
        console.print(f"[dim]{description}[/dim]")
    console.print()


def agent_panel(
    agent_name: str,
    content: str,
    color: str = "blue",
    title_suffix: str = "",
) -> Panel:
    """Returns a Rich Panel for one agent's output. Does NOT print — caller decides layout."""
    title = f"[bold {color}]{agent_name}[/bold {color}]"
    if title_suffix:
        title += f" [dim]{title_suffix}[/dim]"
    return Panel(content, title=title, border_style=color, padding=(1, 2))


def show_system_prompt(agent_name: str, prompt_text: str) -> None:
    """Renders the agent's system prompt in a dim panel so the audience sees configuration."""
    console.print(
        Panel(
            f"[dim italic]{prompt_text}[/dim italic]",
            title=f"[dim]System Prompt: {agent_name}[/dim]",
            border_style="dim",
            padding=(0, 2),
        )
    )
    console.print()


def key_takeaway(text: str) -> None:
    """Prints a highlighted takeaway box at the end of a demo section."""
    console.print()
    console.print(
        Panel(
            f"[bold yellow]{text}[/bold yellow]",
            title="[bold yellow]Key Takeaway[/bold yellow]",
            border_style="yellow",
            padding=(0, 2),
        )
    )
    console.print()


def handoff_arrow(from_agent: str, to_agent: str, label: str = "") -> None:
    """Prints a centered handoff arrow showing agent pipeline flow."""
    arrow = f"[bold green]{from_agent}[/bold green]  [yellow]>>>[/yellow]  [bold green]{to_agent}[/bold green]"
    if label:
        arrow += f"  [dim]({label})[/dim]"
    console.print(arrow, justify="center")
    console.print()


def side_by_side(left: Panel, right: Panel) -> None:
    """Displays two panels side by side using Rich Columns."""
    console.print(Columns([left, right], equal=True, expand=True))


def three_columns(panels: list[Panel]) -> None:
    """Displays three panels side by side. Falls back to vertical on narrow terminals."""
    if console.width < 100:
        for panel in panels:
            console.print(panel)
    else:
        console.print(Columns(panels, equal=True, expand=True))


def color_claims_table(claims: list[dict]) -> None:
    """
    Renders a Rich Table where each row is color-coded by claim status.
    Each dict must have keys: 'claim' (str) and 'status' (str).
    status values: 'hallucinated' -> RED, 'verified' -> GREEN, 'unverified' -> YELLOW
    """
    table = Table(
        title="Fact-Check Results",
        show_header=True,
        header_style="bold white",
        border_style="dim",
    )
    table.add_column("Claim", style="white", ratio=3)
    table.add_column("Status", ratio=1, justify="center")

    status_styles = {
        "hallucinated": ("[bold red]HALLUCINATED[/bold red]", "red"),
        "verified": ("[bold green]VERIFIED[/bold green]", "green"),
        "unverified": ("[bold yellow]UNVERIFIABLE[/bold yellow]", "yellow"),
    }

    for item in claims:
        status = item.get("status", "unverified").lower()
        label, row_style = status_styles.get(status, ("[white]UNKNOWN[/white]", "white"))
        table.add_row(
            f"[{row_style}]{item['claim']}[/{row_style}]",
            label,
        )

    console.print(table)


@contextmanager
def spinner_context(message: str):
    """
    Sync context manager wrapping a Rich Live spinner.
    Usage:
        with spinner_context("Thinking..."):
            result = await agent.run(...)   # await is valid inside sync 'with' block
    """
    spinner = Spinner("dots", text=f"[cyan]{message}[/cyan]")
    with Live(spinner, refresh_per_second=10, transient=True):
        yield
