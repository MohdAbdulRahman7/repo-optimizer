# Git Repo Health Checker

A terminal-based tool that analyzes local git repositories and provides a health score based on repository structure and git history. Works completely offline with no network access required.

## Features

- **Repository Structure Analysis**
  - Checks for README.md
  - Checks for LICENSE file (case-insensitive)
  - Checks for tests directory (tests/ or __tests__/)
  - Checks for .gitignore

- **Git History Analysis**
  - Total commit count
  - Date of most recent commit

- **Commit Quality Checks** (optional)
  - Analyzes recent commits for bad messages (e.g., "wip", very short)
  - Checks for recent activity

- **Security Scan** (optional)
  - Scans for potential secrets in .env files, config files
  - Checks for private keys

- **Code Quality Checks** (optional)
  - Detects long functions (>50 lines)
  - Identifies circular dependencies
  - Scans for high-entropy strings (potential hardcoded secrets)
- **Language-Specific Checks** (optional)
  - Detects primary language (Python, JavaScript/TypeScript, Go)
  - Checks for relevant files (requirements.txt, package.json, go.mod, etc.)
  - Provides resolution tips for failed checks

- **Code Quality Checks** (optional)
  - Detects long functions (>50 lines)
  - Identifies circular dependencies using directed graph analysis
  - Scans for high-entropy strings (potential hardcoded secrets)

- **Code Coverage Analysis** (optional)
  - Estimates test coverage for Python code
  - Analyzes function and line coverage
  - Identifies untested modules and functions
  - Provides coverage statistics and improvement tips

- **Health Score**
  - Calculates a score out of 100 based on all checks
  - Provides a category (Excellent, Good, Fair, Poor, Critical)

## Requirements

- Python 3.6 or higher
- Git installed and available in PATH
- A local git repository to analyze

## Installation

No installation required! Just clone or download this repository.

## Usage

### Basic Usage

Analyze the current directory with all checks enabled (if it's a git repository):
```bash
python main.py
```

### Analyze a Specific Repository

```bash
python main.py /path/to/repository
```

### Selective Checks

Run only specific checks with command-line flags:

```bash
# Run only commit quality checks
python main.py --check-commits

# Run only security scan for secrets
python main.py --check-security

# Run only language-specific checks
python main.py --check-language

# Combine multiple checks
python main.py --check-commits --check-security
```

### Examples

```bash
# Full analysis (all checks) of current directory
python main.py

# Full analysis of a specific repository
python main.py ../my-project

# Analyze with explicit current directory (all checks)
python main.py .

# Run only security scan on a repository
python main.py --check-security /path/to/repo
```

## Project Structure

```
repo-optimizer/
├── main.py          # Entry point
├── cli.py           # Command-line interface
├── analyzer.py      # Repository analysis logic
├── scoring.py       # Health score calculation
├── reporter.py      # Report formatting
├── utils.py         # Utility functions
└── README.md        # This file
```

## Scoring Breakdown

The health score is calculated out of 100 points:

- **README.md**: 20 points
- **LICENSE file**: 15 points
- **Tests directory**: 25 points
- **.gitignore**: 15 points
- **Git history** (at least 1 commit): 15 points
- **Recent activity** (commit in last 6 months): 10 points

Issues found in enabled checks apply penalties:

- **Commit Quality**: -10 points per warning (up to -30)
- **Security**: -20 points per warning (up to -50)
- **Language Specific**: -10 points per warning (up to -30)
- **Code Quality**:
  - Long functions: -5 points per (up to -20)
  - Circular dependencies: -15 points per (up to -30)
  - High-entropy secrets: -20 points per (up to -40)
- **Code Coverage**: -15 points per warning (up to -45)

### Score Categories

- **90-100**: Excellent
- **70-89**: Good
- **50-69**: Fair
- **30-49**: Poor
- **0-29**: Critical

## Example Output

```
============================================================
📁 Analyzing repository: /path/to/my-repo
============================================================
🔧 CONFIGURATION:
  ✅ Commit quality checks enabled
  ✅ Security scan for secrets enabled
  ✅ Language-specific checks enabled
  ✅ Code quality checks enabled

⏳ ANALYSIS IN PROGRESS...

🔍 Analyzing repository structure...
✓ Repository structure analyzed
📊 Analyzing git history...
✓ Git history analyzed
🔒 Scanning for security issues...
✓ Security scan completed
💻 Analyzing language-specific requirements...
✓ Language analysis completed
======================================================================
  🏥 Git Repository Health Checker
======================================================================

📁 Repository: /path/to/my-repo
📅 Analysis Date: 2024-01-15 10:30:45

----------------------------------------------------------------------
  📊 HEALTH SCORE
----------------------------------------------------------------------
Score: 40/100 (Poor)

📊 SCORE BREAKDOWN:
  Base Score: +60
  Structure: +35
  History: +25
  Commit Quality: -30
  Security: 0
  Language Specific: -20
  Code Quality: -25

----------------------------------------------------------------------
  📁 REPOSITORY STRUCTURE
----------------------------------------------------------------------
  ✓ README.md
  ✗ LICENSE file
    💡 Tip: Add a LICENSE file (e.g., MIT, Apache) to specify usage rights.
  ✗ Tests directory (tests/ or __tests__/)
    💡 Tip: Add tests to ensure code reliability.
  ✓ .gitignore

----------------------------------------------------------------------
  📈 GIT HISTORY
----------------------------------------------------------------------
  Total Commits: 42
  Most Recent Commit: 2024-01-10 14:22:33

----------------------------------------------------------------------
  🔍 COMMIT QUALITY
----------------------------------------------------------------------
  ✓ No quality issues found in recent commits

----------------------------------------------------------------------
  🔒 SECURITY SCAN
----------------------------------------------------------------------
  🔍 Scanned Files: 2
  ✓ No potential secrets found

----------------------------------------------------------------------
  💻 LANGUAGE SPECIFIC
----------------------------------------------------------------------
  🏷️  Primary Language: Python
  ⚠ Python project missing dependency file (requirements.txt, pyproject.toml, or setup.py)
    💡 Tip: Create a requirements.txt or pyproject.toml file to manage dependencies.
  ⚠ Python project missing tests
    💡 Tip: Add test files in a 'tests/' directory or as 'test_*.py' files.
----------------------------------------------------------------------
  🔧 CODE QUALITY
----------------------------------------------------------------------
  ⚠ Long function 'long_function' in test_long.py: 54 lines
    💡 Tip: Break down long functions into smaller, more manageable pieces.

======================================================================
============================================================
✅ Analysis complete! Review the report above for insights.
============================================================
```

## Error Handling

The tool will exit with an error message if:
- The provided path doesn't exist
- The path is not a directory
- The path is not a git repository

If git history cannot be analyzed (e.g., empty repository), the tool will still run and report available information.

## Resolution Tips

The tool provides actionable tips for failed checks:

- **Missing LICENSE**: Add a LICENSE file to your repository root
- **No Tests**: Create a `tests/` directory and add test files
- **Committed node_modules**: Add `node_modules/` to your `.gitignore`
- **Secrets in Files**: Remove sensitive data or use environment variables
- **Bad Commit Messages**: Use descriptive commit messages (e.g., "Fix bug in login validation")
- **Long Functions**: Break down into smaller, focused functions
- **Circular Dependencies**: Refactor to eliminate import cycles
- **High-Entropy Strings**: Replace with secure credential management
- **Low Test Coverage**: Add unit tests for untested functions and modules

## Limitations

- Only analyzes the repository root (does not scan subdirectories for files)
- Tests directory check only looks for `tests/` or `__tests__/` in the root
- LICENSE check is case-insensitive but only checks common variations
- Requires git to be installed and accessible
- Security scan is basic and may have false positives/negatives
- Language detection based on file extensions only

## Future Enhancements

Potential features for future versions:
- CI/CD configuration detection
- Dependency analysis
- Code quality metrics
- More language support
- Custom configuration files

## License

This project is provided as-is for educational and development purposes.

