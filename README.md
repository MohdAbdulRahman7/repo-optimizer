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

Analyze the current directory (if it's a git repository):
```bash
python main.py
```

### Analyze a Specific Repository

```bash
python main.py /path/to/repository
```

### Examples

```bash
# Analyze current directory
python main.py

# Analyze a specific repository
python main.py ../my-project

# Analyze with explicit current directory
python main.py .
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

### Score Categories

- **90-100**: Excellent
- **70-89**: Good
- **50-69**: Fair
- **30-49**: Poor
- **0-29**: Critical

## Example Output

```
======================================================================
  Git Repository Health Checker
======================================================================

Repository: /path/to/my-repo
Analysis Date: 2024-01-15 10:30:45

----------------------------------------------------------------------
  HEALTH SCORE
----------------------------------------------------------------------
Score: 85/100 (Good)

----------------------------------------------------------------------
  REPOSITORY STRUCTURE
----------------------------------------------------------------------
  ✓ README.md
  ✓ LICENSE file
  ✓ Tests directory (tests/ or __tests__/)
  ✓ .gitignore

----------------------------------------------------------------------
  GIT HISTORY
----------------------------------------------------------------------
  Total Commits: 42
  Most Recent Commit: 2024-01-10 14:22:33

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

## Future Enhancements

Potential features for future versions:
- CI/CD configuration detection
- Security scanning
- Language-specific analysis
- Dependency analysis
- Code quality metrics

## License

This project is provided as-is for educational and development purposes.

