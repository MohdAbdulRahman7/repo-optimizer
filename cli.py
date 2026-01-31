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
  %(prog)s                    # Analyze current directory (all checks)
  %(prog)s /path/to/repo      # Analyze specific repository (all checks)
  %(prog)s .                  # Analyze current directory (explicit, all checks)
  %(prog)s --check-commits    # Run only commit quality checks
  %(prog)s --check-security   # Run only security scan
  %(prog)s --check-language          # Run only language-specific checks
  %(prog)s --check-code-quality     # Run only code quality checks
  %(prog)s --check-coverage         # Run only code coverage analysis
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
        help='Run only commit quality checks'
    )

    parser.add_argument(
        '--check-security',
        action='store_true',
        help='Run only offline security scan for secrets'
    )

    parser.add_argument(
        '--check-language',
        action='store_true',
        help='Run only language-specific checks (dependencies, etc.)'
    )

    parser.add_argument(
        '--check-code-quality',
        action='store_true',
        help='Run only code quality checks (long functions, circular deps, entropy)'
    )

    parser.add_argument(
        '--check-coverage',
        action='store_true',
        help='Run code coverage analysis (estimates test coverage)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-essential output'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json', 'yaml', 'markdown'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Save report to file'
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
            'check_code_quality': args.check_code_quality,
            'check_coverage': args.check_coverage,
            'verbose': args.verbose,
            'quiet': args.quiet,
            'format': args.format,
            'output': args.output,
        }
        return repo_path, options
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

