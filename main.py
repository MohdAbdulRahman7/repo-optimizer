#!/usr/bin/env python3
"""
Git Repo Health Checker - Main Entry Point

A terminal-based tool that analyzes local git repositories and provides
a health score based on repository structure and git history.

Usage:
    python main.py [repo_path]

    If repo_path is not provided, defaults to current directory.
"""

import time
from analyzer import analyze_repository
from cli import get_repo_path_and_options
from reporter import format_report, print_report
from scoring import calculate_health_score, get_score_category
from utils import Colors


# Global for quiet mode
quiet_mode = False


def print_progress_bar(current, total, width=50):
    """Print a simple progress bar."""
    global quiet_mode
    if total == 0 or quiet_mode:
        return
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + '░' * (width - filled)
    percent = int(progress * 100)
    print(f"\r📊 Progress: [{bar}] {percent}% ({current}/{total})", end='', flush=True)
    if current == total:
        print()  # New line when complete


def main():
    """
    Main entry point for the Git Repo Health Checker.
    """
    start_time = time.time()

    # Get and validate repository path and options from CLI
    repo_path, options = get_repo_path_and_options()

    # If no specific checks specified, enable all
    if not any(options.values()):
        options = {'check_commits': True, 'check_security': True, 'check_language': True, 'check_code_quality': True, 'check_coverage': True}

    quiet = options.get('quiet', False)
    global quiet_mode
    quiet_mode = quiet
    output_format = options.get('format', 'text')
    output_file = options.get('output')

    # Analyze the repository
    if not quiet:
        print(f"{Colors.BOLD}{Colors.CYAN}{'┌' + '─' * 58 + '┐'}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}│{'Git Repo Health Checker'.center(58)}│{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'└' + '─' * 58 + '┘'}{Colors.RESET}")
        print(f"📁 Repository: {repo_path}")
        print("🔧 CONFIGURATION:")
        if options['check_commits']:
            print("  ✅ Commit quality checks enabled")
        if options['check_security']:
            print("  ✅ Security scan for secrets enabled")
        if options['check_language']:
            print("  ✅ Language-specific checks enabled")
        if options['check_code_quality']:
            print("  ✅ Code quality checks enabled")
        if options['check_coverage']:
            print("  ✅ Code coverage analysis enabled")
        print("\n⏳ ANALYSIS IN PROGRESS...\n")
        # Initialize progress bar
        total_steps = 2  # structure and history always
        if options.get('check_security'): total_steps += 1
        if options.get('check_language'): total_steps += 1
        if options.get('check_code_quality'): total_steps += 1
        if options.get('check_coverage'): total_steps += 1
        print_progress_bar(0, total_steps)

    analysis_results = analyze_repository(repo_path, options)

    # Calculate health score
    health_score, score_breakdown = calculate_health_score(analysis_results, options)
    score_category = get_score_category(health_score)

    # Generate report
    report = format_report(analysis_results, repo_path, health_score, score_category, options, score_breakdown, output_format)

    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(report)
            if not quiet:
                print(f"💾 Report saved to: {output_file}")
        except Exception as e:
            print(f"Error saving report: {e}")
    else:
        print_report(report, output_format)

    execution_time = time.time() - start_time
    if not quiet:
        print(f"{Colors.BOLD}{Colors.GREEN}✅ Analysis complete in {execution_time:.2f}s{Colors.RESET}")


if __name__ == '__main__':
    main()

