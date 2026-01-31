"""
Repository analyzer module.
Analyzes repository structure and git history.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from utils import file_exists, directory_exists, print_progress, print_success, print_warning
import re
import ast
import math
from collections import defaultdict, deque


def analyze_repository_structure(repo_path: str) -> Dict[str, bool]:
    """
    Analyze the repository structure for common files and directories.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Dictionary with analysis results for each check
    """
    results = {
        'has_readme': file_exists(repo_path, 'README.md'),
        'has_license': _check_license_file(repo_path),
        'has_tests': _check_tests_directory(repo_path),
        'has_gitignore': file_exists(repo_path, '.gitignore'),
    }
    
    return results


def _check_license_file(repo_path: str) -> bool:
    """
    Check if a LICENSE file exists (case-insensitive).
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if LICENSE file exists (any case variation)
    """
    repo = Path(repo_path)
    # Check common LICENSE file variations
    license_variations = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'license', 'License']
    
    for license_file in license_variations:
        if (repo / license_file).exists():
            return True
    
    return False


def analyze_commit_quality(commits: list[str]) -> list[str]:
    """
    Analyze commit messages for quality issues.

    Args:
        commits: List of commit lines (oneline format)

    Returns:
        List of warning messages
    """
    warnings = []
    bad_keywords = ['wip', 'fix', 'temp', 'test', 'debug', 'hack']
    very_short_threshold = 10

    for commit in commits:
        if not commit.strip():
            continue
        # Split to get message
        parts = commit.split(' ', 1)
        if len(parts) < 2:
            continue
        message = parts[1].lower()

        # Check for bad keywords
        for keyword in bad_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', message):
                warnings.append({
                    'message': f"Bad commit message: '{commit.strip()}' (contains '{keyword}')",
                    'tip': "Use descriptive commit messages, e.g., 'Add user authentication feature'."
                })

        # Check for very short messages
        if len(message) < very_short_threshold and not message.startswith('merge'):
            warnings.append({
                'message': f"Very short commit message: '{commit.strip()}'",
                'tip': "Write meaningful commit messages explaining what changed and why."
            })

    # Remove duplicates based on message
    seen = set()
    unique_warnings = []
    for w in warnings:
        msg = w['message'] if isinstance(w, dict) else w
        if msg not in seen:
            seen.add(msg)
            unique_warnings.append(w)
    return unique_warnings


def _check_tests_directory(repo_path: str) -> bool:
    """
    Check if a tests directory exists (tests/ or __tests__/).
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if either tests/ or __tests__/ directory exists
    """
    return (directory_exists(repo_path, 'tests') or 
            directory_exists(repo_path, '__tests__'))


def analyze_git_history(repo_path: str, options: Dict[str, bool] = None) -> Dict[str, any]:
    """
    Analyze git history to get commit statistics.

    Args:
        repo_path: Path to the repository
        options: Dictionary of optional checks to enable

    Returns:
        Dictionary with git history analysis results
    """
    if options is None:
        options = {}

    results = {
        'total_commits': 0,
        'most_recent_commit_date': None,
        'commits_quality_warnings': [],
    }

    try:
        # Get total commit count
        commit_count_cmd = ['git', 'rev-list', '--count', 'HEAD']
        commit_count_result = subprocess.run(
            commit_count_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        results['total_commits'] = int(commit_count_result.stdout.strip())

        # Get most recent commit date
        date_cmd = ['git', 'log', '-1', '--format=%ci', 'HEAD']
        date_result = subprocess.run(
            date_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )

        if date_result.stdout.strip():
            # Parse the date string (format: "2024-01-15 10:30:45 -0500")
            date_str = date_result.stdout.strip()
            # Extract just the date and time part (first 19 characters)
            date_part = date_str[:19]
            results['most_recent_commit_date'] = datetime.strptime(
                date_part, '%Y-%m-%d %H:%M:%S'
            )

        if options.get('check_commits', False):
            # Analyze commit messages
            log_cmd = ['git', 'log', '--oneline', '-100']  # Last 100 commits
            log_result = subprocess.run(
                log_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commits = log_result.stdout.strip().split('\n') if log_result.stdout.strip() else []
            results['commits_quality_warnings'] = analyze_commit_quality(commits)

    except subprocess.CalledProcessError as e:
        # If git command fails, return default values
        print(f"Warning: Could not analyze git history: {e}")
    except ValueError as e:
        # If date parsing fails
        print(f"Warning: Could not parse commit date: {e}")
    except Exception as e:
        print(f"Warning: Unexpected error analyzing git history: {e}")

    return results


def analyze_code_quality(repo_path: str) -> Dict[str, any]:
    """
    Analyze code quality (long functions, circular deps, entropy).

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with code quality analysis results
    """
    results = {
        'code_quality_warnings': [],
    }

    language = detect_primary_language(repo_path)

    # Code quality checks
    long_func_warnings = check_long_functions(repo_path, language)
    results['code_quality_warnings'].extend(long_func_warnings)

    circ_dep_warnings = check_circular_dependencies(repo_path, language)
    results['code_quality_warnings'].extend(circ_dep_warnings)

    entropy_warnings = check_high_entropy_strings(repo_path, language)
    results['code_quality_warnings'].extend(entropy_warnings)

    return results


def analyze_code_coverage(repo_path: str) -> Dict[str, any]:
    """Analyze code coverage by estimating test coverage."""
    results = {
        'coverage_warnings': [],
        'coverage_stats': {},
    }

    language = detect_primary_language(repo_path)
    if language != 'python':
        results['coverage_warnings'].append({
            'message': "Code coverage analysis only supported for Python",
            'tip': "Coverage analysis is currently limited to Python projects."
        })
        return results

    repo = Path(repo_path)
    code_files = {}
    test_files = {}

    # Collect all Python files
    for py_file in repo.rglob('*.py'):
        if py_file.is_file():
            relative_path = py_file.relative_to(repo)
            module_name = str(relative_path)[:-3].replace('/', '.').replace('\\', '.')

            # Skip irrelevant files
            if should_skip_for_coverage(relative_path):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                functions = []
                classes = []
                lines_of_code = 0

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                        functions.append(node.name)
                        lines_of_code += node.end_lineno - node.lineno + 1
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)

                if functions or classes:  # Only include files with functionality
                    code_files[module_name] = {
                        'path': relative_path,
                        'functions': functions,
                        'classes': classes,
                        'lines': lines_of_code,
                        'total_lines': sum(1 for line in open(py_file, 'r') if line.strip()),
                    }
            except Exception:
                pass

    # Find test files
    for py_file in repo.rglob('test_*.py'):
        if py_file.is_file():
            relative_path = py_file.relative_to(repo)
            test_module = str(relative_path)[:-3].replace('/', '.').replace('\\', '.')

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                test_functions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                        test_functions.append(node.name)

                if test_functions:
                    # Match to source module: remove 'tests.' prefix and 'test_' prefix
                    source_module = test_module
                    if source_module.startswith('tests.'):
                        source_module = source_module[6:]  # remove 'tests.'
                    source_module = source_module.replace('test_', '').replace('.test_', '.')
                    test_files[source_module] = {
                        'path': relative_path,
                        'test_functions': test_functions,
                    }
            except Exception:
                pass

    # Analyze coverage
    total_functions = 0
    tested_functions = 0
    total_lines = 0
    covered_lines_est = 0

    for module, info in code_files.items():
        total_functions += len(info['functions'])
        total_lines += info['lines']

        if module in test_files:
            # Simple heuristic: assume each test function covers some functions
            test_count = len(test_files[module]['test_functions'])
            # Estimate: each test covers 1-3 functions, but cap at actual functions
            covered_funcs = min(test_count * 2, len(info['functions']))
            tested_functions += covered_funcs
            # Estimate lines covered: assume tested functions are fully covered
            covered_lines_est += (covered_funcs / len(info['functions'])) * info['lines'] if info['functions'] else 0
        else:
            results['coverage_warnings'].append({
                'message': f"No test file found for module '{module}' ({info['path']})",
                'tip': f"Create a test file 'test_{info['path'].stem}.py' with test functions."
            })

    # Calculate percentages
    function_coverage = (tested_functions / total_functions * 100) if total_functions else 0
    line_coverage_est = (covered_lines_est / total_lines * 100) if total_lines else 0

    results['coverage_stats'] = {
        'total_modules': len(code_files),
        'total_functions': total_functions,
        'tested_functions': tested_functions,
        'function_coverage_pct': round(function_coverage, 1),
        'total_lines': total_lines,
        'estimated_covered_lines': round(covered_lines_est),
        'line_coverage_est_pct': round(line_coverage_est, 1),
    }

    # Warnings based on coverage
    if function_coverage < 80:
        results['coverage_warnings'].append({
            'message': f"Low function coverage: {function_coverage:.1f}% ({tested_functions}/{total_functions} functions)",
            'tip': "Aim for at least 80% function coverage. Add more unit tests."
        })

    if line_coverage_est < 70:
        results['coverage_warnings'].append({
            'message': f"Estimated low line coverage: {line_coverage_est:.1f}%",
            'tip': "Consider running actual coverage tools like coverage.py for precise measurement."
        })

    return results


def should_skip_for_coverage(relative_path: Path) -> bool:
    """Determine if a file should be skipped for coverage analysis."""
    path_str = str(relative_path)

    # Skip common non-functional files
    skip_patterns = [
        '__init__.py',  # Often just imports
        'setup.py',
        'conftest.py',
        'manage.py',
        'wsgi.py',
        'asgi.py',
        'urls.py',  # Django-specific
        'admin.py',  # Django-specific
        'apps.py',  # Django-specific
        'models.py',  # Often just data definitions
        'serializers.py',  # DRF-specific
        'migrations/',  # Database migrations
        'tests/',  # Test directories (but we handle test files separately)
    ]

    # Skip test files
    if 'test_' in path_str:
        return True

    for pattern in skip_patterns:
        if pattern in path_str:
            return True

    # Skip if file is very small or empty
    try:
        with open(relative_path, 'r') as f:
            content = f.read().strip()
            if len(content) < 50:  # Very small files
                return True
            tree = ast.parse(content)
            # Skip if only has imports and no functions/classes
            has_code = any(isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) for node in ast.walk(tree))
            if not has_code:
                return True
    except:
        return True

    return False


def analyze_repository(repo_path: str, options: Dict[str, bool] = None, verbose: bool = False, quiet: bool = False) -> Dict[str, any]:
    """
    Perform complete repository analysis.

    Args:
        repo_path: Path to the repository
        options: Dictionary of optional checks to enable

    Returns:
        Dictionary containing all analysis results
    """
    if options is None:
        options = {}

    if not quiet:
        print_progress("🔍 Analyzing repository structure...", "")
    structure = analyze_repository_structure(repo_path)
    if verbose and not quiet:
        print_success("Repository structure analyzed")

    if not quiet:
        print_progress("📊 Analyzing git history...", "")
    history = analyze_git_history(repo_path, options)
    if verbose and not quiet:
        print_success("Git history analyzed")

    results = {
        'structure': structure,
        'history': history,
    }

    if options.get('check_security', False):
        if not quiet:
            print_progress("🔒 Scanning for security issues...", "")
        security = analyze_security(repo_path)
        results['security'] = security
        if verbose and not quiet:
            print_success("Security scan completed")

    if options.get('check_language', False):
        if not quiet:
            print_progress("💻 Analyzing language-specific requirements...", "")
        language = analyze_language_checks(repo_path)
        results['language'] = language
        if verbose and not quiet:
            print_success("Language analysis completed")

    if options.get('check_code_quality', False):
        if not quiet:
            print_progress("🔧 Analyzing code quality...", "")
        code_quality = analyze_code_quality(repo_path)
        results['code_quality'] = code_quality
        if verbose and not quiet:
            print_success("Code quality analysis completed")

    if options.get('check_coverage', False):
        if not quiet:
            print_progress("📊 Analyzing code coverage...", "")
        coverage = analyze_code_coverage(repo_path)
        results['coverage'] = coverage
        if verbose and not quiet:
            print_success("Code coverage analysis completed")

    return results


def check_long_functions(repo_path: str, language: str) -> list:
    """Check for functions longer than 50 lines."""
    warnings = []
    if language != 'python':
        return warnings

    repo = Path(repo_path)
    for py_file in repo.rglob('*.py'):
        if py_file.is_file():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        start_line = node.lineno
                        end_line = node.end_lineno
                        length = end_line - start_line + 1
                        if length > 50:
                            warnings.append({
                                'message': f"Long function '{node.name}' in {py_file.relative_to(repo)}: {length} lines",
                                'tip': "Break down long functions into smaller, more manageable pieces."
                            })
            except Exception:
                pass  # Skip unparseable files
    return warnings


def check_circular_dependencies(repo_path: str, language: str) -> list:
    """Check for circular import dependencies using directed graph."""
    warnings = []
    if language != 'python':
        return warnings

    repo = Path(repo_path)
    import_graph = defaultdict(list)

    # Build directed import graph
    for py_file in repo.rglob('*.py'):
        if py_file.is_file():
            module_name = '.'.join(py_file.relative_to(repo).parts)[:-3]  # Remove .py
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
                for imp in imports:
                    if imp and imp != '__future__':
                        import_graph[module_name].append(imp)
            except Exception:
                pass

    # Detect cycles using DFS on directed graph
    visited = set()
    rec_stack = set()
    cycle_found = False

    def has_cycle(node, path):
        nonlocal cycle_found
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        for neighbor in import_graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, path):
                    return True
            elif neighbor in rec_stack:
                # Cycle found
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                warnings.append({
                    'message': f"Circular dependency detected: {' -> '.join(cycle)}",
                    'tip': "Refactor to break circular imports, e.g., move shared code to a separate module or use dependency injection."
                })
                cycle_found = True
                return True
        path.pop()
        rec_stack.remove(node)
        return False

    for node in import_graph:
        if node not in visited:
            has_cycle(node, [])
            if cycle_found:
                break  # Report one cycle for simplicity

    return warnings


def calculate_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0
    entropy = 0
    length = len(s)
    char_count = defaultdict(int)
    for char in s:
        char_count[char] += 1
    for count in char_count.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def check_high_entropy_strings(repo_path: str, language: str) -> list:
    """Check for high-entropy strings that might be hardcoded credentials."""
    warnings = []
    if language != 'python':
        return warnings

    repo = Path(repo_path)
    # Patterns for potential secrets (variable names)
    secret_patterns = re.compile(r'\b(api_key|apikey|secret|token|password|pwd|key)\b\s*[:=]\s*["\']([^"\']+)["\']', re.IGNORECASE)

    for py_file in repo.rglob('*.py'):
        if py_file.is_file():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                for match in secret_patterns.finditer(content):
                    var_name, value = match.groups()
                    if len(value) > 10:  # Only check longer strings
                        entropy = calculate_entropy(value)
                        if entropy > 4.5:  # High entropy threshold
                            warnings.append({
                                'message': f"High-entropy string detected in {py_file.relative_to(repo)}: variable '{var_name}'",
                                'tip': "Replace hardcoded credentials with environment variables or secure storage."
                            })
            except Exception:
                pass
    return warnings


def analyze_security(repo_path: str) -> Dict[str, any]:
    """
    Perform offline security scan for secrets.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with security analysis results
    """
    results = {
        'secrets_warnings': [],
        'scanned_files': 0,
    }

    repo = Path(repo_path)

    # Files to check for secrets
    suspicious_files = [
        '.env', '.env.local', '.env.production', '.env.staging',
        'config.json', 'config.yml', 'config.yaml',
        'secrets.json', 'secrets.yml', 'secrets.yaml',
        'credentials.json', 'credentials.yml', 'credentials.yaml',
    ]

    # Patterns for secrets
    secret_patterns = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,})["\']?', 'API Key'),
        (r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,})["\']?', 'Secret Key'),
        (r'(?i)(password|pwd)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{8,})["\']?', 'Password'),
        (r'(?i)(token)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{10,})["\']?', 'Token'),
        (r'(?i)(private[_-]?key)\s*[:=]\s*["\']?-----BEGIN.*-----', 'Private Key'),
    ]

    # Check specific files
    for file in suspicious_files:
        file_path = repo / file
        if file_path.exists() and file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    results['scanned_files'] += 1
                    for pattern, desc in secret_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if isinstance(match, tuple):
                                value = match[1] if len(match) > 1 else match[0]
                            else:
                                value = match
                            results['secrets_warnings'].append({
                                'message': f"Potential {desc} in {file}: {value[:10]}...",
                                'tip': "Remove sensitive data from files. Use environment variables or secret management."
                            })
            except Exception as e:
                results['secrets_warnings'].append({
                    'message': f"Error scanning {file}: {str(e)}",
                    'tip': "Check file permissions or content."
                })

    # Check for private keys in common locations
    private_key_files = ['id_rsa', 'id_ed25519', 'private.pem', 'key.pem']
    for key_file in private_key_files:
        key_path = repo / key_file
        if key_path.exists() and key_path.is_file():
            results['secrets_warnings'].append({
                'message': f"Private key file found: {key_file}",
                'tip': "Remove private keys from repository. Use SSH agents or secure key storage."
            })

    return results


def detect_primary_language(repo_path: str) -> str:
    """
    Detect the primary programming language based on file extensions.

    Args:
        repo_path: Path to the repository

    Returns:
        Detected language ('python', 'javascript', 'go', 'unknown')
    """
    repo = Path(repo_path)
    extensions = {'python': ['.py'], 'javascript': ['.js', '.ts', '.jsx', '.tsx'], 'go': ['.go']}

    counts = {'python': 0, 'javascript': 0, 'go': 0}

    for file in repo.rglob('*'):
        if file.is_file():
            ext = file.suffix.lower()
            for lang, exts in extensions.items():
                if ext in exts:
                    counts[lang] += 1

    if counts['python'] > 0 or counts['javascript'] > 0 or counts['go'] > 0:
        return max(counts, key=counts.get)
    return 'unknown'


def analyze_language_checks(repo_path: str) -> Dict[str, any]:
    """
    Analyze language-specific requirements (dependencies, etc.).

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary with language-specific analysis results
    """
    results = {
        'primary_language': 'unknown',
        'language_warnings': [],
    }

    language = detect_primary_language(repo_path)
    results['primary_language'] = language

    if language == 'python':
        # Check for requirements.txt, pyproject.toml, setup.py, and tests
        has_req = file_exists(repo_path, 'requirements.txt')
        has_pyproject = file_exists(repo_path, 'pyproject.toml')
        has_setup = file_exists(repo_path, 'setup.py')
        has_tests = directory_exists(repo_path, 'tests') or directory_exists(repo_path, '__tests__')
        if not has_tests:
            # Check for test files
            repo = Path(repo_path)
            test_files = list(repo.glob('test_*.py'))
            has_tests = len(test_files) > 0

        if not (has_req or has_pyproject or has_setup):
            results['language_warnings'].append({
                'message': "Python project missing dependency file (requirements.txt, pyproject.toml, or setup.py)",
                'tip': "Create a requirements.txt or pyproject.toml file to manage dependencies."
            })
        if not has_tests:
            results['language_warnings'].append({
                'message': "Python project missing tests",
                'tip': "Add test files in a 'tests/' directory or as 'test_*.py' files."
            })

    elif language == 'javascript':
        # Check for package.json, scripts, and node_modules not committed
        has_package = file_exists(repo_path, 'package.json')
        if not has_package:
            results['language_warnings'].append({
                'message': "JavaScript/TypeScript project missing package.json",
                'tip': "Run 'npm init' to create a package.json file."
            })

        # Check if node_modules is committed (bad)
        if directory_exists(repo_path, 'node_modules'):
            results['language_warnings'].append({
                'message': "node_modules directory is committed (should be in .gitignore)",
                'tip': "Add 'node_modules/' to your .gitignore file and remove it from git."
            })

        # Check for scripts in package.json
        if has_package:
            try:
                import json
                with open(Path(repo_path) / 'package.json', 'r') as f:
                    pkg = json.load(f)
                    scripts = pkg.get('scripts', {})
                    if not scripts:
                        results['language_warnings'].append({
                            'message': "package.json has no scripts defined",
                            'tip': "Add scripts to package.json, e.g., 'start', 'test', 'build'."
                        })
            except Exception as e:
                results['language_warnings'].append({
                    'message': f"Error parsing package.json: {str(e)}",
                    'tip': "Ensure package.json is valid JSON."
                })

    elif language == 'go':
        # Check for go.mod, go.sum
        has_go_mod = file_exists(repo_path, 'go.mod')
        has_go_sum = file_exists(repo_path, 'go.sum')

        if not has_go_mod:
            results['language_warnings'].append({
                'message': "Go project missing go.mod",
                'tip': "Run 'go mod init <module_name>' to create go.mod."
            })
        if not has_go_sum:
            results['language_warnings'].append({
                'message': "Go project missing go.sum",
                'tip': "Run 'go mod tidy' to generate go.sum."
            })

    return results

