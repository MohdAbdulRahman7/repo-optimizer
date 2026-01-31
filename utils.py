"""
Utility functions for the Git Repo Health Checker.
Provides helper functions for validation and file operations.
"""

import os
import sys
from pathlib import Path


# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'


def print_progress(message: str, status: str = "", color: str = Colors.BLUE):
    """Print a progress message with optional status and color."""
    if status:
        print(f"{color}{message} {status}{Colors.RESET}")
    else:
        print(f"{color}{message}{Colors.RESET}")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_header(message: str):
    """Print a header message."""
    print(f"{Colors.BOLD}{Colors.CYAN}{message}{Colors.RESET}")


def print_score(score: int, category: str):
    """Print the health score with color based on category."""
    color_map = {
        "Excellent": Colors.GREEN,
        "Good": Colors.GREEN,
        "Fair": Colors.YELLOW,
        "Poor": Colors.RED,
        "Critical": Colors.RED
    }
    color = color_map.get(category, Colors.WHITE)
    print(f"{color}{Colors.BOLD}Score: {score}/100 ({category}){Colors.RESET}")


def is_git_repository(repo_path: str) -> bool:
    """
    Check if the given path is a valid git repository.
    
    Args:
        repo_path: Path to check
        
    Returns:
        True if the path contains a .git directory, False otherwise
    """
    git_dir = Path(repo_path) / '.git'
    return git_dir.exists() and git_dir.is_dir()


def validate_repo_path(repo_path: str) -> str:
    """
    Validate and normalize the repository path.
    
    Args:
        repo_path: Path to validate
        
    Returns:
        Normalized absolute path
        
    Raises:
        ValueError: If the path doesn't exist or isn't a git repository
    """
    # Convert to absolute path
    abs_path = os.path.abspath(repo_path)
    
    # Check if path exists
    if not os.path.exists(abs_path):
        raise ValueError(f"Path does not exist: {abs_path}")
    
    # Check if it's a directory
    if not os.path.isdir(abs_path):
        raise ValueError(f"Path is not a directory: {abs_path}")
    
    # Check if it's a git repository
    if not is_git_repository(abs_path):
        raise ValueError(f"Path is not a git repository: {abs_path}")
    
    return abs_path


def file_exists(repo_path: str, filename: str) -> bool:
    """
    Check if a file exists in the repository root.
    
    Args:
        repo_path: Path to the repository
        filename: Name of the file to check
        
    Returns:
        True if the file exists, False otherwise
    """
    file_path = Path(repo_path) / filename
    return file_path.exists() and file_path.is_file()


def directory_exists(repo_path: str, dirname: str) -> bool:
    """
    Check if a directory exists in the repository.
    
    Args:
        repo_path: Path to the repository
        dirname: Name of the directory to check
        
    Returns:
        True if the directory exists, False otherwise
    """
    dir_path = Path(repo_path) / dirname
    return dir_path.exists() and dir_path.is_dir()

