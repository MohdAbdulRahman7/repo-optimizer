import pytest
import tempfile
from pathlib import Path
from reporter import format_report, format_text_report, format_markdown_report


class TestFormatReport:
    def test_text_format(self):
        analysis_results = {
            'structure': {'has_readme': True, 'has_license': False, 'has_tests': True, 'has_gitignore': True},
            'history': {'total_commits': 5},
        }
        score_breakdown = {'base_score': 60, 'structure': 35, 'history': 25, 'final_score': 60}

        report = format_report(analysis_results, '/test/repo', 60, 'Fair', {}, score_breakdown, 'text')
        assert 'Git Repository Health Checker' in report
        assert 'Score: 60/100 (Fair)' in report
        assert 'README.md' in report

    def test_json_format(self):
        analysis_results = {'structure': {'has_readme': True}}
        score_breakdown = {'final_score': 20}

        report = format_report(analysis_results, '/test/repo', 20, 'Poor', {}, score_breakdown, 'json')
        assert '"health_score": 20' in report
        assert '"score_category": "Poor"' in report

    def test_markdown_format(self):
        analysis_results = {'structure': {'has_readme': True}}
        score_breakdown = {'final_score': 20}

        report = format_report(analysis_results, '/test/repo', 20, 'Poor', {}, score_breakdown, 'markdown')
        assert '# Git Repository Health Checker' in report
        assert '**Health Score:** 20/100 (Poor)' in report

    def test_yaml_format_missing_library(self):
        analysis_results = {'structure': {'has_readme': True}}
        score_breakdown = {'final_score': 20}

        report = format_report(analysis_results, '/test/repo', 20, 'Poor', {}, score_breakdown, 'yaml')
        assert "YAML format requires PyYAML" in report


class TestFormatTextReport:
    def test_basic_report(self):
        analysis_results = {
            'structure': {'has_readme': True, 'has_license': True, 'has_tests': True, 'has_gitignore': True},
            'history': {'total_commits': 10},
        }
        score_breakdown = {'base_score': 100, 'final_score': 100}

        report = format_text_report(analysis_results, '/test/repo', 100, 'Excellent', {}, score_breakdown)
        assert 'Excellent' in report
        assert 'Score: 100/100' in report


class TestFormatMarkdownReport:
    def test_markdown_output(self):
        analysis_results = {'structure': {'has_readme': True}}
        score_breakdown = {'final_score': 20}

        report = format_markdown_report(analysis_results, '/test/repo', 20, 'Poor', {}, score_breakdown)
        assert '## Score Breakdown' in report
        assert '| Category | Score |' in report