"""
Syntax validation tests to prevent Python syntax errors
"""
import pytest
import ast
import os
from pathlib import Path
import py_compile
import tempfile


class TestSyntaxValidation:
    """Test Python file syntax validation"""
    
    def get_python_files(self):
        """Get all Python files in the project"""
        project_root = Path(__file__).parent.parent
        python_files = []
        
        # Get main app file
        main_app = project_root / "case-opening-app.py"
        if main_app.exists():
            python_files.append(main_app)
        
        # Get module files
        modules_dir = project_root / "modules"
        if modules_dir.exists():
            python_files.extend(modules_dir.glob("*.py"))
        
        # Get test files
        tests_dir = project_root / "tests"
        if tests_dir.exists():
            python_files.extend(tests_dir.glob("*.py"))
            python_files.extend(tests_dir.glob("**/*.py"))
        
        return python_files
    
    def test_python_syntax_valid(self):
        """Test that all Python files have valid syntax"""
        python_files = self.get_python_files()
        errors = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Parse with AST to check syntax
                ast.parse(source, filename=str(file_path))
                
            except SyntaxError as e:
                errors.append(f"{file_path}: Line {e.lineno} - {e.msg}")
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
        
        if errors:
            pytest.fail(f"Syntax errors found:\\n" + "\\n".join(errors))
    
    def test_python_compilation(self):
        """Test that all Python files can be compiled"""
        python_files = self.get_python_files()
        compilation_errors = []
        
        for file_path in python_files:
            try:
                # Use py_compile to check if file compiles (compile only, don't write)
                py_compile.compile(str(file_path), doraise=True)
                    
            except py_compile.PyCompileError as e:
                compilation_errors.append(f"{file_path}: {str(e)}")
            except Exception as e:
                compilation_errors.append(f"{file_path}: {str(e)}")
        
        if compilation_errors:
            pytest.fail(f"Compilation errors found:\\n" + "\\n".join(compilation_errors))
    
    def test_indentation_consistency(self):
        """Test that files use consistent indentation"""
        python_files = self.get_python_files()
        indentation_errors = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    # Skip empty lines and comments
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#'):
                        continue
                    
                    # Check for mixed tabs and spaces
                    leading = line[:len(line) - len(line.lstrip())]
                    if '\\t' in leading and ' ' in leading:
                        indentation_errors.append(
                            f"{file_path}:{line_num} - Mixed tabs and spaces"
                        )
                
            except Exception as e:
                indentation_errors.append(f"{file_path}: {str(e)}")
        
        if indentation_errors:
            pytest.fail(f"Indentation errors found:\\n" + "\\n".join(indentation_errors))
    
    def test_specific_indentation_patterns(self):
        """Test for specific problematic indentation patterns"""
        python_files = self.get_python_files()
        pattern_errors = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines):
                    # Check for 'with' statements followed by unindented code
                    if line.strip().endswith(':') and 'with ' in line and 'col' in line:
                        # Get the indentation level of the 'with' statement
                        with_indent = len(line) - len(line.lstrip())
                        
                        # Check the next few lines for proper indentation
                        for next_line_idx in range(line_num + 1, min(line_num + 4, len(lines))):
                            next_line = lines[next_line_idx]
                            if next_line.strip() and not next_line.strip().startswith('#'):
                                next_indent = len(next_line) - len(next_line.lstrip())
                                
                                # Content should be more indented than the 'with' statement
                                if next_indent <= with_indent and not next_line.strip().startswith(('with ', 'def ', 'class ', 'if ', 'elif ', 'else', 'try', 'except', 'finally', 'for ', 'while ')):
                                    pattern_errors.append(
                                        f"{file_path}:{next_line_idx + 1} - Possible missing indentation after 'with' statement at line {line_num + 1}"
                                    )
                                break
                
            except Exception as e:
                pattern_errors.append(f"{file_path}: {str(e)}")
        
        if pattern_errors:
            pytest.fail(f"Indentation pattern errors found:\\n" + "\\n".join(pattern_errors))
    
    def test_main_app_specific_syntax(self):
        """Test case-opening-app.py for specific syntax requirements"""
        project_root = Path(__file__).parent.parent
        main_app = project_root / "case-opening-app.py"
        
        if not main_app.exists():
            pytest.skip("Main application file not found")
        
        with open(main_app, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test that the file can be parsed as AST
        try:
            tree = ast.parse(content)
            assert tree is not None
        except SyntaxError as e:
            pytest.fail(f"Syntax error in main app: Line {e.lineno} - {e.msg}")
        
        # Test for specific Streamlit patterns
        lines = content.split('\\n')
        for line_num, line in enumerate(lines):
            # Check for proper 'with col*:' usage specifically
            if 'with col' in line and ':' in line and line.strip().endswith(':'):
                # Get the indentation level of the 'with' statement
                with_indent = len(line) - len(line.lstrip())
                
                # Find the next non-empty, non-comment line
                for next_idx in range(line_num + 1, min(line_num + 5, len(lines))):
                    if next_idx < len(lines):
                        next_line = lines[next_idx]
                        if next_line.strip() and not next_line.strip().startswith('#'):
                            next_indent = len(next_line) - len(next_line.lstrip())
                            
                            # Content should be more indented than the 'with' statement
                            if next_indent <= with_indent and not next_line.strip().startswith(('with ', 'def ', 'class ', '@', 'if __name__')):
                                pytest.fail(
                                    f"Indentation issue at line {next_idx + 1}: "
                                    f"Expected content inside 'with col' block to be indented (got {next_indent} spaces, expected > {with_indent})"
                                )
                            break