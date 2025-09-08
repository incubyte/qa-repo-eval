"""
AI-powered QA repository analysis module.

This module provides functions to analyze QA repositories using AI models
and generate comprehensive QA metrics and assessments.
"""

import json
import os
from pathlib import Path
from typing import List

from git import Repo

from .git_utils import (
    get_commit_count,
    get_repository_structure,
    detect_test_files,
    detect_qa_config_files,
)
from .types import (
    QAMetrics,
    TestAutomationMetrics,
    TechnicalSkillsMetrics,
)
from .utils.prompts import (
    get_test_automation_prompt,
    get_technical_skills_prompt,
)
from .metrics_calculator import (
    calculate_overall_qa_score,
    determine_qa_level,
    determine_verdict,
    identify_strengths_and_improvements,
)


def get_ai_client():
    """Get configured AI client (Azure OpenAI)."""
    try:
        from openai import AzureOpenAI

        return AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://campus-recruitment.openai.azure.com/",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    except ImportError:
        raise ImportError(
            "OpenAI library not installed. Please install with: pip install openai"
        )


def call_ai_api(prompt: str, content: str, max_tokens: int = 2000) -> str:
    """
    Make AI API call with error handling.

    Args:
        prompt: System prompt for the AI
        content: User content to analyze
        max_tokens: Maximum response tokens

    Returns:
        AI response as string

    Raises:
        Exception: If AI call fails
    """
    try:
        client = get_ai_client()
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            temperature=0.1,
            max_tokens=max_tokens,
            model="gpt-4o-mini-campus-2025",
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI API call failed: {e}")
        raise


def extract_repo_content(repo_path: Path, max_files: int = 50) -> str:
    """
    Extract relevant repository content for AI analysis.

    Args:
        repo_path: Path to repository
        max_files: Maximum number of files to include

    Returns:
        Formatted string with repository content
    """
    content_parts = []

    # Get repository structure overview
    try:
        from gitingest import ingest

        _, tree, content = ingest(str(repo_path))

        content_parts.append("REPOSITORY STRUCTURE:")
        content_parts.append(tree[:5000])  # Limit tree size

        content_parts.append("\nREPOSITORY CONTENT:")
        content_parts.append(content[:50000])  # Limit content size

        return "\n".join(content_parts)
    except ImportError:
        # Fallback: manual content extraction
        return ""


def extract_commit_history(repo: Repo, max_commits: int = 50) -> List[str]:
    """
    Extract commit history for analysis.

    Args:
        repo: Git repository object
        max_commits: Maximum number of commits to analyze

    Returns:
        List of commit message strings
    """
    try:
        commits = []
        for commit in repo.iter_commits(max_count=max_commits):
            commit_info = {
                "message": commit.message.strip(),
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "files_changed": len(commit.stats.files),
            }
            commits.append(commit_info)
        return commits
    except Exception as e:
        print(f"Error extracting commit history: {e}")
        return []


def analyze_test_automation(repo_path: Path) -> TestAutomationMetrics:
    """
    Analyze test automation practices using AI.

    Args:
        repo_path: Path to repository

    Returns:
        TestAutomationMetrics with scores
    """
    try:
        # Extract test-related content
        test_files = detect_test_files(repo_path)
        test_content_parts = []

        test_content_parts.append(f"Found {len(test_files)} test files:")
        for test_file in test_files[:20]:  # Limit to first 20 test files
            try:
                relative_path = test_file.relative_to(repo_path)
                test_content_parts.append(f"\n--- {relative_path} ---")
                content = test_file.read_text(encoding="utf-8", errors="ignore")
                # Limit file size for analysis
                if len(content) > 3000:
                    content = content[:3000] + "\n... (truncated)"
                test_content_parts.append(content)
            except Exception:
                continue

        # Get QA config files
        qa_configs = detect_qa_config_files(repo_path)
        test_content_parts.append(
            f"\n\nQA Configuration files found: {len(qa_configs)}"
        )
        for config_file in qa_configs:
            try:
                relative_path = config_file.relative_to(repo_path)
                test_content_parts.append(f"\n--- {relative_path} ---")
                content = config_file.read_text(encoding="utf-8", errors="ignore")
                if len(content) > 1000:
                    content = content[:1000] + "\n... (truncated)"
                test_content_parts.append(content)
            except Exception:
                continue

        content = "\n".join(test_content_parts)

        # Call AI for analysis
        prompt = get_test_automation_prompt()
        response = call_ai_api(prompt, content)

        # Parse JSON response
        result = json.loads(response)

        return TestAutomationMetrics(
            test_coverage_score=result.get("test_coverage_score", 0),
            test_organization_score=result.get("test_organization_score", 0),
            framework_usage_score=result.get("framework_usage_score", 0),
            assertion_quality_score=result.get("assertion_quality_score", 0),
            test_data_management_score=result.get("test_data_management_score", 0),
        )

    except Exception as e:
        print(f"Error in test automation analysis: {e}")
        return TestAutomationMetrics(0, 0, 0, 0, 0)


def analyze_technical_skills(repo_path: Path) -> TechnicalSkillsMetrics:
    """
    Analyze technical QA skills demonstrated in the repository.

    Args:
        repo_path: Path to repository

    Returns:
        TechnicalSkillsMetrics with scores
    """
    try:
        # Extract comprehensive repository content
        content = extract_repo_content(repo_path, max_files=40)

        # Call AI for analysis
        prompt = get_technical_skills_prompt()
        response = call_ai_api(prompt, content)

        # Parse JSON response
        result = json.loads(response)

        return TechnicalSkillsMetrics(
            test_design_patterns_score=result.get("test_design_patterns_score", 0),
            api_testing_score=result.get("api_testing_score", 0),
            ui_testing_score=result.get("ui_testing_score", 0),
        )

    except Exception as e:
        print(f"Error in technical skills analysis: {e}")
        return TechnicalSkillsMetrics(0, 0, 0)


def analyze_full_qa_repository(repo: Repo, repo_path: Path) -> QAMetrics:
    """
    Perform comprehensive QA analysis of a repository.

    Args:
        repo: Git repository object
        repo_path: Path to repository

    Returns:
        Complete QAMetrics object with all assessments
    """
    print("🔍 Starting comprehensive QA repository analysis...")

    # Get basic repository information
    repo_structure = get_repository_structure(repo_path)
    commit_count = get_commit_count(repo)

    print("📊 Analyzing test automation...")
    test_automation = analyze_test_automation(repo_path)

    print("💻 Analyzing technical skills...")
    technical_skills = analyze_technical_skills(repo_path)

    # Create comprehensive metrics
    metrics = QAMetrics(
        # Basic info
        commit_count=commit_count,
        primary_language=repo_structure["primary_language"],
        test_file_count=len(repo_structure["test_files"]),
        total_file_count=repo_structure["total_files"],
        test_frameworks=list(repo_structure["test_frameworks"]),
        # Detailed assessments
        test_automation=test_automation,
        technical_skills=technical_skills,
        # These will be calculated
        overall_qa_maturity_score=0,
        qa_level="",
        strengths=[],
        improvement_areas=[],
        final_verdict="",
        final_verdict_reason="",
    )

    print("🧮 Calculating overall assessment...")

    # Calculate overall scores and verdict
    overall_score = calculate_overall_qa_score(metrics)
    metrics.overall_qa_maturity_score = overall_score

    qa_level = determine_qa_level(overall_score)
    metrics.qa_level = qa_level

    verdict, reason = determine_verdict(metrics, overall_score)
    metrics.final_verdict = verdict
    metrics.final_verdict_reason = reason

    strengths, improvements = identify_strengths_and_improvements(metrics)
    metrics.strengths = strengths
    metrics.improvement_areas = improvements

    print("✅ QA repository analysis completed!")

    return metrics
