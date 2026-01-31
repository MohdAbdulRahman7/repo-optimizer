import pytest
from scoring import calculate_health_score, get_score_category


class TestCalculateHealthScore:
    def test_perfect_score(self):
        analysis_results = {
            'structure': {'has_readme': True, 'has_license': True, 'has_tests': True, 'has_gitignore': True},
            'history': {'total_commits': 10, 'most_recent_commit_date': None},  # Mock recent date if needed
        }
        options = {}

        score, breakdown = calculate_health_score(analysis_results, options)
        assert score == 100
        assert breakdown['final_score'] == 100

    def test_minimum_score(self):
        analysis_results = {
            'structure': {'has_readme': False, 'has_license': False, 'has_tests': False, 'has_gitignore': False},
            'history': {'total_commits': 0, 'most_recent_commit_date': None},
        }
        options = {}

        score, breakdown = calculate_health_score(analysis_results, options)
        assert score == 0
        assert breakdown['final_score'] == 0

    def test_with_warnings(self):
        analysis_results = {
            'structure': {'has_readme': True, 'has_license': True, 'has_tests': True, 'has_gitignore': True},
            'history': {'total_commits': 10, 'commits_quality_warnings': [{'message': 'test', 'tip': 'fix'}]},
        }
        options = {'check_commits': True}

        score, breakdown = calculate_health_score(analysis_results, options)
        assert score < 100
        assert breakdown['commit_quality'] < 0

    def test_code_quality_penalties(self):
        analysis_results = {
            'structure': {'has_readme': True, 'has_license': True, 'has_tests': True, 'has_gitignore': True},
            'history': {'total_commits': 10},
            'code_quality': {'code_quality_warnings': [{'message': 'Long function test', 'tip': 'fix'}]},
        }
        options = {'check_code_quality': True}

        score, breakdown = calculate_health_score(analysis_results, options)
        assert breakdown['code_quality'] < 0

    def test_coverage_penalties(self):
        analysis_results = {
            'structure': {'has_readme': True, 'has_license': True, 'has_tests': True, 'has_gitignore': True},
            'history': {'total_commits': 10},
            'coverage': {'coverage_warnings': [{'message': 'Low coverage', 'tip': 'add tests'}]},
        }
        options = {'check_coverage': True}

        score, breakdown = calculate_health_score(analysis_results, options)
        assert breakdown['coverage'] < 0


class TestGetScoreCategory:
    def test_excellent(self):
        assert get_score_category(95) == "Excellent"

    def test_good(self):
        assert get_score_category(85) == "Good"

    def test_fair(self):
        assert get_score_category(65) == "Fair"

    def test_poor(self):
        assert get_score_category(45) == "Poor"

    def test_critical(self):
        assert get_score_category(25) == "Critical"

    def test_boundary_cases(self):
        assert get_score_category(90) == "Excellent"
        assert get_score_category(70) == "Good"
        assert get_score_category(50) == "Fair"
        assert get_score_category(30) == "Poor"
        assert get_score_category(0) == "Critical"