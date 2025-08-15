# Contributing to Case Opening Sheet Manager

Thank you for your interest in contributing to the Case Opening Sheet Manager! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Code Quality Standards](#code-quality-standards)
- [Security Guidelines](#security-guidelines)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. By participating, you agree to:

- Be respectful and professional in all interactions
- Focus on constructive feedback and collaboration
- Respect privacy and confidentiality requirements for legal software
- Follow all security and data protection guidelines

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git for version control
- Familiarity with Streamlit framework
- Understanding of legal case management workflows (helpful but not required)

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/CaseOpening.git
   cd CaseOpening
   ```

2. **Set up development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r case-requirements.txt
   pip install -r tests/requirements-test.txt
   ```

3. **Verify setup:**
   ```bash
   pytest
   streamlit run case-opening-app.py
   ```

## Development Workflow

### Branch Strategy

- **`master`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/feature-name`**: Individual feature development
- **`hotfix/fix-description`**: Critical production fixes

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   pytest
   flake8 modules/ case-opening-app.py
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

### Commit Message Guidelines

Use conventional commit format:
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `test:` test additions/modifications
- `refactor:` code refactoring
- `security:` security improvements
- `ci:` CI/CD changes

## Testing Guidelines

### Test Requirements

All contributions must include appropriate tests:

- **Unit tests** for individual functions/methods
- **Integration tests** for feature workflows
- **Security tests** for authentication/data handling
- **Performance tests** for database operations

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m security

# Run with coverage
pytest --cov=modules --cov=case-opening-app --cov-report=html

# Run specific test file
pytest tests/test_database.py -v
```

### Writing Tests

1. **Follow existing test patterns:**
   ```python
   def test_function_name_scenario():
       # Arrange
       setup_data = create_test_data()
       
       # Act
       result = function_under_test(setup_data)
       
       # Assert
       assert result == expected_value
   ```

2. **Use fixtures for common setup:**
   ```python
   @pytest.fixture
   def sample_case_data():
       return {"name": "Test Case", "number": "123"}
   
   def test_with_fixture(sample_case_data):
       assert sample_case_data["name"] == "Test Case"
   ```

3. **Mock external dependencies:**
   ```python
   @patch('modules.pdf_generator.SimpleDocTemplate')
   def test_pdf_generation(mock_doc):
       # Test without actually creating PDF files
   ```

### Test Coverage Requirements

- **Minimum overall coverage**: 80%
- **Critical modules**: >90% coverage
- **New code**: 100% coverage required
- **Security functions**: 100% coverage required

## Code Quality Standards

### Python Style Guidelines

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear, descriptive variable names
- Keep functions focused and small
- Add docstrings to all public functions

### Code Formatting

```bash
# Check formatting
black --check modules/ case-opening-app.py tests/

# Apply formatting
black modules/ case-opening-app.py tests/

# Sort imports
isort modules/ case-opening-app.py tests/
```

### Linting

```bash
# Run all linting checks
flake8 modules/ case-opening-app.py
pylint modules/ case-opening-app.py
mypy modules/ case-opening-app.py --ignore-missing-imports
```

### Documentation

- Add docstrings to all public functions
- Update README.md for new features
- Include inline comments for complex logic
- Document any security considerations

## Security Guidelines

### Data Protection

- **Never commit real case data** or PII
- Use placeholder data in tests and examples
- Implement proper data validation and sanitization
- Follow secure coding practices

### Authentication & Authorization

- Test all authentication flows thoroughly
- Validate input data to prevent injection attacks
- Use secure session management
- Implement proper error handling

### Dependency Security

- Regularly update dependencies
- Review security advisories
- Use `safety check` and `bandit` for security scanning
- Document any security implications of new dependencies

## Submitting Changes

### Pull Request Process

1. **Create a descriptive PR title:**
   ```
   feat: add case search functionality with advanced filters
   fix: resolve PDF generation error for special characters
   ```

2. **Fill out the PR template completely:**
   - Description of changes
   - Type of change
   - Testing performed
   - Security considerations
   - Breaking changes (if any)

3. **Ensure all checks pass:**
   - ✅ All tests pass
   - ✅ Code quality checks pass
   - ✅ Security scans pass
   - ✅ Coverage requirements met

4. **Respond to review feedback:**
   - Address all reviewer comments
   - Update tests as needed
   - Maintain clean commit history

### Review Criteria

PRs will be reviewed for:
- **Functionality**: Does it work as intended?
- **Testing**: Adequate test coverage and quality
- **Security**: No security vulnerabilities introduced
- **Performance**: No significant performance regressions
- **Code Quality**: Follows project standards
- **Documentation**: Appropriate documentation updates

## Issue Guidelines

### Reporting Bugs

Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment information
- Error messages or logs
- Screenshots if applicable

### Feature Requests

Use the feature request template and include:
- Clear problem statement
- Proposed solution
- Use cases and user stories
- Implementation considerations
- Priority and impact assessment

### Security Issues

**DO NOT create public issues for security vulnerabilities!**

Instead:
1. Email dkarpay@pd15.org with subject "SECURITY: Case Opening Manager"
2. Include detailed information about the vulnerability
3. Allow time for assessment and fix before disclosure

### Questions

Use the question template for:
- Usage questions
- Configuration help
- Best practices
- Integration guidance

## Additional Resources

### Documentation

- [README.md](README.md) - Project overview and setup
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- [AUTH_SETUP.md](AUTH_SETUP.md) - Authentication setup
- [tests/README.md](tests/README.md) - Testing documentation

### Tools and Links

- [Streamlit Documentation](https://docs.streamlit.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Security Guidelines](https://bandit.readthedocs.io/)

### Getting Help

- Create a GitHub issue with the question template
- Email maintainers for security concerns
- Review existing issues and documentation first

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation (with permission)

Thank you for contributing to the Case Opening Sheet Manager! Your contributions help improve case management for public defenders and legal aid organizations.