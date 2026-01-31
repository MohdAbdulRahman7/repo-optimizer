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

- **Language-Specific Checks** (optional)
  - Detects primary language (Python, JavaScript/TypeScript, Go)
  - Checks for relevant files (requirements.txt, package.json, go.mod, etc.)

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

### Score Categories

- **90-100**: Excellent
- **70-89**: Good
- **50-69**: Fair
- **30-49**: Poor
- **0-29**: Critical

## Example Output

```
📁 Analyzing repository: /path/to/my-repo
🔍 Enabled checks: Commit Quality, Security Scan, Language Checks
⏳ Analyzing...

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
Score: 85/100 (Good)

----------------------------------------------------------------------
  📁 REPOSITORY STRUCTURE
----------------------------------------------------------------------
  ✓ README.md
  ✓ LICENSE file
  ✓ Tests directory (tests/ or __tests__/)
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
  ✓ Language-specific checks passed

======================================================================
```

## Error Handling

The tool will exit with an error message if:
- The provided path doesn't exist
- The path is not a directory
- The path is not a git repository

If git history cannot be analyzed (e.g., empty repository), the tool will still run and report available information.

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

