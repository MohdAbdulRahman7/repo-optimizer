"""
Repository analyzer module.
Analyzes repository structure and git history.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from utils import file_exists, directory_exists


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


def analyze_git_history(repo_path: str, check_commits: bool = False) -> Dict[str, any]:
    """
    Analyze git history to get commit statistics.

    Args:
        repo_path: Path to the repository
        check_commits: Whether to perform commit quality checks

    Returns:
        Dictionary with git history analysis results
    """
    results = {
        'total_commits': 0,
        'most_recent_commit_date': None,
    }

    if check_commits:
        results.update({
            'bad_commit_messages': 0,
            'short_commits': 0,
        })
    
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

        if check_commits and results['total_commits'] > 0:
            # Analyze commit quality
            try:
                # Get commit messages
                msg_cmd = ['git', 'log', '--format=%s', 'HEAD']
                msg_result = subprocess.run(
                    msg_cmd,
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                messages = msg_result.stdout.strip().split('\n')
                bad_count = 0
                short_count = 0
                for msg in messages:
                    msg = msg.strip()
                    if len(msg) < 10:
                        short_count += 1
                    if 'wip' in msg.lower() or 'work in progress' in msg.lower():
                        bad_count += 1
                results['bad_commit_messages'] = bad_count
                results['short_commits'] = short_count
            except subprocess.CalledProcessError:
                pass  # Ignore if fails

    except subprocess.CalledProcessError as e:
        # If git command fails, return default values
        print(f"Warning: Could not analyze git history: {e}")
    except ValueError as e:
        # If date parsing fails
        print(f"Warning: Could not parse commit date: {e}")
    except Exception as e:
        print(f"Warning: Unexpected error analyzing git history: {e}")

    return results


def analyze_security_scan(repo_path: str) -> Dict[str, any]:
    """
    Perform offline security scan for potential secrets.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with security scan results
    """
    results = {
        'has_env_files': False,
        'potential_secrets': [],
    }

    repo = Path(repo_path)

    # Check for .env files
    env_files = ['.env', '.env.local', '.env.production', '.env.development']
    for env_file in env_files:
        if file_exists(repo_path, env_file):
            results['has_env_files'] = True
            break

    # Search for potential secrets using grep
    secret_patterns = [
        r'API_KEY\s*=\s*[^#]*',
        r'SECRET\s*=\s*[^#]*',
        r'PRIVATE_KEY\s*=\s*[^#]*',
        r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
        r'password\s*=\s*[^#]*',
        r'token\s*=\s*[^#]*',
    ]

    try:
        for pattern in secret_patterns:
            # Use ripgrep if available, else git grep for tracked files
            try:
                grep_cmd = ['rg', '--regexp', pattern, '--no-heading', '--line-number', '--type', 'not', 'binary']
                grep_result = subprocess.run(
                    grep_cmd,
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=False  # Don't fail if no matches
                )
                if grep_result.returncode == 0:
                    lines = grep_result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            results['potential_secrets'].append(line)
            except FileNotFoundError:
                # Fallback to git grep for tracked files
                try:
                    git_grep_cmd = ['git', 'grep', '-n', pattern]
                    grep_result = subprocess.run(
                        git_grep_cmd,
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if grep_result.returncode == 0:
                        lines = grep_result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip():
                                results['potential_secrets'].append(line)
                except subprocess.CalledProcessError:
                    pass
    except Exception:
        pass  # Ignore errors in security scan

    return results


def analyze_language_checks(repo_path: str) -> Dict[str, any]:
    """
    Detect primary language and perform language-specific checks.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with language analysis results
    """
    results = {
        'primary_language': None,
        'language_checks': {},
    }

    # Detect language based on files
    if file_exists(repo_path, 'go.mod'):
        results['primary_language'] = 'Go'
        results['language_checks'] = _check_go_files(repo_path)
    elif file_exists(repo_path, 'package.json'):
        results['primary_language'] = 'JavaScript/TypeScript'
        results['language_checks'] = _check_js_files(repo_path)
    elif file_exists(repo_path, 'requirements.txt') or file_exists(repo_path, 'pyproject.toml') or file_exists(repo_path, 'setup.py'):
        results['primary_language'] = 'Python'
        results['language_checks'] = _check_python_files(repo_path)
    else:
        # Fallback: count file extensions
        results['primary_language'] = _detect_language_by_extensions(repo_path)

    return results


def _check_go_files(repo_path: str) -> Dict[str, bool]:
    """Check Go-specific files."""
    return {
        'has_go_mod': file_exists(repo_path, 'go.mod'),
        'has_go_sum': file_exists(repo_path, 'go.sum'),
    }


def _check_js_files(repo_path: str) -> Dict[str, bool]:
    """Check JS/TS-specific files."""
    checks = {
        'has_package_json': file_exists(repo_path, 'package.json'),
        'has_scripts_in_package': False,
        'node_modules_committed': directory_exists(repo_path, 'node_modules'),
    }
    if checks['has_package_json']:
        # Check if package.json has scripts
        try:
            import json
            with open(Path(repo_path) / 'package.json', 'r') as f:
                data = json.load(f)
                if 'scripts' in data and data['scripts']:
                    checks['has_scripts_in_package'] = True
        except:
            pass
    return checks


def _check_python_files(repo_path: str) -> Dict[str, bool]:
    """Check Python-specific files."""
    return {
        'has_requirements': file_exists(repo_path, 'requirements.txt'),
        'has_pyproject': file_exists(repo_path, 'pyproject.toml'),
        'has_setup_py': file_exists(repo_path, 'setup.py'),
        'has_tests': _check_tests_directory(repo_path),  # Reuse existing
    }


def _detect_language_by_extensions(repo_path: str) -> str:
    """Fallback language detection by file extensions."""
    repo = Path(repo_path)
    exts = {}
    for file in repo.rglob('*'):
        if file.is_file():
            ext = file.suffix.lower()
            exts[ext] = exts.get(ext, 0) + 1
    # Simple heuristic
    if exts.get('.py', 0) > max(exts.get('.js', 0), exts.get('.go', 0), exts.get('.ts', 0)):
        return 'Python'
    elif exts.get('.js', 0) + exts.get('.ts', 0) > max(exts.get('.py', 0), exts.get('.go', 0)):
        return 'JavaScript/TypeScript'
    elif exts.get('.go', 0) > max(exts.get('.py', 0), exts.get('.js', 0) + exts.get('.ts', 0)):
        return 'Go'
    else:
        return 'Unknown'


def analyze_repository(repo_path: str, args) -> Dict[str, any]:
    """
    Perform complete repository analysis.

    Args:
        repo_path: Path to the repository
        args: Parsed command-line arguments

    Returns:
        Dictionary containing all analysis results
    """
    structure = analyze_repository_structure(repo_path)
    history = analyze_git_history(repo_path, args.check_commits)

    results = {
        'structure': structure,
        'history': history,
    }

    if args.check_security:
        security = analyze_security_scan(repo_path)
        results['security'] = security

    if args.check_language:
        language = analyze_language_checks(repo_path)
        results['language'] = language

    return results

