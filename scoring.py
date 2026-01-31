"""
Scoring module for calculating repository health score.
Computes a health score out of 100 based on various checks.
"""

from typing import Dict


def calculate_health_score(analysis_results: Dict[str, any]) -> int:
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
    
    return min(score, 100)  # Cap at 100


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

