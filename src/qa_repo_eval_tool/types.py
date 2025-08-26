from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class TestAutomationMetrics:
    """Metrics for test automation assessment."""

    test_coverage_score: int  # 0-10: How well tests cover functionality
    test_organization_score: int  # 0-10: Test structure and organization
    framework_usage_score: int  # 0-10: Proper use of testing frameworks
    assertion_quality_score: int  # 0-10: Quality of test assertions
    test_data_management_score: int  # 0-10: How test data is managed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_coverage_score": self.test_coverage_score,
            "test_organization_score": self.test_organization_score,
            "framework_usage_score": self.framework_usage_score,
            "assertion_quality_score": self.assertion_quality_score,
            "test_data_management_score": self.test_data_management_score,
        }


@dataclass
class CIPipelineMetrics:
    """Metrics for CI/CD pipeline assessment."""

    pipeline_configuration_score: int  # 0-10: Quality of CI/CD setup
    automated_testing_integration_score: int  # 0-10: Tests integrated in pipeline
    deployment_automation_score: int  # 0-10: Automated deployment practices
    pipeline_efficiency_score: int  # 0-10: Pipeline speed and reliability
    environment_management_score: int  # 0-10: Environment setup and management

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_configuration_score": self.pipeline_configuration_score,
            "automated_testing_integration_score": self.automated_testing_integration_score,
            "deployment_automation_score": self.deployment_automation_score,
            "pipeline_efficiency_score": self.pipeline_efficiency_score,
            "environment_management_score": self.environment_management_score,
        }


@dataclass
class QualityProcessMetrics:
    """Metrics for overall QA process assessment."""

    testing_strategy_score: int  # 0-10: Evidence of testing strategy
    bug_tracking_score: int  # 0-10: Bug reporting and tracking practices
    code_review_process_score: int  # 0-10: Code review quality
    documentation_quality_score: int  # 0-10: QA documentation quality
    collaboration_score: int  # 0-10: Team collaboration evidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "testing_strategy_score": self.testing_strategy_score,
            "bug_tracking_score": self.bug_tracking_score,
            "code_review_process_score": self.code_review_process_score,
            "documentation_quality_score": self.documentation_quality_score,
            "collaboration_score": self.collaboration_score,
        }


@dataclass
class TechnicalSkillsMetrics:
    """Metrics for technical QA skills assessment."""

    test_design_patterns_score: int  # 0-10: Use of test design patterns
    api_testing_score: int  # 0-10: API testing capabilities
    ui_testing_score: int  # 0-10: UI testing implementation
    performance_testing_score: int  # 0-10: Performance testing evidence
    security_testing_score: int  # 0-10: Security testing practices

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_design_patterns_score": self.test_design_patterns_score,
            "api_testing_score": self.api_testing_score,
            "ui_testing_score": self.ui_testing_score,
            "performance_testing_score": self.performance_testing_score,
            "security_testing_score": self.security_testing_score,
        }


@dataclass
class RepositoryStructureMetrics:
    """Metrics for repository structure and organization."""

    project_structure_score: int  # 0-10: Overall project organization
    test_structure_score: int  # 0-10: Test file organization
    configuration_management_score: int  # 0-10: Config file management
    dependency_management_score: int  # 0-10: Dependency handling
    version_control_practices_score: int  # 0-10: Git practices and commit quality

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_structure_score": self.project_structure_score,
            "test_structure_score": self.test_structure_score,
            "configuration_management_score": self.configuration_management_score,
            "dependency_management_score": self.dependency_management_score,
            "version_control_practices_score": self.version_control_practices_score,
        }


@dataclass
class QAMetrics:
    """Comprehensive QA assessment metrics."""

    # Basic repository info
    commit_count: int
    primary_language: str
    test_file_count: int
    total_file_count: int
    test_frameworks: List[str]

    # Detailed metric categories
    test_automation: TestAutomationMetrics
    ci_pipeline: CIPipelineMetrics
    quality_process: QualityProcessMetrics
    technical_skills: TechnicalSkillsMetrics
    repository_structure: RepositoryStructureMetrics

    # Overall assessment
    overall_qa_maturity_score: int  # 0-100: Calculated overall score
    qa_level: str  # "Beginner", "Intermediate", "Advanced", "Expert"
    strengths: List[str]  # Areas where the candidate excels
    improvement_areas: List[str]  # Areas needing improvement
    final_verdict: str  # "PASS", "CONDITIONAL_PASS", "FAIL"
    final_verdict_reason: str  # Detailed explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            # Basic info
            "commit_count": self.commit_count,
            "primary_language": self.primary_language,
            "test_file_count": self.test_file_count,
            "total_file_count": self.total_file_count,
            "test_frameworks": self.test_frameworks,
            # Detailed metrics
            "test_automation": self.test_automation.to_dict(),
            "ci_pipeline": self.ci_pipeline.to_dict(),
            "quality_process": self.quality_process.to_dict(),
            "technical_skills": self.technical_skills.to_dict(),
            "repository_structure": self.repository_structure.to_dict(),
            # Overall assessment
            "overall_qa_maturity_score": self.overall_qa_maturity_score,
            "qa_level": self.qa_level,
            "strengths": self.strengths,
            "improvement_areas": self.improvement_areas,
            "final_verdict": self.final_verdict,
            "final_verdict_reason": self.final_verdict_reason,
        }

    def get_category_scores(self) -> Dict[str, float]:
        """Get average scores for each major category."""
        return {
            "test_automation": sum(
                [
                    self.test_automation.test_coverage_score,
                    self.test_automation.test_organization_score,
                    self.test_automation.framework_usage_score,
                    self.test_automation.assertion_quality_score,
                    self.test_automation.test_data_management_score,
                ]
            )
            / 5.0,
            "ci_pipeline": sum(
                [
                    self.ci_pipeline.pipeline_configuration_score,
                    self.ci_pipeline.automated_testing_integration_score,
                    self.ci_pipeline.deployment_automation_score,
                    self.ci_pipeline.pipeline_efficiency_score,
                    self.ci_pipeline.environment_management_score,
                ]
            )
            / 5.0,
            "quality_process": sum(
                [
                    self.quality_process.testing_strategy_score,
                    self.quality_process.bug_tracking_score,
                    self.quality_process.code_review_process_score,
                    self.quality_process.documentation_quality_score,
                    self.quality_process.collaboration_score,
                ]
            )
            / 5.0,
            "technical_skills": sum(
                [
                    self.technical_skills.test_design_patterns_score,
                    self.technical_skills.api_testing_score,
                    self.technical_skills.ui_testing_score,
                    self.technical_skills.performance_testing_score,
                    self.technical_skills.security_testing_score,
                ]
            )
            / 5.0,
            "repository_structure": sum(
                [
                    self.repository_structure.project_structure_score,
                    self.repository_structure.test_structure_score,
                    self.repository_structure.configuration_management_score,
                    self.repository_structure.dependency_management_score,
                    self.repository_structure.version_control_practices_score,
                ]
            )
            / 5.0,
        }


@dataclass
class QAResult:
    """Container for QA evaluation result."""

    url: str
    metrics: Optional[QAMetrics]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        base_dict = {"url": self.url}

        if self.metrics:
            base_dict.update(self.metrics.to_dict())

        if self.error_message:
            base_dict["error_message"] = self.error_message

        return base_dict

    @property
    def is_successful(self) -> bool:
        """Check if the evaluation was successful."""
        return self.metrics is not None and self.error_message is None


@dataclass
class QAReportSummary:
    """Summary statistics for a batch of QA evaluations."""

    total_repositories: int
    successful_evaluations: int
    failed_evaluations: int
    average_qa_maturity_score: float
    qa_level_distribution: Dict[str, int]  # Count by QA level
    verdict_distribution: Dict[str, int]  # Count by verdict
    common_strengths: List[str]  # Most common strengths
    common_improvement_areas: List[str]  # Most common improvement areas
    top_frameworks: List[str]  # Most used frameworks

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_repositories": self.total_repositories,
            "successful_evaluations": self.successful_evaluations,
            "failed_evaluations": self.failed_evaluations,
            "success_rate": self.successful_evaluations / self.total_repositories
            if self.total_repositories > 0
            else 0,
            "average_qa_maturity_score": self.average_qa_maturity_score,
            "qa_level_distribution": self.qa_level_distribution,
            "verdict_distribution": self.verdict_distribution,
            "common_strengths": self.common_strengths,
            "common_improvement_areas": self.common_improvement_areas,
            "top_frameworks": self.top_frameworks,
        }


# QA Evaluation Thresholds and Constants
QA_LEVEL_THRESHOLDS = {
    "Expert": 85,  # 85-100
    "Advanced": 70,  # 70-84
    "Intermediate": 50,  # 50-69
    "Beginner": 0,  # 0-49
}

VERDICT_THRESHOLDS = {
    "PASS": 70,  # Score >= 70
    "CONDITIONAL_PASS": 50,  # Score >= 50 and < 70
    "FAIL": 0,  # Score < 50
}

# Minimum requirements for different verdict levels
MINIMUM_REQUIREMENTS = {
    "PASS": {
        "min_test_files": 5,
        "min_commit_count": 10,
        "required_categories": ["test_automation", "repository_structure"],
        "min_category_score": 6.0,
    },
    "CONDITIONAL_PASS": {
        "min_test_files": 3,
        "min_commit_count": 5,
        "required_categories": ["test_automation"],
        "min_category_score": 4.0,
    },
}
