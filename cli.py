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
  %(prog)s --check-commits    # Include commit quality checks
  %(prog)s --check-security   # Include offline security scan
  %(prog)s --check-language   # Include language-specific checks
        """
    )

    parser.add_argument(
        'repo_path',
        nargs='?',
        default='.',
        help='Path to the git repository (default: current directory)'
    )

    parser.add_argument(
        '--check-commits',
        action='store_true',
        help='Enable commit quality checks (recent activity and bad commit messages)'
    )

    parser.add_argument(
        '--check-security',
        action='store_true',
        help='Enable offline security scan for secrets (.env files, API keys, etc.)'
    )

    parser.add_argument(
        '--check-language',
        action='store_true',
        help='Enable language-specific checks based on detected primary language'
    )

    return parser.parse_args()


def get_repo_path_and_options() -> tuple[str, dict]:
    """
    Get and validate the repository path and options from command-line arguments.

    Returns:
        Tuple of (validated absolute path to the repository, options dict)

    Raises:
        SystemExit: If validation fails
    """
    args = parse_arguments()

    try:
        repo_path = validate_repo_path(args.repo_path)
        options = {
            'check_commits': args.check_commits,
            'check_security': args.check_security,
            'check_language': args.check_language,
        }
        return repo_path, options
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

