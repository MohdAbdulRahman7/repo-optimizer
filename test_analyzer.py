import pytest
import tempfile
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from analyzer import (
    analyze_repository_structure,
    analyze_git_history,
    analyze_security,
    detect_primary_language,
    analyze_language_checks,
    analyze_code_quality,
    analyze_code_coverage,
    check_long_functions,
    check_circular_dependencies,
    check_high_entropy_strings,
)


@pytest.fixture
def mock_repo():
    """Create a temporary mock repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)

        # Create mock files
        (repo_path / 'README.md').write_text('# Test Repo')
        (repo_path / 'LICENSE').write_text('MIT License')
        (repo_path / 'tests').mkdir()
        (repo_path / 'tests' / '__init__.py').write_text('')
        (repo_path / '.gitignore').write_text('*.pyc\n__pycache__/')
        (repo_path / 'main.py').write_text('print("hello")')
        (repo_path / 'utils.py').write_text('def func(): pass')

        yield str(repo_path)


@pytest.fixture
def empty_repo():
    """Create an empty temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestAnalyzeRepositoryStructure:
    def test_full_structure(self, mock_repo):
        result = analyze_repository_structure(mock_repo)
        assert result['has_readme'] is True
        assert result['has_license'] is True
        assert result['has_tests'] is True
        assert result['has_gitignore'] is True

    def test_missing_files(self, empty_repo):
        result = analyze_repository_structure(empty_repo)
        assert result['has_readme'] is False
        assert result['has_license'] is False
        assert result['has_tests'] is False
        assert result['has_gitignore'] is False


class TestAnalyzeGitHistory:
    @patch('subprocess.run')
    def test_successful_git_history(self, mock_run, mock_repo):
        mock_run.side_effect = [
            MagicMock(stdout='5\n', returncode=0),
            MagicMock(stdout='2024-01-01 12:00:00 +0000\n', returncode=0),
        ]

        result = analyze_git_history(mock_repo)
        assert result['total_commits'] == 5
        assert result['most_recent_commit_date'] is not None

    @patch('subprocess.run')
    def test_git_command_failure(self, mock_run, mock_repo):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')

        result = analyze_git_history(mock_repo)
        assert result['total_commits'] == 0
        assert result['most_recent_commit_date'] is None


class TestAnalyzeSecurity:
    def test_security_scan_with_env(self, mock_repo):
        # Create a mock .env file
        env_file = Path(mock_repo) / '.env'
        env_file.write_text('API_KEY=sk-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890\nPASSWORD=secret123')

        result = analyze_security(mock_repo)
        assert 'secrets_warnings' in result
        assert len(result['secrets_warnings']) > 0
        assert 'API Key' in result['secrets_warnings'][0]

    def test_no_secrets(self, mock_repo):
        result = analyze_security(mock_repo)
        assert len(result['secrets_warnings']) == 0


class TestDetectPrimaryLanguage:
    def test_python_detection(self, mock_repo):
        lang = detect_primary_language(mock_repo)
        assert lang == 'python'

    def test_unknown_language(self, empty_repo):
        lang = detect_primary_language(empty_repo)
        assert lang == 'unknown'


class TestAnalyzeLanguageChecks:
    def test_python_checks(self, mock_repo):
        result = analyze_language_checks(mock_repo)
        assert result['primary_language'] == 'python'
        # Should have warnings for missing requirements.txt
        assert 'language_warnings' in result


class TestCheckLongFunctions:
    def test_long_function_detection(self, mock_repo):
        # Create a file with a long function
        long_file = Path(mock_repo) / 'long.py'
        long_file.write_text('''
def short_func():
    return 1

def long_function():
''' + '\n    pass' * 55 + '''
    return 42
''')

        warnings = check_long_functions(mock_repo, 'python')
        assert len(warnings) > 0
        assert 'long_function' in warnings[0]['message']

    def test_no_long_functions(self, mock_repo):
        warnings = check_long_functions(mock_repo, 'python')
        # main.py and utils.py have short functions
        assert len(warnings) == 0


class TestCheckCircularDependencies:
    def test_no_cycles(self, mock_repo):
        warnings = check_circular_dependencies(mock_repo, 'python')
        assert len(warnings) == 0

    def test_with_cycles(self, mock_repo):
        # Create files with circular imports
        file_a = Path(mock_repo) / 'a.py'
        file_b = Path(mock_repo) / 'b.py'
        file_a.write_text('import b\n')
        file_b.write_text('import a\n')

        warnings = check_circular_dependencies(mock_repo, 'python')
        assert len(warnings) > 0
        assert 'Circular dependency' in warnings[0]['message']


class TestCheckHighEntropyStrings:
    def test_high_entropy_detection(self, mock_repo):
        # Add a file with high entropy string
        secret_file = Path(mock_repo) / 'secrets.py'
        secret_file.write_text('api_key = "sk-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"')

        warnings = check_high_entropy_strings(mock_repo, 'python')
        assert len(warnings) > 0
        assert 'High-entropy' in warnings[0]['message']

    def test_no_high_entropy(self, mock_repo):
        warnings = check_high_entropy_strings(mock_repo, 'python')
        assert len(warnings) == 0


class TestAnalyzeCodeQuality:
    def test_code_quality_analysis(self, mock_repo):
        result = analyze_code_quality(mock_repo)
        assert 'code_quality_warnings' in result
        # May have warnings for long functions or other issues


class TestAnalyzeCodeCoverage:
    def test_coverage_analysis(self, mock_repo):
        result = analyze_code_coverage(mock_repo)
        assert 'coverage_warnings' in result
        assert 'coverage_stats' in result
        # Should warn about missing test files