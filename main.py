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
from cli import get_args
from reporter import format_report, print_report
from scoring import calculate_health_score, get_score_category


def main():
    """
    Main entry point for the Git Repo Health Checker.
    """
    # Get and validate arguments from CLI
    args = get_args()
    repo_path = args.repo_path
    
    # Analyze the repository
    print(f"Analyzing repository: {repo_path}")
    print("Please wait...\n")
    
    analysis_results = analyze_repository(repo_path, args)

    # Calculate health score
    health_score = calculate_health_score(analysis_results, args)
    score_category = get_score_category(health_score)
    
    # Generate and print report
    report = format_report(analysis_results, repo_path, health_score, score_category, args)
    print_report(report)


if __name__ == '__main__':
    main()

