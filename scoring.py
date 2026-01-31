"""
Scoring module for calculating repository health score.
Computes a health score out of 100 based on various checks.
"""

from typing import Dict


def calculate_health_score(analysis_results: Dict[str, any], args) -> int:
    """
    Calculate a health score out of 100 based on analysis results.
    
    Scoring breakdown:
    - README.md: 20 points
    - LICENSE file: 15 points
    - Tests directory: 25 points
    - .gitignore: 15 points
    - Git history (at least 1 commit): 15 points
    - Recent activity (commit in last 6 months): 10 points
    
    Args:
        analysis_results: Dictionary containing analysis results
        
    Returns:
        Health score from 0 to 100
    """
    score = 0
    structure = analysis_results.get('structure', {})
    history = analysis_results.get('history', {})
    
    # File and directory checks (70 points total)
    if structure.get('has_readme', False):
        score += 20
    
    if structure.get('has_license', False):
        score += 15
    
    if structure.get('has_tests', False):
        score += 25
    
    if structure.get('has_gitignore', False):
        score += 15
    
    # Git history checks (30 points total)
    total_commits = history.get('total_commits', 0)
    if total_commits > 0:
        score += 15  # At least one commit
    
    # Check for recent activity (commit in last 6 months)
    most_recent_date = history.get('most_recent_commit_date')
    if most_recent_date:
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        if most_recent_date >= six_months_ago:
            score += 10

    # Commit quality checks (if enabled)
    if args.check_commits:
        bad_messages = history.get('bad_commit_messages', 0)
        short_commits = history.get('short_commits', 0)
        # Deduct 2 points per bad message/short commit, max 20
        penalty = min((bad_messages + short_commits) * 2, 20)
        score -= penalty

    # Security checks (if enabled)
    if args.check_security:
        security = analysis_results.get('security', {})
        if security.get('has_env_files', False):
            score -= 10  # Deduct for having .env files (potential risk)
        potential_secrets = len(security.get('potential_secrets', []))
        score -= min(potential_secrets * 5, 20)  # Deduct for potential secrets

    # Language-specific checks (if enabled)
    if args.check_language:
        language = analysis_results.get('language', {})
        lang_checks = language.get('language_checks', {})
        if language.get('primary_language') == 'Python':
            if lang_checks.get('has_requirements', False) or lang_checks.get('has_pyproject', False):
                score += 10
            if lang_checks.get('has_tests', False):
                score += 5  # Additional for tests
        elif language.get('primary_language') == 'JavaScript/TypeScript':
            if lang_checks.get('has_package_json', False):
                score += 10
            if lang_checks.get('has_scripts_in_package', False):
                score += 5
            if lang_checks.get('node_modules_committed', False):
                score -= 15  # Deduct for committed node_modules
        elif language.get('primary_language') == 'Go':
            if lang_checks.get('has_go_mod', False):
                score += 10
            if lang_checks.get('has_go_sum', False):
                score += 5

    return max(score, 0)  # Floor at 0


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

