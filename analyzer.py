"""
Repository analyzer module.
Analyzes repository structure and git history.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from utils import file_exists, directory_exists
import re


def analyze_repository_structure(repo_path: str) -> Dict[str, bool]:
    """
    Analyze the repository structure for common files and directories.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with analysis results for each check
    """
    results = {
        'has_readme': file_exists(repo_path, 'README.md'),
        'has_license': _check_license_file(repo_path),
        'has_tests': _check_tests_directory(repo_path),
        'has_gitignore': file_exists(repo_path, '.gitignore'),
    }
    
    return results


def _check_license_file(repo_path: str) -> bool:
    """
    Check if a LICENSE file exists (case-insensitive).
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if LICENSE file exists (any case variation)
    """
    repo = Path(repo_path)
    # Check common LICENSE file variations
    license_variations = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'license', 'License']
    
    for license_file in license_variations:
        if (repo / license_file).exists():
            return True
    
    return False


def analyze_commit_quality(commits: list[str]) -> list[str]:
    """
    Analyze commit messages for quality issues.

    Args:
        commits: List of commit lines (oneline format)

    Returns:
        List of warning messages
    """
    warnings = []
    bad_keywords = ['wip', 'fix', 'temp', 'test', 'debug', 'hack']
    very_short_threshold = 10

    for commit in commits:
        if not commit.strip():
            continue
        # Split to get message
        parts = commit.split(' ', 1)
        if len(parts) < 2:
            continue
        message = parts[1].lower()

        # Check for bad keywords
        for keyword in bad_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', message):
                warnings.append(f"Bad commit message: '{commit.strip()}' (contains '{keyword}')")

        # Check for very short messages
        if len(message) < very_short_threshold and not message.startswith('merge'):
            warnings.append(f"Very short commit message: '{commit.strip()}'")

    # Remove duplicates
    return list(set(warnings))


def _check_tests_directory(repo_path: str) -> bool:
    """
    Check if a tests directory exists (tests/ or __tests__/).
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if either tests/ or __tests__/ directory exists
    """
    return (directory_exists(repo_path, 'tests') or 
            directory_exists(repo_path, '__tests__'))


def analyze_git_history(repo_path: str, options: Dict[str, bool] = None) -> Dict[str, any]:
    """
    Analyze git history to get commit statistics.

    Args:
        repo_path: Path to the repository
        options: Dictionary of optional checks to enable

    Returns:
        Dictionary with git history analysis results
    """
    if options is None:
        options = {}

    results = {
        'total_commits': 0,
        'most_recent_commit_date': None,
        'commits_quality_warnings': [],
    }

    try:
        # Get total commit count
        commit_count_cmd = ['git', 'rev-list', '--count', 'HEAD']
        commit_count_result = subprocess.run(
            commit_count_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        results['total_commits'] = int(commit_count_result.stdout.strip())

        # Get most recent commit date
        date_cmd = ['git', 'log', '-1', '--format=%ci', 'HEAD']
        date_result = subprocess.run(
            date_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )

        if date_result.stdout.strip():
            # Parse the date string (format: "2024-01-15 10:30:45 -0500")
            date_str = date_result.stdout.strip()
            # Extract just the date and time part (first 19 characters)
            date_part = date_str[:19]
            results['most_recent_commit_date'] = datetime.strptime(
                date_part, '%Y-%m-%d %H:%M:%S'
            )

        if options.get('check_commits', False):
            # Analyze commit messages
            log_cmd = ['git', 'log', '--oneline', '-100']  # Last 100 commits
            log_result = subprocess.run(
                log_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commits = log_result.stdout.strip().split('\n') if log_result.stdout.strip() else []
            results['commits_quality_warnings'] = analyze_commit_quality(commits)

    except subprocess.CalledProcessError as e:
        # If git command fails, return default values
        print(f"Warning: Could not analyze git history: {e}")
    except ValueError as e:
        # If date parsing fails
        print(f"Warning: Could not parse commit date: {e}")
    except Exception as e:
        print(f"Warning: Unexpected error analyzing git history: {e}")

    return results


def analyze_repository(repo_path: str, options: Dict[str, bool] = None) -> Dict[str, any]:
    """
    Perform complete repository analysis.

    Args:
        repo_path: Path to the repository
        options: Dictionary of optional checks to enable

    Returns:
        Dictionary containing all analysis results
    """
    if options is None:
        options = {}

    structure = analyze_repository_structure(repo_path)
    history = analyze_git_history(repo_path, options)

    results = {
        'structure': structure,
        'history': history,
    }

    if options.get('check_security', False):
        security = analyze_security(repo_path)
        results['security'] = security

    if options.get('check_language', False):
        language = analyze_language_specific(repo_path)
        results['language'] = language

    return results


def analyze_security(repo_path: str) -> Dict[str, any]:
    """
    Perform offline security scan for secrets.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with security analysis results
    """
    results = {
        'secrets_warnings': [],
        'scanned_files': 0,
    }

    repo = Path(repo_path)

    # Files to check for secrets
    suspicious_files = [
        '.env', '.env.local', '.env.production', '.env.staging',
        'config.json', 'config.yml', 'config.yaml',
        'secrets.json', 'secrets.yml', 'secrets.yaml',
        'credentials.json', 'credentials.yml', 'credentials.yaml',
    ]

    # Patterns for secrets
    secret_patterns = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,})["\']?', 'API Key'),
        (r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,})["\']?', 'Secret Key'),
        (r'(?i)(password|pwd)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{8,})["\']?', 'Password'),
        (r'(?i)(token)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,})["\']?', 'Token'),
        (r'(?i)(private[_-]?key)\s*[:=]\s*["\']?-----BEGIN.*-----', 'Private Key'),
    ]

    # Check specific files
    for file in suspicious_files:
        file_path = repo / file
        if file_path.exists() and file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    results['scanned_files'] += 1
                    for pattern, desc in secret_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if isinstance(match, tuple):
                                value = match[1] if len(match) > 1 else match[0]
                            else:
                                value = match
                            results['secrets_warnings'].append(f"Potential {desc} in {file}: {value[:10]}...")
            except Exception as e:
                results['secrets_warnings'].append(f"Error scanning {file}: {str(e)}")

    # Check for private keys in common locations
    private_key_files = ['id_rsa', 'id_ed25519', 'private.pem', 'key.pem']
    for key_file in private_key_files:
        key_path = repo / key_file
        if key_path.exists() and key_path.is_file():
            results['secrets_warnings'].append(f"Private key file found: {key_file}")

    return results


def detect_primary_language(repo_path: str) -> str:
    """
    Detect the primary programming language based on file extensions.

    Args:
        repo_path: Path to the repository

    Returns:
        Detected language ('python', 'javascript', 'go', 'unknown')
    """
    repo = Path(repo_path)
    extensions = {'python': ['.py'], 'javascript': ['.js', '.ts', '.jsx', '.tsx'], 'go': ['.go']}

    counts = {'python': 0, 'javascript': 0, 'go': 0}

    for file in repo.rglob('*'):
        if file.is_file():
            ext = file.suffix.lower()
            for lang, exts in extensions.items():
                if ext in exts:
                    counts[lang] += 1

    if counts['python'] > 0 or counts['javascript'] > 0 or counts['go'] > 0:
        return max(counts, key=counts.get)
    return 'unknown'


def analyze_language_specific(repo_path: str) -> Dict[str, any]:
    """
    Analyze language-specific requirements.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with language-specific analysis results
    """
    results = {
        'primary_language': 'unknown',
        'language_warnings': [],
    }

    language = detect_primary_language(repo_path)
    results['primary_language'] = language

    if language == 'python':
        # Check for requirements.txt, pyproject.toml, setup.py, and tests
        has_req = file_exists(repo_path, 'requirements.txt')
        has_pyproject = file_exists(repo_path, 'pyproject.toml')
        has_setup = file_exists(repo_path, 'setup.py')
        has_tests = directory_exists(repo_path, 'tests') or directory_exists(repo_path, '__tests__')
        if not has_tests:
            # Check for test files
            repo = Path(repo_path)
            test_files = list(repo.glob('test_*.py'))
            has_tests = len(test_files) > 0

        if not (has_req or has_pyproject or has_setup):
            results['language_warnings'].append("Python project missing dependency file (requirements.txt, pyproject.toml, or setup.py)")
        if not has_tests:
            results['language_warnings'].append("Python project missing tests")

    elif language == 'javascript':
        # Check for package.json, scripts, and node_modules not committed
        has_package = file_exists(repo_path, 'package.json')
        if not has_package:
            results['language_warnings'].append("JavaScript/TypeScript project missing package.json")

        # Check if node_modules is committed (bad)
        if directory_exists(repo_path, 'node_modules'):
            results['language_warnings'].append("node_modules directory is committed (should be in .gitignore)")

        # Check for scripts in package.json
        if has_package:
            try:
                import json
                with open(Path(repo_path) / 'package.json', 'r') as f:
                    pkg = json.load(f)
                    scripts = pkg.get('scripts', {})
                    if not scripts:
                        results['language_warnings'].append("package.json has no scripts defined")
            except Exception as e:
                results['language_warnings'].append(f"Error parsing package.json: {str(e)}")

    elif language == 'go':
        # Check for go.mod, go.sum
        has_go_mod = file_exists(repo_path, 'go.mod')
        has_go_sum = file_exists(repo_path, 'go.sum')

        if not has_go_mod:
            results['language_warnings'].append("Go project missing go.mod")
        if not has_go_sum:
            results['language_warnings'].append("Go project missing go.sum")

    return results

