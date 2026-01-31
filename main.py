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
        options = {'check_commits': True, 'check_security': True, 'check_language': True, 'check_code_quality': True, 'check_coverage': True}

    # Analyze the repository
    print(f"{'='*60}")
    print(f"📁 Analyzing repository: {repo_path}")
    print(f"{'='*60}")
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

    analysis_results = analyze_repository(repo_path, options)

    # Calculate health score
    health_score, score_breakdown = calculate_health_score(analysis_results, options)
    score_category = get_score_category(health_score)

    # Generate and print report
    report = format_report(analysis_results, repo_path, health_score, score_category, options, score_breakdown)
    print_report(report)
    print(f"{'='*60}")
    print("✅ Analysis complete! Review the report above for insights.")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

