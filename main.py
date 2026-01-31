#!/usr/bin/env python3
"""
Git Repo Health Checker - Main Entry Point

A terminal-based tool that analyzes local git repositories and provides
a health score based on repository structure and git history.

Usage:
    python main.py [repo_path]
    
    If repo_path is not provided, defaults to current directory.
"""

from analyzer import analyze_repository
from cli import get_repo_path_and_options
from reporter import format_report, print_report
from scoring import calculate_health_score, get_score_category


def main():
    """
    Main entry point for the Git Repo Health Checker.
    """
    # Get and validate repository path and options from CLI
    repo_path, options = get_repo_path_and_options()

    # If no specific checks specified, enable all
    if not any(options.values()):
        options = {'check_commits': True, 'check_security': True, 'check_language': True}

    # Analyze the repository
    print(f"📁 Analyzing repository: {repo_path}")
    enabled_checks = []
    if options['check_commits']:
        enabled_checks.append("Commit Quality")
    if options['check_security']:
        enabled_checks.append("Security Scan")
    if options['check_language']:
        enabled_checks.append("Language Checks")
    if enabled_checks:
        print(f"🔍 Enabled checks: {', '.join(enabled_checks)}")
    print("⏳ Analyzing...\n")

    analysis_results = analyze_repository(repo_path, options)

    # Calculate health score
    health_score = calculate_health_score(analysis_results, options)
    score_category = get_score_category(health_score)

    # Generate and print report
    report = format_report(analysis_results, repo_path, health_score, score_category, options)
    print_report(report)


if __name__ == '__main__':
    main()

