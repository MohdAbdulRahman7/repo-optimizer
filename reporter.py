"""
Report formatting module.
Formats analysis results into a readable terminal report.
"""

from datetime import datetime
from typing import Dict


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

    if args.check_commits:
        bad_messages = history.get('bad_commit_messages', 0)
        short_commits = history.get('short_commits', 0)
        report_lines.append(f"  Bad Commit Messages (wip-like): {bad_messages}")
        report_lines.append(f"  Very Short Commits (<10 chars): {short_commits}")
        if bad_messages > 0 or short_commits > 0:
            report_lines.append("  WARNING: Poor commit quality detected!")

    report_lines.append("")

    # Security Scan
    if args.check_security:
        security = analysis_results.get('security', {})
        report_lines.append("-" * 70)
        report_lines.append("  SECURITY SCAN")
        report_lines.append("-" * 70)

        has_env = security.get('has_env_files', False)
        env_status = "[WARN]" if has_env else "[OK]"
        report_lines.append(f"  {env_status} .env files present: {has_env}")

        secrets = security.get('potential_secrets', [])
        secrets_status = "[WARN]" if secrets else "[OK]"
        report_lines.append(f"  {secrets_status} Potential secrets found: {len(secrets)}")
        if secrets:
            report_lines.append("  WARNING: Potential secrets detected in code!")
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
            req_status = "[PASS]" if lang_checks.get('has_requirements', False) or lang_checks.get('has_pyproject', False) else "[FAIL]"
            report_lines.append(f"  {req_status} Dependencies file (requirements.txt/pyproject.toml)")
            test_status = "[PASS]" if lang_checks.get('has_tests', False) else "[FAIL]"
            report_lines.append(f"  {test_status} Tests directory")
        elif primary_lang == 'JavaScript/TypeScript':
            pkg_status = "[PASS]" if lang_checks.get('has_package_json', False) else "[FAIL]"
            report_lines.append(f"  {pkg_status} package.json")
            script_status = "[PASS]" if lang_checks.get('has_scripts_in_package', False) else "[FAIL]"
            report_lines.append(f"  {script_status} Scripts in package.json")
            node_status = "[FAIL]" if lang_checks.get('node_modules_committed', False) else "[PASS]"
            report_lines.append(f"  {node_status} node_modules not committed")
            if lang_checks.get('node_modules_committed', False):
                report_lines.append("  WARNING: node_modules should not be committed!")
        elif primary_lang == 'Go':
            mod_status = "[PASS]" if lang_checks.get('has_go_mod', False) else "[FAIL]"
            report_lines.append(f"  {mod_status} go.mod")
            sum_status = "[PASS]" if lang_checks.get('has_go_sum', False) else "[FAIL]"
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

