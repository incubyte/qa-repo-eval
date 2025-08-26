"""
Command Line Interface for QA Repository Evaluation Tool

This module provides a Typer-based CLI for evaluating QA repositories.
"""

import os
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .metrics import (
    batch_compute_qa_metrics,
    get_evaluation_summary,
)
from .types import QAResult
from .reporter import write_reports

load_dotenv()
app = typer.Typer(
    help="QA Repository Evaluation Tool - AI-powered assessment of QA practices in repositories"
)
console = Console()


def read_repo_urls_from_file(file_path: Path) -> List[str]:
    """Read repository URLs from a text file."""
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/]")
        raise typer.Exit(code=1)

    urls = []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith("#"):  # Skip empty lines and comments
                    urls.append(line)

        if not urls:
            console.print(f"[yellow]No repository URLs found in {file_path}[/]")
            raise typer.Exit(code=1)

        return urls

    except Exception as e:
        console.print(f"[red]Error reading file {file_path}: {e}[/]")
        raise typer.Exit(code=1)


def validate_environment():
    """Validate environment setup and show helpful messages."""
    issues = []

    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY environment variable not set")

    # Check dependencies
    try:
        import git
    except ImportError:
        issues.append("GitPython not installed (pip install gitpython)")

    try:
        import openai
    except ImportError:
        issues.append("OpenAI library not installed (pip install openai)")

    if issues:
        console.print("[red]Environment configuration issues:[/]")
        for issue in issues:
            console.print(f"  • {issue}")

        if "OPENAI_API_KEY" in str(issues):
            console.print("\n[yellow]💡 To enable AI analysis:[/]")
            console.print("  Set your OpenAI API key as an environment variable:")
            console.print("  [bold]export OPENAI_API_KEY='your-api-key-here'[/]")

        console.print(
            "\n[red]Please fix these issues before running the evaluation.[/]"
        )
        raise typer.Exit(code=1)


def display_single_result(result: QAResult):
    """Display results for a single repository evaluation."""
    if result.is_successful:
        metrics = result.metrics

        # Create main results table
        table = Table(title=f"QA Evaluation Results: {result.url}")
        table.add_column("Metric", style="bold blue")
        table.add_column("Value", style="green")

        table.add_row("🎯 Overall QA Score", f"{metrics.overall_qa_maturity_score}/100")
        table.add_row("📈 QA Level", metrics.qa_level)
        table.add_row("⚖️ Final Verdict", metrics.final_verdict)
        table.add_row("💻 Primary Language", metrics.primary_language)
        table.add_row(
            "🧪 Test Files", f"{metrics.test_file_count}/{metrics.total_file_count}"
        )
        table.add_row("📊 Commit Count", str(metrics.commit_count))

        if metrics.test_frameworks:
            table.add_row("🔧 Test Frameworks", ", ".join(metrics.test_frameworks))

        console.print(table)

        # Category scores
        console.print("\n[bold]📊 Category Scores:[/]")
        category_scores = metrics.get_category_scores()
        for category, score in category_scores.items():
            bar_length = int(score)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            category_name = category.replace("_", " ").title()
            console.print(f"  {category_name:<20} {bar} {score:.1f}/10")

        # Strengths
        if metrics.strengths:
            console.print("\n[bold green]✅ Strengths:[/]")
            for strength in metrics.strengths:
                console.print(f"  • {strength}")

        # Improvement areas
        if metrics.improvement_areas:
            console.print("\n[bold yellow]⚠️ Areas for Improvement:[/]")
            for improvement in metrics.improvement_areas:
                console.print(f"  • {improvement}")

        # Verdict reasoning
        console.print("\n[bold]💭 Verdict Reasoning:[/]")
        console.print(Panel(metrics.final_verdict_reason, border_style="blue"))

    else:
        console.print(f"[red]❌ Evaluation failed for {result.url}[/]")
        console.print(f"[red]Error: {result.error_message}[/]")


def display_batch_results(results: List[QAResult]):
    """Display results for batch repository evaluation."""
    successful_results = [r for r in results if r.is_successful]
    failed_results = [r for r in results if not r.is_successful]

    # Summary statistics
    summary = get_evaluation_summary(results)

    console.print("\n[bold]📋 Batch Evaluation Summary[/]")
    console.print(f"  • Total repositories: {summary['total_repositories']}")
    console.print(f"  • Successful evaluations: {summary['successful_evaluations']}")
    console.print(f"  • Failed evaluations: {summary['failed_evaluations']}")
    console.print(f"  • Success rate: {summary['success_rate']:.1%}")

    if successful_results:
        console.print(f"  • Average QA score: {summary['average_score']:.1f}/100")

    # Results table
    if successful_results:
        table = Table(title="QA Evaluation Results")
        table.add_column("Repository", style="blue", width=40)
        table.add_column("Score", justify="center", style="bold")
        table.add_column("Level", justify="center")
        table.add_column("Verdict", justify="center")
        table.add_column("Language", justify="center")
        table.add_column("Tests", justify="center")

        for result in successful_results:
            m = result.metrics
            # Truncate long URLs
            repo_name = result.url
            if len(repo_name) > 35:
                repo_name = "..." + repo_name[-32:]

            verdict_color = (
                "green"
                if m.final_verdict == "PASS"
                else "yellow"
                if m.final_verdict == "CONDITIONAL_PASS"
                else "red"
            )

            table.add_row(
                repo_name,
                f"{m.overall_qa_maturity_score}/100",
                m.qa_level,
                f"[{verdict_color}]{m.final_verdict}[/]",
                m.primary_language,
                f"{m.test_file_count}/{m.total_file_count}",
            )

        console.print(table)

    # Score distribution
    if summary["score_distribution"]:
        console.print("\n[bold]📊 Score Distribution:[/]")
        for level, count in summary["score_distribution"].items():
            if count > 0:
                console.print(f"  • {level}: {count}")

    # Verdict distribution
    if summary["verdict_distribution"]:
        console.print("\n[bold]⚖️ Verdict Distribution:[/]")
        for verdict, count in summary["verdict_distribution"].items():
            verdict_color = (
                "green"
                if verdict == "PASS"
                else "yellow"
                if verdict == "CONDITIONAL_PASS"
                else "red"
            )
            console.print(f"  • [{verdict_color}]{verdict}[/]: {count}")

    # Failed repositories
    if failed_results:
        console.print(f"\n[bold red]❌ Failed Evaluations ({len(failed_results)}):[/]")
        for result in failed_results:
            console.print(f"  • {result.url}: {result.error_message}")


@app.command()
def evaluate(
    repo_url: str = typer.Argument(..., help="Repository URL to evaluate"),
    shallow: bool = typer.Option(
        True, "--shallow/--full", help="Use shallow clone (faster)"
    ),
    keep_clone: bool = typer.Option(
        False, "--keep-clone", help="Keep cloned repository"
    ),
    verbose: bool = typer.Option(
        True, "--verbose/--quiet", help="Show detailed progress"
    ),
):
    """Evaluate a single repository for QA practices."""
    console.print("[bold blue]🚀 QA Repository Evaluation Tool[/]")
    console.print(f"Repository: {repo_url}")
    console.print()

    # Validate environment
    validate_environment()

    # Perform evaluation using batch function with single URL
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Evaluating repository...", total=None)

        results = batch_compute_qa_metrics(
            repo_urls=[repo_url],
            shallow=shallow,
            keep_clone=keep_clone,
            verbose=verbose,
            continue_on_error=True,
        )
        result = results[0]  # Get the single result

        progress.update(task, completed=True)

    # Display results
    display_single_result(result)


@app.command()
def batch(
    input_file: Path = typer.Argument(
        ..., help="File containing repository URLs (one per line)"
    ),
    output_dir: Path = typer.Option("qa_reports", help="Directory to save reports"),
    shallow: bool = typer.Option(
        True, "--shallow/--full", help="Use shallow clones (faster)"
    ),
    keep_clone: bool = typer.Option(
        False, "--keep-clone", help="Keep cloned repositories"
    ),
    verbose: bool = typer.Option(
        True, "--verbose/--quiet", help="Show detailed progress"
    ),
    continue_on_error: bool = typer.Option(
        True, "--continue/--stop-on-error", help="Continue if a repository fails"
    ),
):
    """Evaluate multiple repositories from a file."""
    console.print("[bold blue]🔄 Batch QA Repository Evaluation[/]")
    console.print(f"Input file: {input_file}")
    console.print(f"Output directory: {output_dir}")
    console.print()

    # Validate environment
    validate_environment()

    # Read repository URLs
    repo_urls = read_repo_urls_from_file(input_file)
    console.print(f"Found {len(repo_urls)} repositories to evaluate")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Perform batch evaluation
    results = batch_compute_qa_metrics(
        repo_urls=repo_urls,
        shallow=shallow,
        keep_clone=keep_clone,
        verbose=verbose,
        continue_on_error=continue_on_error,
    )

    # Display results
    display_batch_results(results)

    # Write comprehensive reports
    created_files = write_reports(results, output_dir)

    console.print("\n[green]✅ Reports generated:[/]")
    for file_path in created_files:
        console.print(f"  • {file_path.name}")
    console.print(f"[green]📁 Output directory: {output_dir}[/]")


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"QA Repository Evaluation Tool v{__version__}")


@app.command()
def check():
    """Check environment configuration."""
    console.print("[bold blue]🔧 Environment Check[/]")

    issues = []

    # Check OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        console.print("[green]✅ OPENAI_API_KEY is set[/]")
    else:
        console.print("[red]❌ OPENAI_API_KEY not set[/]")
        issues.append("OPENAI_API_KEY")

    # Check dependencies
    try:
        import git

        console.print("[green]✅ GitPython is installed[/]")
    except ImportError:
        console.print("[red]❌ GitPython not installed[/]")
        issues.append("GitPython")

    try:
        import openai

        console.print("[green]✅ OpenAI library is installed[/]")
    except ImportError:
        console.print("[red]❌ OpenAI library not installed[/]")
        issues.append("OpenAI")

    try:
        import gitingest

        console.print("[green]✅ gitingest is installed[/]")
    except ImportError:
        console.print("[yellow]⚠️ gitingest not installed (using fallback)[/]")

    if issues:
        console.print(
            f"\n[red]Found {len(issues)} issue(s). Please install missing dependencies:[/]"
        )
        if "GitPython" in issues:
            console.print("  pip install gitpython")
        if "OpenAI" in issues:
            console.print("  pip install openai")
        if "OPENAI_API_KEY" in issues:
            console.print("  export OPENAI_API_KEY='your-api-key-here'")

        raise typer.Exit(code=1)
    else:
        console.print("\n[green]🎉 Environment is properly configured![/]")


def main():
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
