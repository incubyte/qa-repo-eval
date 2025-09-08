"""
Utility functions for calculating QA metrics and determining verdicts.
"""

from typing import List, Dict
from .types import (
    QAMetrics,
    QAResult,
    QAReportSummary,
    QA_LEVEL_THRESHOLDS,
    VERDICT_THRESHOLDS,
    MINIMUM_REQUIREMENTS,
)


def calculate_overall_qa_score(metrics: QAMetrics) -> int:
    """Calculate the overall QA maturity score (0-100) based on category scores."""
    category_scores = metrics.get_category_scores()

    # Weighted scoring - some categories are more important
    weights = {
        "test_automation": 0.30,  # 30% - Most important
        "technical_skills": 0.25,  # 25% - Very important
        "quality_process": 0.25,  # 25% - Important
        "ci_pipeline": 0.20,  # 20% - Important but not always applicable
    }

    weighted_score = sum(
        category_scores[category] * weight for category, weight in weights.items()
    )

    # Convert from 0-10 scale to 0-100 scale
    return int(weighted_score * 10)


def determine_qa_level(overall_score: int) -> str:
    """Determine QA level based on overall score."""
    for level, threshold in sorted(
        QA_LEVEL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True
    ):
        if overall_score >= threshold:
            return level
    return "Beginner"


def determine_verdict(metrics: QAMetrics, overall_score: int) -> tuple[str, str]:
    """Determine final verdict and reason based on metrics and score."""
    reasons = []

    # Check minimum requirements
    if overall_score >= VERDICT_THRESHOLDS["PASS"]:
        requirements = MINIMUM_REQUIREMENTS["PASS"]
        verdict = "PASS"
    elif overall_score >= VERDICT_THRESHOLDS["CONDITIONAL_PASS"]:
        requirements = MINIMUM_REQUIREMENTS["CONDITIONAL_PASS"]
        verdict = "CONDITIONAL_PASS"
    else:
        verdict = "FAIL"
        reasons.append(f"Overall QA score ({overall_score}) is below minimum threshold")

    if verdict != "FAIL":
        # Check specific requirements
        if metrics.test_file_count < requirements["min_test_files"]:
            reasons.append(
                f"Insufficient test files ({metrics.test_file_count} < {requirements['min_test_files']})"
            )
            if verdict == "PASS":
                verdict = "CONDITIONAL_PASS"

        if metrics.commit_count < requirements["min_commit_count"]:
            reasons.append(
                f"Insufficient commit history ({metrics.commit_count} < {requirements['min_commit_count']})"
            )
            if verdict == "PASS":
                verdict = "CONDITIONAL_PASS"

        # Check category requirements
        category_scores = metrics.get_category_scores()
        for required_category in requirements["required_categories"]:
            if category_scores[required_category] < requirements["min_category_score"]:
                reasons.append(
                    f"Low {required_category} score ({category_scores[required_category]:.1f})"
                )
                if verdict == "PASS":
                    verdict = "CONDITIONAL_PASS"

    # Build reason string
    if not reasons:
        if verdict == "PASS":
            reason = f"Strong QA skills demonstrated across all areas (Score: {overall_score})"
        elif verdict == "CONDITIONAL_PASS":
            reason = (
                f"Good QA foundation with room for improvement (Score: {overall_score})"
            )
    else:
        reason = "; ".join(reasons)
        if verdict == "CONDITIONAL_PASS":
            reason += f" (Score: {overall_score})"

    if verdict == "FAIL" and not reasons:
        reason = f"QA skills need significant development (Score: {overall_score})"

    return verdict, reason


def identify_strengths_and_improvements(
    metrics: QAMetrics,
) -> tuple[List[str], List[str]]:
    """Identify strengths and areas for improvement based on category scores."""
    category_scores = metrics.get_category_scores()
    strengths = []
    improvements = []

    # Define strength and improvement thresholds
    STRENGTH_THRESHOLD = 7.5
    IMPROVEMENT_THRESHOLD = 5.0

    for category, score in category_scores.items():
        category_name = category.replace("_", " ").title()

        if score >= STRENGTH_THRESHOLD:
            strengths.append(category_name)
        elif score < IMPROVEMENT_THRESHOLD:
            improvements.append(category_name)

    # Add specific insights based on individual metrics
    if metrics.test_file_count == 0:
        improvements.append("Test Coverage - No test files found")
    elif metrics.test_file_count / metrics.total_file_count > 0.3:
        strengths.append("High Test Coverage Ratio")

    if len(metrics.test_frameworks) >= 2:
        strengths.append("Multiple Testing Frameworks")
    elif len(metrics.test_frameworks) == 0:
        improvements.append("Testing Framework Usage")

    if metrics.commit_count < 5:
        improvements.append("Version Control Practices")
    elif metrics.commit_count > 50:
        strengths.append("Active Development History")

    return strengths, improvements


def generate_report_summary(results: List[QAResult]) -> QAReportSummary:
    """Generate summary statistics from a list of QA evaluation results."""
    successful_results = [r for r in results if r.is_successful]

    if not successful_results:
        return QAReportSummary(
            total_repositories=len(results),
            successful_evaluations=0,
            failed_evaluations=len(results),
            average_qa_maturity_score=0.0,
            qa_level_distribution={},
            verdict_distribution={},
            common_strengths=[],
            common_improvement_areas=[],
            top_frameworks=[],
        )

    # Calculate distributions
    qa_levels = [r.metrics.qa_level for r in successful_results]
    verdicts = [r.metrics.final_verdict for r in successful_results]
    all_strengths = [
        strength for r in successful_results for strength in r.metrics.strengths
    ]
    all_improvements = [
        improvement
        for r in successful_results
        for improvement in r.metrics.improvement_areas
    ]
    all_frameworks = [
        framework for r in successful_results for framework in r.metrics.test_frameworks
    ]

    # Count occurrences
    qa_level_counts = {level: qa_levels.count(level) for level in set(qa_levels)}
    verdict_counts = {verdict: verdicts.count(verdict) for verdict in set(verdicts)}

    # Get most common items
    def get_most_common(items: List[str], limit: int = 5) -> List[str]:
        if not items:
            return []
        counts = {item: items.count(item) for item in set(items)}
        return sorted(counts.keys(), key=lambda x: counts[x], reverse=True)[:limit]

    return QAReportSummary(
        total_repositories=len(results),
        successful_evaluations=len(successful_results),
        failed_evaluations=len(results) - len(successful_results),
        average_qa_maturity_score=sum(
            r.metrics.overall_qa_maturity_score for r in successful_results
        )
        / len(successful_results),
        qa_level_distribution=qa_level_counts,
        verdict_distribution=verdict_counts,
        common_strengths=get_most_common(all_strengths),
        common_improvement_areas=get_most_common(all_improvements),
        top_frameworks=get_most_common(all_frameworks),
    )


def create_default_metrics() -> QAMetrics:
    """Create a QAMetrics object with default values for testing purposes."""
    from .types import (
        TestAutomationMetrics,
        TechnicalSkillsMetrics,
    )

    # Default to low scores - actual evaluation will override these
    return QAMetrics(
        commit_count=0,
        primary_language="unknown",
        test_file_count=0,
        total_file_count=0,
        test_frameworks=[],
        test_automation=TestAutomationMetrics(0, 0, 0, 0, 0),
        technical_skills=TechnicalSkillsMetrics(0, 0, 0),
        overall_qa_maturity_score=0,
        qa_level="Beginner",
        strengths=[],
        improvement_areas=[],
        final_verdict="FAIL",
        final_verdict_reason="Not evaluated",
    )
