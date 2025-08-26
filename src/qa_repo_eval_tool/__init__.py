__version__ = "0.1.0"

# Re-export common API for programmatic use
from .git_utils import (
    cleanup_clone,
    clone_repo,
    detect_ci_files,
    detect_primary_language,
    detect_qa_config_files,
    detect_readme,
    detect_test_files,
    detect_test_frameworks,
    get_commit_count,
    get_repository_structure,
)
from .metrics import (
    batch_compute_qa_metrics,
    compute_qa_metrics,
    get_evaluation_summary,
)

from .cli import main as cli_main
from .reporter import write_reports
from .qa_analysis import (
    analyze_ci_pipeline,
    analyze_full_qa_repository,
    analyze_quality_process,
    analyze_technical_skills,
    analyze_test_automation,
)
from .types import (
    MINIMUM_REQUIREMENTS,
    QA_LEVEL_THRESHOLDS,
    VERDICT_THRESHOLDS,
    CIPipelineMetrics,
    QAMetrics,
    QAReportSummary,
    QAResult,
    QualityProcessMetrics,
    TechnicalSkillsMetrics,
    TestAutomationMetrics,
)
from .utils.prompts import (
    get_ci_pipeline_prompt,
    get_commit_analysis_prompt,
    get_overall_qa_assessment_prompt,
    get_quality_process_prompt,
    get_technical_skills_prompt,
    get_test_automation_prompt,
)


__all__ = [
    "cleanup_clone",
    "clone_repo",
    "detect_ci_files",
    "detect_primary_language",
    "detect_qa_config_files",
    "detect_readme",
    "detect_test_files",
    "detect_test_frameworks",
    "get_commit_count",
    "get_repository_structure",
    "batch_compute_qa_metrics",
    "compute_qa_metrics",
    "get_evaluation_summary",
    "cli_main",
    "write_reports",
    "analyze_ci_pipeline",
    "analyze_full_qa_repository",
    "analyze_quality_process",
    "analyze_technical_skills",
    "analyze_test_automation",
    "MINIMUM_REQUIREMENTS",
    "QA_LEVEL_THRESHOLDS",
    "VERDICT_THRESHOLDS",
    "CIPipelineMetrics",
    "QAMetrics",
    "QAReportSummary",
    "QAResult",
    "QualityProcessMetrics",
    "TechnicalSkillsMetrics",
    "TestAutomationMetrics",
    "get_ci_pipeline_prompt",
    "get_commit_analysis_prompt",
    "get_overall_qa_assessment_prompt",
    "get_quality_process_prompt",
    "get_technical_skills_prompt",
    "get_test_automation_prompt",
]
