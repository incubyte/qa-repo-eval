# QA Repository Evaluation Tool

An AI-powered tool for evaluating QA practices in software repositories. Perfect for assessing automation test repositories, QA candidate submissions, and code quality analysis.

## 🎯 Overview

This tool provides comprehensive evaluation of QA repositories across four key categories:

- **Test Automation** (30%) - Framework usage, test organization, coverage
- **Technical Skills** (25%) - API/UI testing, design patterns, assertions
- **Quality Process** (25%) - Testing strategy, documentation, collaboration
- **CI Pipeline** (20%) - Automation integration, deployment practices

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd qa-repo-eval-tool

# Install dependencies
uv sync

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### Basic Usage

```bash
# Check environment setup
python main.py check

# Evaluate a single repository
python main.py evaluate "https://github.com/user/automation-repo"

# Batch evaluation from file
echo "https://github.com/user/repo1" > repos.txt
echo "https://github.com/user/repo2" >> repos.txt
python main.py batch repos.txt
```

> **Alternative**: You can also use `python -m src.qa_repo_eval_tool.cli <command>` if you prefer the module syntax.

## 📊 Features

### ✅ **Single Repository Evaluation**

- Comprehensive QA assessment with detailed scoring
- Visual progress tracking and rich console output
- Strengths and improvement recommendations
- Pass/Conditional Pass/Fail verdicts

### ✅ **Batch Processing**

- Evaluate multiple repositories from input file
- Generate JSON, CSV, and summary reports
- Batch analytics and success rates
- Continue-on-error for resilient processing

### ✅ **Professional Reports**

- **JSON** - Complete structured data for analysis
- **CSV** - Spreadsheet-compatible format
- **Summary** - Human-readable statistics and insights

### ✅ **AI-Powered Analysis**

- Framework detection (Selenium, Cypress, pytest, etc.)
- BDD implementation assessment (Cucumber, Gherkin)
- Page Object Model evaluation
- CI/CD pipeline analysis

## 🛠️ Use Cases

### **QA Candidate Assessment**

Perfect for evaluating automation test submissions like:

- Selenium WebDriver projects
- Cypress E2E tests
- API automation suites
- BDD/Cucumber implementations

### **Code Quality Review**

- Repository health checks
- Best practices compliance
- Framework usage assessment
- Test coverage analysis

### **Team Evaluation**

- Batch assessment of team repositories
- Standardization compliance
- Training needs identification

## 📋 CLI Commands

### Environment Check

```bash
python main.py check
```

Validates API key and dependencies.

### Single Evaluation

```bash
python main.py evaluate "https://github.com/user/repo" [OPTIONS]

Options:
  --shallow/--full     Use shallow clone (faster) [default: shallow]
  --keep-clone         Keep cloned repository for inspection
  --verbose/--quiet    Progress detail level [default: verbose]
```

### Batch Evaluation

```bash
python main.py batch INPUT_FILE [OPTIONS]

Options:
  --output-dir PATH    Output directory [default: qa_reports]
  --shallow/--full     Clone type for all repositories
  --continue/--stop    Continue if a repository fails [default: continue]
  --verbose/--quiet    Progress detail level
```

### Version Info

```bash
python main.py version
```

## 📈 Sample Output

```
📊 QA Evaluation Results: https://github.com/user/automation-repo

🎯 Overall QA Score: 78/100
📈 QA Level: Advanced
⚖️ Final Verdict: PASS
💻 Primary Language: java
🧪 Test Files: 15/28
🔧 Test Frameworks: selenium, cucumber, testng

📊 Category Scores:
Test Automation     ████████░░ 8.2/10
CI Pipeline         ██████░░░░ 6.0/10
Quality Process     ███████░░░ 7.5/10
Technical Skills    ████████░░ 8.0/10

✅ Strengths:
  • Excellent BDD implementation with Cucumber
  • Strong Page Object Model structure
  • Good test coverage for core flows

⚠️ Areas for Improvement:
  • Missing CI/CD pipeline configuration
  • Limited error handling in tests
  • Could improve test data management
```

## 🏗️ Architecture

```
src/qa_repo_eval_tool/
├── cli.py              # Command-line interface
├── metrics.py          # Core evaluation orchestration
├── qa_analysis.py      # AI-powered analysis engine
├── reporter.py         # Report generation (JSON/CSV/text)
├── git_utils.py        # Repository operations
├── types.py            # Data models and metrics
├── metrics_calculator.py # Scoring and verdict logic
└── utils/
    └── prompts.py      # AI evaluation prompts
```

## 🔧 Configuration

### Required Environment Variables

```bash
OPENAI_API_KEY=your-openai-api-key
```

### Input File Format

```text
# QA repositories for evaluation
https://github.com/user/selenium-tests
https://github.com/user/api-automation
https://github.com/user/cypress-e2e

# Comments start with #
# Empty lines are ignored
```

## 🎯 Evaluation Criteria

### Test Automation (30%)

- Test coverage and organization
- Framework usage quality
- Assertion patterns
- Test data management

### Technical Skills (25%)

- Test design patterns (Page Object, Builder, etc.)
- API testing implementation
- UI testing practices
- Performance and security considerations

### Quality Process (25%)

- Testing strategy evidence
- Documentation quality
- Collaboration indicators
- Process maturity

### CI Pipeline (20%)

- Pipeline configuration
- Test integration
- Deployment automation
- Environment management

## 📊 Scoring System

- **Expert (85-100)**: Advanced QA practices, production-ready
- **Advanced (70-84)**: Strong QA skills, minor improvements needed
- **Intermediate (50-69)**: Good foundation, development areas identified
- **Beginner (0-49)**: Basic skills, significant improvement needed

### Verdicts

- **PASS** (≥70): Ready for QA roles
- **CONDITIONAL_PASS** (50-69): Potential with development
- **FAIL** (<50): Needs significant improvement

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request
