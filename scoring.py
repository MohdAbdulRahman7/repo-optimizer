"""
Scoring module for calculating repository health score.
Computes a health score out of 100 based on various checks.
"""

from typing import Dict


def calculate_health_score(analysis_results: Dict[str, any], options: Dict[str, bool] = None) -> tuple[int, dict]:
    """
    Calculate a health score out of 100 based on analysis results.

    Returns:
        Tuple of (final_score, breakdown_dict)
    """
    if options is None:
        options = {}

    breakdown = {
        'base_score': 0,
        'structure': 0,
        'history': 0,
        'commit_quality': 0,
        'security': 0,
        'language_specific': 0,
        'code_quality': 0,
        'coverage': 0
    }

    score = 0
    structure = analysis_results.get('structure', {})
    history = analysis_results.get('history', {})
    security = analysis_results.get('security', {})
    language = analysis_results.get('language', {})

    # File and directory checks (70 points total)
    if structure.get('has_readme', False):
        score += 20
        breakdown['structure'] += 20

    if structure.get('has_license', False):
        score += 15
        breakdown['structure'] += 15

    if structure.get('has_tests', False):
        score += 25
        breakdown['structure'] += 25

    if structure.get('has_gitignore', False):
        score += 15
        breakdown['structure'] += 15

    # Git history checks (30 points total)
    total_commits = history.get('total_commits', 0)
    if total_commits > 0:
        score += 15  # At least one commit
        breakdown['history'] += 15

    # Check for recent activity (commit in last 6 months)
    most_recent_date = history.get('most_recent_commit_date')
    if most_recent_date:
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        if most_recent_date >= six_months_ago:
            score += 10
            breakdown['history'] += 10

    breakdown['base_score'] = score

    # Optional checks - penalties for issues
    if options.get('check_commits', False):
        commit_warnings = history.get('commits_quality_warnings', [])
        penalty = min(len(commit_warnings) * 10, 30)
        score -= penalty
        breakdown['commit_quality'] = -penalty

    if options.get('check_security', False):
        secrets_warnings = security.get('secrets_warnings', [])
        penalty = min(len(secrets_warnings) * 20, 50)
        score -= penalty
        breakdown['security'] = -penalty

    if options.get('check_language', False):
        language_warnings = language.get('language_warnings', [])
        other_lang_count = len(language_warnings)
        other_penalty = min(other_lang_count * 10, 30)
        breakdown['language_specific'] = -other_penalty
        score -= other_penalty

    if options.get('check_code_quality', False):
        code_quality_warnings = analysis_results.get('code_quality', {}).get('code_quality_warnings', [])
        # Separate penalties for different types
        long_func_count = sum(1 for w in code_quality_warnings if 'Long function' in w.get('message', ''))
        circ_dep_count = sum(1 for w in code_quality_warnings if 'Circular dependency' in w.get('message', ''))
        entropy_count = sum(1 for w in code_quality_warnings if 'High-entropy' in w.get('message', ''))

        long_penalty = min(long_func_count * 5, 20)
        circ_penalty = min(circ_dep_count * 15, 30)
        entropy_penalty = min(entropy_count * 20, 40)

        breakdown['code_quality'] = -(long_penalty + circ_penalty + entropy_penalty)
        score -= (long_penalty + circ_penalty + entropy_penalty)

    if options.get('check_coverage', False):
        coverage_warnings = analysis_results.get('coverage', {}).get('coverage_warnings', [])
        coverage_penalty = min(len(coverage_warnings) * 15, 45)  # -15 per warning, max -45
        breakdown['coverage'] = -coverage_penalty
        score -= coverage_penalty

    final_score = max(score, 0)
    breakdown['final_score'] = final_score
    return final_score, breakdown


def get_score_category(score: int) -> str:
    """
    Get a human-readable category for the health score.

    Args:
        score: Health score (0-100)

    Returns:
        Category string (Excellent, Good, Fair, Poor, Critical)
    """
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score >= 30:
        return "Poor"
    else:
        return "Critical"

