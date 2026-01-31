"""
Report formatting module.
Formats analysis results into a readable terminal report.
"""

from datetime import datetime
from typing import Dict
from utils import Colors, print_header, print_score, print_success, print_warning, print_error


def format_report(analysis_results: Dict[str, any], repo_path: str, health_score: int, score_category: str, options: Dict[str, bool] = None, score_breakdown: dict = None, output_format: str = 'text') -> str:
    """
    Format analysis results into a report.

    Args:
        analysis_results: Dictionary containing analysis results
        repo_path: Path to the analyzed repository
        health_score: Calculated health score (0-100)
        score_category: Category of the health score
        options: Dictionary of enabled options
        score_breakdown: Score breakdown dictionary
        output_format: Output format ('text', 'json', 'yaml', 'markdown')

    Returns:
        Formatted report string
    """
    if output_format == 'json':
        import json
        data = {
            'repository': repo_path,
            'analysis_date': datetime.now().isoformat(),
            'health_score': health_score,
            'score_category': score_category,
            'score_breakdown': score_breakdown or {},
            'results': analysis_results
        }
        return json.dumps(data, indent=2, default=str)

    elif output_format == 'yaml':
        try:
            import yaml
            data = {
                'repository': repo_path,
                'analysis_date': datetime.now().isoformat(),
                'health_score': health_score,
                'score_category': score_category,
                'score_breakdown': score_breakdown or {},
                'results': analysis_results
            }
            return yaml.dump(data, default_flow_style=False)
        except ImportError:
            return "YAML format requires PyYAML. Install with: pip install PyYAML"

    elif output_format == 'markdown':
        return format_markdown_report(analysis_results, repo_path, health_score, score_category, options, score_breakdown)

    else:
        return format_text_report(analysis_results, repo_path, health_score, score_category, options, score_breakdown)


def format_markdown_report(analysis_results, repo_path, health_score, score_category, options, score_breakdown) -> str:
    lines = [f"# Git Repository Health Checker\n"]
    lines.append(f"**Repository:** {repo_path}")
    lines.append(f"**Analysis Date:** {datetime.now().isoformat()}")
    lines.append(f"**Health Score:** {health_score}/100 ({score_category})")
    lines.append("")
    if score_breakdown:
        lines.append("## Score Breakdown")
        lines.append("| Category | Score |")
        lines.append("|----------|-------|")
        for cat, score in score_breakdown.items():
            if cat != 'final_score':
                lines.append(f"| {cat.replace('_', ' ').title()} | {score:+d} |")
        lines.append("")
    lines.append("## Analysis Results")
    # Add basic summary
    structure = analysis_results.get('structure', {})
    history = analysis_results.get('history', {})
    lines.append(f"- **Repository Structure:** README: {'✓' if structure.get('has_readme') else '✗'}, LICENSE: {'✓' if structure.get('has_license') else '✗'}, Tests: {'✓' if structure.get('has_tests') else '✗'}")
    lines.append(f"- **Git History:** {history.get('total_commits', 0)} commits")
    if options.get('check_coverage'):
        coverage = analysis_results.get('coverage', {}).get('coverage_stats', {})
        lines.append(f"- **Code Coverage:** {coverage.get('function_coverage_pct', 0)}% functions, {coverage.get('line_coverage_est_pct', 0)}% lines estimated")
    return "\n".join(lines)


def format_text_report(analysis_results: Dict[str, any], repo_path: str, health_score: int, score_category: str, options: Dict[str, bool] = None, score_breakdown: dict = None) -> str:
    if options is None:
        options = {}

    structure = analysis_results.get('structure', {})
    history = analysis_results.get('history', {})
    security = analysis_results.get('security', {})
    language = analysis_results.get('language', {})
    code_quality = analysis_results.get('code_quality', {})
    coverage = analysis_results.get('coverage', {})

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

    # Score breakdown
    if score_breakdown:
        report_lines.append("")
        report_lines.append(f"{Colors.CYAN}📊 SCORE BREAKDOWN:{Colors.RESET}")
        for category, points in score_breakdown.items():
            if category != 'final_score':
                sign = "+" if points > 0 else ""
                color = Colors.GREEN if points > 0 else (Colors.RED if points < 0 else Colors.WHITE)
                report_lines.append(f"  {category.replace('_', ' ').title()}: {color}{sign}{points}{Colors.RESET}")
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
        report_lines.append("    💡 Tip: Create a README.md file describing your project.")

    # LICENSE
    if structure.get('has_license', False):
        report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} LICENSE file")
    else:
        report_lines.append(f"  {Colors.RED}✗{Colors.RESET} LICENSE file")
        report_lines.append("    💡 Tip: Add a LICENSE file (e.g., MIT, Apache) to specify usage rights.")

    # Tests
    if structure.get('has_tests', False):
        report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} Tests directory (tests/ or __tests__/)")
    else:
        report_lines.append(f"  {Colors.RED}✗{Colors.RESET} Tests directory (tests/ or __tests__/)")
        report_lines.append("    💡 Tip: Add tests to ensure code reliability.")

    # .gitignore
    if structure.get('has_gitignore', False):
        report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} .gitignore")
    else:
        report_lines.append(f"  {Colors.RED}✗{Colors.RESET} .gitignore")
        report_lines.append("    💡 Tip: Create a .gitignore file to exclude unwanted files from git.")

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
                if isinstance(warning, dict):
                    report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning['message']}")
                    report_lines.append(f"    💡 Tip: {warning['tip']}")
                else:
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
                if isinstance(warning, dict):
                    report_lines.append(f"  {Colors.RED}⚠{Colors.RESET} {warning['message']}")
                    report_lines.append(f"    💡 Tip: {warning['tip']}")
                else:
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
                if isinstance(warning, dict):
                    report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning['message']}")
                    report_lines.append(f"    💡 Tip: {warning['tip']}")
                else:
                    report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
        else:
            report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} Language-specific checks passed")

    # Code Quality (if enabled)
    if options.get('check_code_quality', False):
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  🔧 CODE QUALITY{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

        code_quality_warnings = code_quality.get('code_quality_warnings', [])
        if code_quality_warnings:
            for warning in code_quality_warnings:
                if isinstance(warning, dict):
                    report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning['message']}")
                    report_lines.append(f"    💡 Tip: {warning['tip']}")
                else:
                    report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
        else:
            report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} Code quality checks passed")

    # Coverage (if enabled)
    if options.get('check_coverage', False):
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}  📊 CODE COVERAGE{Colors.RESET}")
        report_lines.append(f"{Colors.BOLD}{Colors.BLUE}{'-' * 70}{Colors.RESET}")

        stats = coverage.get('coverage_stats', {})
        if stats:
            report_lines.append(f"  📁 Modules Analyzed: {stats.get('total_modules', 0)}")
            report_lines.append(f"  🔧 Total Functions: {stats.get('total_functions', 0)}")
            report_lines.append(f"  ✅ Tested Functions: {stats.get('tested_functions', 0)}")
            report_lines.append(f"  📈 Function Coverage: {Colors.GREEN if stats.get('function_coverage_pct', 0) >= 80 else Colors.YELLOW}{stats.get('function_coverage_pct', 0)}%{Colors.RESET}")
            report_lines.append(f"  📏 Total Lines: {stats.get('total_lines', 0)}")
            report_lines.append(f"  📏 Estimated Covered Lines: {stats.get('estimated_covered_lines', 0)}")
            report_lines.append(f"  📈 Estimated Line Coverage: {Colors.GREEN if stats.get('line_coverage_est_pct', 0) >= 70 else Colors.YELLOW}{stats.get('line_coverage_est_pct', 0)}%{Colors.RESET}")

        coverage_warnings = coverage.get('coverage_warnings', [])
        if coverage_warnings:
            for warning in coverage_warnings:
                if isinstance(warning, dict):
                    report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning['message']}")
                    report_lines.append(f"    💡 Tip: {warning['tip']}")
                else:
                    report_lines.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {warning}")
        else:
            report_lines.append(f"  {Colors.GREEN}✓{Colors.RESET} Code coverage analysis passed")

        report_lines.append("")

    # Footer
    report_lines.append(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")

    return "\n".join(report_lines)


def print_report(report: str, output_format: str = 'text') -> None:
    """
    Print or handle the formatted report.

    Args:
        report: Formatted report string
        output_format: Output format
    """
    print(report)

