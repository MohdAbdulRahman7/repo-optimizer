import pytest
from unittest.mock import patch
from main import main


def test_main_basic():
    """Test basic main execution."""
    with patch('main.get_repo_path_and_options', return_value=('./', {})), \
         patch('main.analyze_repository', return_value={}), \
         patch('main.calculate_health_score', return_value=(50, {})), \
         patch('main.get_score_category', return_value='Fair'), \
         patch('main.format_report', return_value='Test Report'), \
         patch('main.print_report'):
        main()


def test_main_with_output():
    """Test main with output file."""
    with patch('main.get_repo_path_and_options', return_value=('./', {'output': 'test.txt'})), \
         patch('main.analyze_repository', return_value={}), \
         patch('main.calculate_health_score', return_value=(50, {})), \
         patch('main.get_score_category', return_value='Fair'), \
         patch('main.format_report', return_value='Test Report'), \
         patch('builtins.open') as mock_open:
        main()
        mock_open.assert_called_once()