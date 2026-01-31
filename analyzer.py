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


def analyze_git_history(repo_path: str) -> Dict[str, any]:
    """
    Analyze git history to get commit statistics.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with git history analysis results
    """
    results = {
        'total_commits': 0,
        'most_recent_commit_date': None,
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
        
    except subprocess.CalledProcessError as e:
        # If git command fails, return default values
        print(f"Warning: Could not analyze git history: {e}")
    except ValueError as e:
        # If date parsing fails
        print(f"Warning: Could not parse commit date: {e}")
    except Exception as e:
        print(f"Warning: Unexpected error analyzing git history: {e}")
    
    return results


def analyze_repository(repo_path: str) -> Dict[str, any]:
    """
    Perform complete repository analysis.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary containing all analysis results
    """
    structure = analyze_repository_structure(repo_path)
    history = analyze_git_history(repo_path)
    
    return {
        'structure': structure,
        'history': history,
    }

