import pytest
from unittest.mock import patch
from cli import parse_arguments, get_repo_path_and_options


class TestParseArguments:
    def test_default_arguments(self):
        with patch('sys.argv', ['main.py']):
            args = parse_arguments()
            assert args.repo_path == '.'
            assert args.check_commits is False
            assert args.check_security is False
            assert args.check_language is False
            assert args.check_code_quality is False
            assert args.check_coverage is False
            assert args.verbose is False
            assert args.quiet is False
            assert args.format == 'text'
            assert args.output is None

    def test_all_flags_enabled(self):
        with patch('sys.argv', ['main.py', '--check-commits', '--check-security', '--check-language', '--check-code-quality', '--check-coverage', '--verbose', '--format', 'json', '--output', 'report.json']):
            args = parse_arguments()
            assert args.check_commits is True
            assert args.check_security is True
            assert args.check_language is True
            assert args.check_code_quality is True
            assert args.check_coverage is True
            assert args.verbose is True
            assert args.quiet is False
            assert args.format == 'json'
            assert args.output == 'report.json'

    def test_quiet_mode(self):
        with patch('sys.argv', ['main.py', '--quiet']):
            args = parse_arguments()
            assert args.quiet is True

    def test_invalid_format(self):
        with patch('sys.argv', ['main.py', '--format', 'invalid']):
            with pytest.raises(SystemExit):
                parse_arguments()

    def test_custom_repo_path(self):
        with patch('sys.argv', ['main.py', '/path/to/repo']):
            args = parse_arguments()
            assert args.repo_path == '/path/to/repo'


class TestGetRepoPathAndOptions:
    @patch('cli.validate_repo_path')
    def test_valid_repo(self, mock_validate, mock_repo_with_git):
        mock_validate.return_value = mock_repo_with_git

        with patch('sys.argv', ['main.py']):
            repo_path, options = get_repo_path_and_options()

            assert repo_path == mock_repo_with_git
            assert options['check_commits'] is True  # Default all enabled
            assert options['check_security'] is True
            assert options['check_language'] is True
            assert options['check_code_quality'] is True
            assert options['check_coverage'] is True
            assert options['verbose'] is False
            assert options['quiet'] is False
            assert options['format'] == 'text'
            assert options['output'] is None

    @patch('cli.validate_repo_path')
    def test_invalid_repo(self, mock_validate):
        mock_validate.side_effect = ValueError("Invalid repo")

        with patch('sys.argv', ['main.py']):
            with pytest.raises(SystemExit):
                get_repo_path_and_options()

    @patch('cli.validate_repo_path')
    def test_specific_checks_enabled(self, mock_validate, mock_repo_with_git):
        mock_validate.return_value = mock_repo_with_git

        with patch('sys.argv', ['main.py', '--check-commits']):
            repo_path, options = get_repo_path_and_options()

            assert options['check_commits'] is True
            assert options['check_security'] is False  # Others disabled
            assert options['check_language'] is False
            assert options['check_code_quality'] is False
            assert options['check_coverage'] is False


@pytest.fixture
def mock_repo_with_git():
    """Mock repo path."""
    return '/mock/repo/path'