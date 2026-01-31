import pytest
import tempfile
import os
from pathlib import Path
from utils import is_git_repository, validate_repo_path, file_exists, directory_exists


class TestIsGitRepository:
    def test_git_repo(self, mock_repo_with_git):
        assert is_git_repository(mock_repo_with_git) is True

    def test_non_git_repo(self, tmp_path):
        assert is_git_repository(str(tmp_path)) is False


class TestValidateRepoPath:
    def test_valid_repo(self, mock_repo_with_git):
        result = validate_repo_path(mock_repo_with_git)
        assert result == mock_repo_with_git

    def test_nonexistent_path(self):
        with pytest.raises(ValueError, match="Path does not exist"):
            validate_repo_path('/nonexistent/path')

    def test_non_directory(self, tmp_path):
        file_path = tmp_path / 'file.txt'
        file_path.write_text('test')
        with pytest.raises(ValueError, match="Path is not a directory"):
            validate_repo_path(str(file_path))

    def test_non_git_directory(self, tmp_path):
        with pytest.raises(ValueError, match="Path is not a git repository"):
            validate_repo_path(str(tmp_path))


class TestFileExists:
    def test_existing_file(self, tmp_path):
        file_path = tmp_path / 'test.txt'
        file_path.write_text('content')
        assert file_exists(str(tmp_path), 'test.txt') is True

    def test_nonexistent_file(self, tmp_path):
        assert file_exists(str(tmp_path), 'nonexistent.txt') is False

    def test_directory_not_file(self, tmp_path):
        subdir = tmp_path / 'subdir'
        subdir.mkdir()
        assert file_exists(str(tmp_path), 'subdir') is False


class TestDirectoryExists:
    def test_existing_directory(self, tmp_path):
        subdir = tmp_path / 'subdir'
        subdir.mkdir()
        assert directory_exists(str(tmp_path), 'subdir') is True

    def test_nonexistent_directory(self, tmp_path):
        assert directory_exists(str(tmp_path), 'nonexistent') is False

    def test_file_not_directory(self, tmp_path):
        file_path = tmp_path / 'file.txt'
        file_path.write_text('content')
        assert directory_exists(str(tmp_path), 'file.txt') is False


@pytest.fixture
def mock_repo_with_git():
    """Create a temporary directory with .git initialized."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)
        git_dir = repo_path / '.git'
        git_dir.mkdir()

        # Create some basic git files
        (git_dir / 'HEAD').write_text('ref: refs/heads/main\n')
        (git_dir / 'config').write_text('[core]\n\trepositoryformatversion = 0\n')

        yield str(repo_path)