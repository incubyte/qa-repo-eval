import tempfile
import shutil
import re
import requests
from pathlib import Path
from typing import Tuple, Optional, Set, List
from urllib.parse import urlparse

from git import Repo, GitCommandError

# QA-specific file patterns
TEST_FILE_REGEX = re.compile(r"test|spec|__tests__|\.test\.|\.spec\.", re.IGNORECASE)
CI_FILE_PATTERNS = [
    ".github/workflows",
    ".gitlab-ci.yml",
    "Jenkinsfile",
    ".circleci",
    ".travis.yml",
    "azure-pipelines.yml",
    "buildspec.yml",
]

# QA tool configuration patterns
QA_CONFIG_PATTERNS = [
    "pytest.ini",
    "tox.ini",
    "cypress.json",
    "cypress.config.js",
    "selenium",
    "playwright.config",
    "jest.config",
    "karma.conf",
    "protractor.conf",
    "codecept.conf",
    "nightwatch.conf",
    "wdio.conf",
]

# Language detection patterns for QA context
LANGUAGE_PATTERNS = {
    "python": [".py"],
    "java": [".java"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "csharp": [".cs"],
    "ruby": [".rb"],
    "php": [".php"],
    "go": [".go"],
}

# Test framework patterns
TEST_FRAMEWORK_PATTERNS = {
    "python": ["pytest", "unittest", "nose", "testify", "behave", "lettuce"],
    "java": ["junit", "testng", "cucumber", "spock", "mockito"],
    "javascript": ["jest", "mocha", "jasmine", "cypress", "playwright", "webdriver"],
    "typescript": ["jest", "mocha", "jasmine", "cypress", "playwright"],
    "csharp": ["nunit", "xunit", "mstest", "specflow"],
    "ruby": ["rspec", "minitest", "cucumber"],
    "php": ["phpunit", "behat", "codeception"],
    "go": ["testing", "ginkgo", "testify"],
}


def validate_repo_url(url: str, github_token: Optional[str] = None) -> Tuple[bool, str]:
    """Validate if a repository URL is accessible and valid."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
    except Exception:
        return False, "Invalid URL format"

    if "github.com" in url:
        if url.endswith(".git"):
            url = url[:-4]
        api_url = url.replace("github.com", "api.github.com/repos")

        headers = {}
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 404:
                return False, "Repository not found (404)"
            elif response.status_code == 403:
                if github_token:
                    return (
                        False,
                        "Access forbidden - check token permissions or rate limit",
                    )
                else:
                    # Without token, 403 could mean private repo or rate limit
                    return True, ""
            elif response.status_code == 401:
                return False, "Unauthorized - invalid or expired token"
            elif response.status_code != 200:
                return (
                    False,
                    f"Repository check failed with status code {response.status_code}",
                )
        except requests.RequestException as e:
            # If API fails, try cloning anyway
            return True, ""

    return True, ""


def clone_repo(
    url: str, shallow: bool = True, depth: int = 50, github_token: Optional[str] = None
) -> Tuple[Repo, Path]:
    """Clone the repo to a temp directory and return (Repo, path).
    The caller is responsible for deleting the directory (use `cleanup_clone`)."""
    is_valid, error = validate_repo_url(url, github_token)
    if not is_valid:
        raise ValueError(f"Repository validation failed: {error}")

    tmp_dir = Path(tempfile.mkdtemp(prefix="qa_repo_eval_")).resolve()
    try:
        # For private repos with token, include token in clone URL
        clone_url = url
        if github_token and "github.com" in url:
            clone_url = url.replace("https://", f"https://{github_token}@")

        if shallow:
            repo = Repo.clone_from(clone_url, tmp_dir, depth=depth)
        else:
            repo = Repo.clone_from(clone_url, tmp_dir)
    except GitCommandError as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise e
    return repo, tmp_dir


def cleanup_clone(path: Path) -> None:
    """Clean up cloned repository directory."""
    shutil.rmtree(path, ignore_errors=True)


def get_commit_count(repo: Repo) -> int:
    """Get total commit count in the repository."""
    return int(repo.git.rev_list("--count", "HEAD"))


def detect_readme(repo_path: Path) -> Path | None:
    """Find README file in the repository."""
    for filename in ["README.md", "README.rst", "README.txt", "README"]:
        path = repo_path / filename
        if path.exists():
            return path
    # Search case-insensitive fallback
    for path in repo_path.iterdir():
        if path.is_file() and path.name.lower().startswith("readme"):
            return path
    return None


def detect_test_files(repo_path: Path) -> List[Path]:
    """Detect test files in the repository."""
    test_files = []
    for file_path in repo_path.rglob("*"):
        if file_path.is_file() and TEST_FILE_REGEX.search(file_path.name):
            test_files.append(file_path)
    return test_files


def detect_ci_files(repo_path: Path) -> List[Path]:
    """Detect CI/CD configuration files."""
    ci_files = []
    for pattern in CI_FILE_PATTERNS:
        if "/" in pattern:
            # Directory pattern
            ci_dir = repo_path / pattern
            if ci_dir.exists() and ci_dir.is_dir():
                ci_files.extend([f for f in ci_dir.rglob("*") if f.is_file()])
        else:
            # File pattern
            ci_file = repo_path / pattern
            if ci_file.exists():
                ci_files.append(ci_file)
    return ci_files


def detect_qa_config_files(repo_path: Path) -> List[Path]:
    """Detect QA tool configuration files."""
    qa_configs = []
    for pattern in QA_CONFIG_PATTERNS:
        # Search for files containing the pattern
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and pattern.lower() in file_path.name.lower():
                qa_configs.append(file_path)
    return qa_configs


def detect_primary_language(repo_path: Path) -> str:
    """Detect the primary programming language of the repository."""
    language_counts = {}

    for language, extensions in LANGUAGE_PATTERNS.items():
        count = 0
        for ext in extensions:
            count += len(list(repo_path.rglob(f"*{ext}")))
        if count > 0:
            language_counts[language] = count

    if not language_counts:
        return "unknown"

    return max(language_counts, key=language_counts.get)


def detect_test_frameworks(repo_path: Path, language: str) -> Set[str]:
    """Detect test frameworks used in the repository."""
    frameworks = set()

    if language not in TEST_FRAMEWORK_PATTERNS:
        return frameworks

    # Read key files to detect frameworks
    key_files = [
        "requirements.txt",
        "package.json",
        "pom.xml",
        "build.gradle",
        "Gemfile",
        "composer.json",
        "go.mod",
        "*.csproj",
    ]

    content_to_search = ""
    for pattern in key_files:
        for file_path in repo_path.rglob(pattern):
            if file_path.is_file():
                try:
                    content_to_search += file_path.read_text(
                        encoding="utf-8", errors="ignore"
                    ).lower()
                except:
                    continue

    # Also search in test files
    test_files = detect_test_files(repo_path)
    for test_file in test_files[:10]:  # Limit to first 10 test files
        try:
            content_to_search += test_file.read_text(
                encoding="utf-8", errors="ignore"
            ).lower()
        except:
            continue

    # Check for framework patterns
    for framework in TEST_FRAMEWORK_PATTERNS[language]:
        if framework.lower() in content_to_search:
            frameworks.add(framework)

    return frameworks


def get_repository_structure(repo_path: Path) -> dict:
    """Get a comprehensive structure analysis of the repository."""
    return {
        "primary_language": detect_primary_language(repo_path),
        "test_files": detect_test_files(repo_path),
        "ci_files": detect_ci_files(repo_path),
        "qa_config_files": detect_qa_config_files(repo_path),
        "readme_file": detect_readme(repo_path),
        "test_frameworks": detect_test_frameworks(
            repo_path, detect_primary_language(repo_path)
        ),
        "total_files": len([f for f in repo_path.rglob("*") if f.is_file()]),
        "directories": [d for d in repo_path.rglob("*") if d.is_dir()],
    }
