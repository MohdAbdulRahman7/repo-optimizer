import pytest
from analyzer import analyze_repository_structure, detect_primary_language


def test_analyze_repository_structure():
    # This would need a mock repo, but for simplicity
    result = analyze_repository_structure('.')
    assert isinstance(result, dict)
    assert 'has_readme' in result


def test_detect_primary_language():
    lang = detect_primary_language('.')
    assert lang in ['python', 'unknown']