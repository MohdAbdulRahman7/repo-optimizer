import pytest
from scoring import calculate_health_score, get_score_category


def test_calculate_health_score():
    analysis_results = {
        'structure': {'has_readme': True, 'has_license': True, 'has_tests': True, 'has_gitignore': True},
        'history': {'total_commits': 5}
    }
    score, breakdown = calculate_health_score(analysis_results, {})
    assert score == 100
    assert breakdown['final_score'] == 100


def test_get_score_category():
    assert get_score_category(95) == 'Excellent'
    assert get_score_category(25) == 'Critical'