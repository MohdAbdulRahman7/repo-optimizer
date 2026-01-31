"""
Report formatting module.
Formats analysis results into a readable terminal report.
"""

from datetime import datetime
from typing import Dict
from utils import Colors, print_header, print_score, print_success, print_warning, print_error


def format_report(analysis_results: Dict[str, any], repo_path: str, health_score: int, score_category: str, options: Dict[str, bool] = None) -> str:
    """
    Format analysis results into a readable terminal report.

    Args:
        analysis_results: Dictionary containing analysis results
        repo_path: Path to the analyzed repository
        health_score: Calculated health score (0-100)
        score_category: Category of the health score
        options: Dictionary of enabled options

    Returns:
        Formatted report string
    """
    if options is None:
        options = {}

    structure = analysis_results.get('structure', {})
    history = analysis_results.get('history', {})
    security = analysis_results.get('security', {})
    language = analysis_results.get('language', {})

    report_lines = []

    # Header
    report_lines.append(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.CYAN}  🏥 Git Repository Health Checker{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    report_lines.append(f"\n📁 Repository: {repo_path}")
    report_lines.append(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    # Health Score
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  📊 HEALTH SCORE{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

    # Color the score based on category
    color_map = {
        "Excellent": Colors.GREEN,
        "Good": Colors.GREEN,
        "Fair": Colors.YELLOW,
        "Poor": Colors.RED,
        "Critical": Colors.RED
    }
    score_color = color_map.get(score_category, Colors.WHITE)
    report_lines.append(f"{score_color}{Colors.BOLD}Score: {health_score}/100 ({score_category}){Colors.RESET}")
    report_lines.append("")

    # Repository Structure
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  📁 REPOSITORY STRUCTURE{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

    # README
    if structure.get('has_readme', False):
        report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} README.md")
    else:
        report_lines.append(f"  {Colors.RED}✗{Colors.RESET} README.md")

    # LICENSE
    if structure.get('has_license', False):
        report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} LICENSE file")
    else:
        report_lines.append(f"  {Colors.RED}✗{Colors.RESET} LICENSE file")

    # Tests
    if structure.get('has_tests', False):
        report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} Tests directory (tests/ or __tests__/)")
    else:
        report_lines.append(f"  {Colors.RED}✗{Colors.RESET} Tests directory (tests/ or __tests__/)")

    # .gitignore
    if structure.get('has_gitignore', False):
        report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} .gitignore")
    else:
        report_lines.append(f"  {Colors.RED}✗{Colors.RESET} .gitignore")

    report_lines.append("")

    # Git History
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  📈 GIT HISTORY{Colors.RESET}")
    report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

    total_commits = history.get('total_commits', 0)
    report_lines.append(f"  Total Commits: {total_commits}")

    most_recent_date = history.get('most_recent_commit_date')
    if most_recent_date:
        date_str = most_recent_date.strftime('%Y-%m-%d %H:%M:%S')
        report_lines.append(f"  Most Recent Commit: {date_str}")
    else:
        report_lines.append("  Most Recent Commit: N/A")

    report_lines.append("")

    # Commit Quality (if enabled)
    if options.get('check_commits', False):
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  🔍 COMMIT QUALITY{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

        commit_warnings = history.get('commits_quality_warnings', [])
        if commit_warnings:
            for warning in commit_warnings:
                report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
        else:
            report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} No quality issues found in recent commits")

        report_lines.append("")

    # Security (if enabled)
    if options.get('check_security', False):
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  🔒 SECURITY SCAN{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

        secrets_warnings = security.get('secrets_warnings', [])
        scanned_files = security.get('scanned_files', 0)
        report_lines.append(f"  🔍 Scanned Files: {scanned_files}")

        if secrets_warnings:
            for warning in secrets_warnings:
                report_lines.append(f"  {Colors.RED}⚠{Colors.RESET} {warning}")
        else:
            report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} No potential secrets found")

        report_lines.append("")

    # Language Specific (if enabled)
    if options.get('check_language', False):
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  💻 LANGUAGE SPECIFIC{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

        primary_lang = language.get('primary_language', 'unknown')
        report_lines.append(f"  🏷️  Primary Language: {primary_lang.capitalize()}")

        language_warnings = language.get('language_warnings', [])
        if language_warnings:
            for warning in language_warnings:
                report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
        else:
            report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} Language-specific checks passed")

        report_lines.append("")

    # Footer
    report_lines.append(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")

    return "\n".join(report_lines)


def print_report(report: str) -> None:
    """
    Print the formatted report to the terminal.
    
    Args:
        report: Formatted report string
    """
    print(report)

