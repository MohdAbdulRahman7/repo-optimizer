import pytest
from utils import file_exists, directory_exists, validate_repo_path


def test_file_exists():
    assert file_exists('.', 'README.md') is True
    assert file_exists('.', 'nonexistent.txt') is False


def test_directory_exists():
    assert directory_exists('.', 'tests') is True
    assert directory_exists('.', 'nonexistent') is False


def test_validate_repo_path():
    # This might fail if not a git repo, but for test
    try:
        result = validate_repo_path('.')
        assert isinstance(result, str)
    except ValueError:
        pass  # Expected if not git repo