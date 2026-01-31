"""
Report formatting module.
Formats analysis results into a readable terminal report.
"""

from datetime import datetime
from typing import Dict

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Icons
PASS_ICON = '✓'
FAIL_ICON = '✗'
WARN_ICON = '⚠'


def format_report(analysis_results: Dict[str, any], repo_path: str, health_score: int, score_category: str, args) -> str:
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

    # Color the score based on category
    if score_category == "Excellent":
        score_color = GREEN
    elif score_category == "Good":
        score_color = BLUE
    elif score_category == "Fair":
        score_color = YELLOW
    else:
        score_color = RED

    report_lines.append(f"Score: {score_color}{health_score}/100 ({score_category}){RESET}")

    # Progress bar
    filled = health_score // 10
    bar = '█' * filled + '░' * (10 - filled)
    report_lines.append(f"[{bar}] {health_score}%")
    report_lines.append("")
    
    # Repository Structure
    report_lines.append("-" * 70)
    report_lines.append("  REPOSITORY STRUCTURE")
    report_lines.append("-" * 70)

    # README
    readme_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if structure.get('has_readme', False) else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
    report_lines.append(f"  {readme_status} README.md")

    # LICENSE
    license_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if structure.get('has_license', False) else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
    report_lines.append(f"  {license_status} LICENSE file")

    # Tests
    tests_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if structure.get('has_tests', False) else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
    report_lines.append(f"  {tests_status} Tests directory (tests/ or __tests__/)")

    # .gitignore
    gitignore_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if structure.get('has_gitignore', False) else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
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

    if args.check_commits:
        bad_messages = history.get('bad_commit_messages', 0)
        short_commits = history.get('short_commits', 0)
        report_lines.append(f"  Bad Commit Messages (wip-like): {bad_messages}")
        report_lines.append(f"  Very Short Commits (<10 chars): {short_commits}")
        if bad_messages > 0 or short_commits > 0:
            report_lines.append(f"  {YELLOW}⚠ WARNING: Poor commit quality detected!{RESET}")

    report_lines.append("")

    # Security Scan
    if args.check_security:
        security = analysis_results.get('security', {})
        report_lines.append("-" * 70)
        report_lines.append("  SECURITY SCAN")
        report_lines.append("-" * 70)

        has_env = security.get('has_env_files', False)
        env_status = f"{YELLOW}{WARN_ICON} [WARN]{RESET}" if has_env else f"{GREEN}{PASS_ICON} [OK]{RESET}"
        report_lines.append(f"  {env_status} .env files present: {has_env}")

        secrets = security.get('potential_secrets', [])
        secrets_status = f"{YELLOW}{WARN_ICON} [WARN]{RESET}" if secrets else f"{GREEN}{PASS_ICON} [OK]{RESET}"
        report_lines.append(f"  {secrets_status} Potential secrets found: {len(secrets)}")
        if secrets:
            report_lines.append(f"  {YELLOW}⚠ WARNING: Potential secrets detected in code!{RESET}")
            for secret in secrets[:5]:  # Show first 5
                report_lines.append(f"    {secret}")
            if len(secrets) > 5:
                report_lines.append(f"    ... and {len(secrets) - 5} more")

        report_lines.append("")

    # Language Checks
    if args.check_language:
        language = analysis_results.get('language', {})
        primary_lang = language.get('primary_language', 'Unknown')
        report_lines.append("-" * 70)
        report_lines.append("  LANGUAGE-SPECIFIC CHECKS")
        report_lines.append("-" * 70)
        report_lines.append(f"  Primary Language: {primary_lang}")

        lang_checks = language.get('language_checks', {})
        if primary_lang == 'Python':
            req_bool = lang_checks.get('has_requirements', False) or lang_checks.get('has_pyproject', False)
            req_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if req_bool else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
            report_lines.append(f"  {req_status} Dependencies file (requirements.txt/pyproject.toml)")
            test_bool = lang_checks.get('has_tests', False)
            test_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if test_bool else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
            report_lines.append(f"  {test_status} Tests directory")
        elif primary_lang == 'JavaScript/TypeScript':
            pkg_bool = lang_checks.get('has_package_json', False)
            pkg_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if pkg_bool else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
            report_lines.append(f"  {pkg_status} package.json")
            script_bool = lang_checks.get('has_scripts_in_package', False)
            script_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if script_bool else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
            report_lines.append(f"  {script_status} Scripts in package.json")
            node_bool = not lang_checks.get('node_modules_committed', False)
            node_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if node_bool else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
            report_lines.append(f"  {node_status} node_modules not committed")
            if lang_checks.get('node_modules_committed', False):
                report_lines.append(f"  {YELLOW}⚠ WARNING: node_modules should not be committed!{RESET}")
        elif primary_lang == 'Go':
            mod_bool = lang_checks.get('has_go_mod', False)
            mod_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if mod_bool else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
            report_lines.append(f"  {mod_status} go.mod")
            sum_bool = lang_checks.get('has_go_sum', False)
            sum_status = f"{GREEN}{PASS_ICON} [PASS]{RESET}" if sum_bool else f"{RED}{FAIL_ICON} [FAIL]{RESET}"
            report_lines.append(f"  {sum_status} go.sum")

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

