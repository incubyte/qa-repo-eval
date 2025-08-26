"""
QA Metrics Orchestration Engine

This module provides the main orchestration functions for QA repository evaluation.
It coordinates repository cloning, AI analysis, metrics calculation, and cleanup.
"""

from typing import Optional

from .git_utils import clone_repo, cleanup_clone
from .qa_analysis import analyze_full_qa_repository
from .types import QAMetrics, QAResult


def compute_qa_metrics(
    repo_url: str,
    shallow: bool = True,
    keep_clone: bool = False,
    github_token: Optional[str] = None,
    verbose: bool = True,
) -> QAMetrics:
    """
    Compute comprehensive QA metrics for a repository.

    This is the main orchestration function that coordinates the entire
    QA evaluation process from repository cloning to final assessment.

    Args:
        repo_url: URL of the repository to analyze
        shallow: Whether to perform shallow clone (faster, default: True)
        keep_clone: Whether to keep cloned repository on disk (default: False)
        github_token: GitHub token for private repositories (optional)
        verbose: Whether to print progress messages (default: True)

    Returns:
        QAMetrics: Complete QA assessment results

    Raises:
        ValueError: If repository URL is invalid
        Exception: If analysis fails

    Example:
        >>> metrics = compute_qa_metrics("https://github.com/user/repo")
        >>> print(f"QA Score: {metrics.overall_qa_maturity_score}/100")
        >>> print(f"Verdict: {metrics.final_verdict}")
    """
    if verbose:
        print(f"🚀 Starting QA evaluation for: {repo_url}")
        print("=" * 80)

    repo_path = None
    repo = None

    try:
        # Step 1: Clone repository
        if verbose:
            print("📥 Step 1: Cloning repository...")

        repo, repo_path = clone_repo(
            repo_url, shallow=shallow, github_token=github_token
        )

        if verbose:
            print(f"   ✅ Repository cloned to: {repo_path}")

        # Step 2: Perform comprehensive AI analysis
        if verbose:
            print("\n🤖 Step 2: Performing AI-powered QA analysis...")

        metrics = analyze_full_qa_repository(repo, repo_path)

        if verbose:
            print("   ✅ QA analysis completed successfully")
            print("\n📊 Results Summary:")
            print(f"   • Overall QA Score: {metrics.overall_qa_maturity_score}/100")
            print(f"   • QA Level: {metrics.qa_level}")
            print(f"   • Final Verdict: {metrics.final_verdict}")
            print(f"   • Test Files: {metrics.test_file_count}")
            print(f"   • Primary Language: {metrics.primary_language}")

            if metrics.test_frameworks:
                print(f"   • Frameworks: {', '.join(metrics.test_frameworks)}")

        return metrics

    except Exception as e:
        if verbose:
            print(f"❌ Error during QA evaluation: {e}")
        raise

    finally:
        # Step 3: Cleanup (unless explicitly keeping clone)
        if repo_path and not keep_clone:
            if verbose:
                print("\n🧹 Step 3: Cleaning up...")
            cleanup_clone(repo_path)
            if verbose:
                print("   ✅ Temporary files cleaned up")
        elif repo_path and keep_clone:
            if verbose:
                print(f"\n📁 Repository kept at: {repo_path}")


def batch_compute_qa_metrics(
    repo_urls: list[str],
    shallow: bool = True,
    keep_clone: bool = False,
    github_token: Optional[str] = None,
    verbose: bool = True,
    continue_on_error: bool = True,
) -> list[QAResult]:
    """
    Compute QA metrics for multiple repositories.

    Args:
        repo_urls: List of repository URLs to analyze
        shallow: Whether to perform shallow clones (default: True)
        keep_clone: Whether to keep cloned repositories (default: False)
        github_token: GitHub token for private repositories (optional)
        verbose: Whether to print progress messages (default: True)
        continue_on_error: Whether to continue if one repository fails (default: True)

    Returns:
        List[QAResult]: Results for all repositories

    Example:
        >>> urls = ["https://github.com/user/repo1", "https://github.com/user/repo2"]
        >>> results = batch_compute_qa_metrics(urls)
        >>> successful = [r for r in results if r.is_successful]
        >>> print(f"Successfully analyzed {len(successful)}/{len(results)} repositories")
    """
    results = []

    if verbose:
        print(f"🔄 Starting batch QA evaluation for {len(repo_urls)} repositories")
        print("=" * 80)

    for i, repo_url in enumerate(repo_urls, 1):
        if verbose:
            print(f"\n📋 Processing repository {i}/{len(repo_urls)}: {repo_url}")
            print("-" * 60)

        try:
            if continue_on_error:
                try:
                    metrics = compute_qa_metrics(
                        repo_url=repo_url,
                        shallow=shallow,
                        keep_clone=keep_clone,
                        github_token=github_token,
                        verbose=verbose,
                    )
                    result = QAResult(url=repo_url, metrics=metrics)
                except Exception as e:
                    if verbose:
                        print(f"❌ QA evaluation failed for {repo_url}: {e}")
                    result = QAResult(url=repo_url, metrics=None, error_message=str(e))
                results.append(result)
            else:
                metrics = compute_qa_metrics(
                    repo_url=repo_url,
                    shallow=shallow,
                    keep_clone=keep_clone,
                    github_token=github_token,
                    verbose=verbose,
                )
                results.append(QAResult(url=repo_url, metrics=metrics))

        except Exception as e:
            if verbose:
                print(f"❌ Failed to process {repo_url}: {e}")

            if not continue_on_error:
                raise

            results.append(QAResult(url=repo_url, metrics=None, error_message=str(e)))

    if verbose:
        successful_count = len([r for r in results if r.is_successful])
        print("\n✅ Batch evaluation completed!")
        print(f"   • Total repositories: {len(results)}")
        print(f"   • Successful evaluations: {successful_count}")
        print(f"   • Failed evaluations: {len(results) - successful_count}")
        print("=" * 80)

    return results


def get_evaluation_summary(results: list[QAResult]) -> dict:
    """
    Generate summary statistics from QA evaluation results.

    Args:
        results: List of QAResult objects

    Returns:
        Dictionary with summary statistics

    Example:
        >>> summary = get_evaluation_summary(results)
        >>> print(f"Average score: {summary['average_score']:.1f}")
        >>> print(f"Success rate: {summary['success_rate']:.1%}")
    """
    if not results:
        return {
            "total_repositories": 0,
            "successful_evaluations": 0,
            "failed_evaluations": 0,
            "success_rate": 0.0,
            "average_score": 0.0,
            "score_distribution": {},
            "verdict_distribution": {},
        }

    successful_results = [r for r in results if r.is_successful]

    # Basic statistics
    total_repos = len(results)
    successful_count = len(successful_results)
    failed_count = total_repos - successful_count
    success_rate = successful_count / total_repos if total_repos > 0 else 0.0

    # Score statistics
    if successful_results:
        scores = [r.metrics.overall_qa_maturity_score for r in successful_results]
        average_score = sum(scores) / len(scores)

        # Score distribution
        score_ranges = {
            "Expert (85-100)": len([s for s in scores if s >= 85]),
            "Advanced (70-84)": len([s for s in scores if 70 <= s < 85]),
            "Intermediate (50-69)": len([s for s in scores if 50 <= s < 70]),
            "Beginner (0-49)": len([s for s in scores if s < 50]),
        }

        # Verdict distribution
        verdicts = [r.metrics.final_verdict for r in successful_results]
        verdict_counts = {}
        for verdict in set(verdicts):
            verdict_counts[verdict] = verdicts.count(verdict)
    else:
        average_score = 0.0
        score_ranges = {}
        verdict_counts = {}

    return {
        "total_repositories": total_repos,
        "successful_evaluations": successful_count,
        "failed_evaluations": failed_count,
        "success_rate": success_rate,
        "average_score": average_score,
        "score_distribution": score_ranges,
        "verdict_distribution": verdict_counts,
    }
