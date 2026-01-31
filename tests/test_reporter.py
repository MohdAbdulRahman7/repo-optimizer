import pytest
from reporter import format_report


def test_format_report_text():
    analysis_results = {'structure': {'has_readme': True}}
    report = format_report(analysis_results, '.', 20, 'Poor', {}, {}, 'text')
    assert 'Git Repository Health Checker' in report


def test_format_report_json():
    analysis_results = {'structure': {'has_readme': True}}
    report = format_report(analysis_results, '.', 20, 'Poor', {}, {}, 'json')
    assert '"health_score": 20' in report


def test_format_report_markdown():
    analysis_results = {'structure': {'has_readme': True}}
    report = format_report(analysis_results, '.', 20, 'Poor', {}, {}, 'markdown')
    assert '# Git Repository Health Checker' in report