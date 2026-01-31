"""
Report formatting module.
Formats analysis results into a readable terminal report.
"""

from datetime import datetime
from typing import Dict


def format_report(analysis_results: Dict[str, any], repo_path: str, health_score: int, score_category: str) -> str:
    """
    Format analysis results into a readable terminal report.
    
    Args:
        analysis_results: Dictionary containing analysis results
        repo_path: Path to the analyzed repository
        health_score: Calculated health score (0-100)
        score_category: Category of the health score
        
    Returns:
        Formatted report string
    """
    structure = analysis_results.get('structure', {})
    history = analysis_results.get('history', {})
    
    report_lines = []
    
    # Header
    report_lines.append("=" * 70)
    report_lines.append("  Git Repository Health Checker")
    report_lines.append("=" * 70)
    report_lines.append(f"\nRepository: {repo_path}")
    report_lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Health Score
    report_lines.append("-" * 70)
    report_lines.append("  HEALTH SCORE")
    report_lines.append("-" * 70)
    report_lines.append(f"Score: {health_score}/100 ({score_category})")
    report_lines.append("")
    
    # Repository Structure
    report_lines.append("-" * 70)
    report_lines.append("  REPOSITORY STRUCTURE")
    report_lines.append("-" * 70)
    
    # README
    readme_status = "[PASS]" if structure.get('has_readme', False) else "[FAIL]"
    report_lines.append(f"  {readme_status} README.md")
    
    # LICENSE
    license_status = "[PASS]" if structure.get('has_license', False) else "[FAIL]"
    report_lines.append(f"  {license_status} LICENSE file")
    
    # Tests
    tests_status = "[PASS]" if structure.get('has_tests', False) else "[FAIL]"
    report_lines.append(f"  {tests_status} Tests directory (tests/ or __tests__/)")
    
    # .gitignore
    gitignore_status = "[PASS]" if structure.get('has_gitignore', False) else "[FAIL]"
    report_lines.append(f"  {gitignore_status} .gitignore")
    
    report_lines.append("")
    
    # Git History
    report_lines.append("-" * 70)
    report_lines.append("  GIT HISTORY")
    report_lines.append("-" * 70)
    
    total_commits = history.get('total_commits', 0)
    report_lines.append(f"  Total Commits: {total_commits}")
    
    most_recent_date = history.get('most_recent_commit_date')
    if most_recent_date:
        date_str = most_recent_date.strftime('%Y-%m-%d %H:%M:%S')
        report_lines.append(f"  Most Recent Commit: {date_str}")
    else:
        report_lines.append(f"  Most Recent Commit: N/A")
    
    report_lines.append("")
    
    # Footer
    report_lines.append("=" * 70)
    
    return "\n".join(report_lines)


def print_report(report: str) -> None:
    """
    Print the formatted report to the terminal.
    
    Args:
        report: Formatted report string
    """
    print(report)

