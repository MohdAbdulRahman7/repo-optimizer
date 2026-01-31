import pytest
from unittest.mock import patch
from cli import parse_arguments, get_repo_path_and_options


def test_parse_arguments_default():
    with patch('sys.argv', ['main.py']):
        args = parse_arguments()
        assert args.repo_path == '.'
        assert args.format == 'text'


def test_get_repo_path_and_options():
    with patch('cli.validate_repo_path', return_value='/test/repo'), \
         patch('sys.argv', ['main.py']):
        path, options = get_repo_path_and_options()
        assert path == '/test/repo'
        assert options['check_commits'] is True