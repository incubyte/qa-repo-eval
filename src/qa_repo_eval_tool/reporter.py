"""
Simple and lean reporter for QA evaluation results.

Generates JSON/CSV reports and console output.
"""

import json
from pathlib import Path
from typing import List

from .types import QAResult


def write_json_report(results: List[QAResult], output_path: Path) -> None:
    """Write results to JSON file."""
    data = [result.to_dict() for result in results]

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_csv_report(results: List[QAResult], output_path: Path) -> None:
    """Write results to CSV file."""
    if not results:
        return

    # Simple CSV without pandas dependency
    lines = []

    # Header
    header = [
        "url",
        "overall_qa_maturity_score",
        "qa_level",
        "final_verdict",
        "primary_language",
        "test_file_count",
        "total_file_count",
        "commit_count",
        "test_frameworks",
        "error_message",
    ]
    lines.append(",".join(header))

    # Data rows
    for result in results:
        if result.is_successful:
            m = result.metrics
            row = [
                f'"{result.url}"',
                str(m.overall_qa_maturity_score),
                f'"{m.qa_level}"',
                f'"{m.final_verdict}"',
                f'"{m.primary_language}"',
                str(m.test_file_count),
                str(m.total_file_count),
                str(m.commit_count),
                f'"{";".join(m.test_frameworks)}"',
                '""',
            ]
        else:
            row = [
                f'"{result.url}"',
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                f'"{result.error_message or ""}"',
            ]
        lines.append(",".join(row))

    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_summary_report(results: List[QAResult], output_path: Path) -> None:
    """Write simple text summary."""
    from .metrics import get_evaluation_summary

    summary = get_evaluation_summary(results)

    lines = [
        "QA Repository Evaluation Summary",
        "=" * 40,
        "",
        f"Total repositories: {summary['total_repositories']}",
        f"Successful evaluations: {summary['successful_evaluations']}",
        f"Failed evaluations: {summary['failed_evaluations']}",
        f"Success rate: {summary['success_rate']:.1%}",
    ]

    if summary["successful_evaluations"] > 0:
        lines.append(f"Average QA score: {summary['average_score']:.1f}/100")

    if summary["score_distribution"]:
        lines.extend(["", "Score Distribution:"])
        for level, count in summary["score_distribution"].items():
            lines.append(f"  {level}: {count}")

    if summary["verdict_distribution"]:
        lines.extend(["", "Verdict Distribution:"])
        for verdict, count in summary["verdict_distribution"].items():
            lines.append(f"  {verdict}: {count}")

    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_reports(results: List[QAResult], output_dir: Path) -> List[Path]:
    """
    Write all reports to output directory.

    Args:
        results: List of QA evaluation results
        output_dir: Directory to write reports

    Returns:
        List of created file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    created_files = []

    # JSON report
    json_path = output_dir / "qa_results.json"
    write_json_report(results, json_path)
    created_files.append(json_path)

    # CSV report
    csv_path = output_dir / "qa_results.csv"
    write_csv_report(results, csv_path)
    created_files.append(csv_path)

    # Summary report
    summary_path = output_dir / "summary.txt"
    write_summary_report(results, summary_path)
    created_files.append(summary_path)

    return created_files
