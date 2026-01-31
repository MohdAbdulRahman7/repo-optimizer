"""
Command-line interface module.
Handles argument parsing and user interaction.
"""

import argparse
import sys
from pathlib import Path

from utils import validate_repo_path


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Git Repo Health Checker - Analyze local git repository health',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Analyze current directory
  %(prog)s /path/to/repo      # Analyze specific repository
  %(prog)s .                  # Analyze current directory (explicit)
        """
    )
    
    parser.add_argument(
        'repo_path',
        nargs='?',
        default='.',
        help='Path to the git repository (default: current directory)'
    )
    
    return parser.parse_args()


def get_repo_path() -> str:
    """
    Get and validate the repository path from command-line arguments.
    
    Returns:
        Validated absolute path to the repository
        
    Raises:
        SystemExit: If validation fails
    """
    args = parse_arguments()
    
    try:
        repo_path = validate_repo_path(args.repo_path)
        return repo_path
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

