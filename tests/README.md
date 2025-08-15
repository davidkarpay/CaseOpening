# Case Opening Sheet Manager - Test Suite

This directory contains comprehensive tests for the Case Opening Sheet Manager application.

## Test Structure

```
tests/
├── conftest.py               # Pytest configuration and shared fixtures
├── pytest.ini               # Pytest settings and coverage configuration
├── requirements-test.txt     # Testing dependencies
├── fixtures/                 # Test data and mock objects
│   ├── __init__.py
│   └── sample_data.py       # Sample case data, users, and test cases
├── test_database.py         # Database module tests
├── test_pdf_generator.py    # PDF generation tests
├── test_forms.py            # Form rendering tests
├── test_utils.py            # Utility function tests
├── test_auth.py             # Authentication module tests
├── test_secure_credentials.py # Secure credential management tests
└── test_integration.py      # End-to-end workflow tests
```

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

2. Ensure the main application dependencies are installed:
```bash
pip install -r case-requirements.txt
```

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database.py

# Run specific test
pytest tests/test_database.py::TestCaseDatabase::test_add_case_success
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov-report=html

# View coverage in terminal
pytest --cov-report=term-missing

# Generate XML coverage for CI/CD
pytest --cov-report=xml
```

## Test Categories

### Unit Tests
- **Database Tests** (`test_database.py`): CRUD operations, search functionality, error handling
- **PDF Generator Tests** (`test_pdf_generator.py`): PDF creation, formatting, file handling
- **Forms Tests** (`test_forms.py`): Streamlit form rendering, data validation
- **Utils Tests** (`test_utils.py`): Phone formatting, date parsing, utility functions
- **Auth Tests** (`test_auth.py`): User authentication, PIN verification, JWT tokens
- **Secure Credentials Tests** (`test_secure_credentials.py`): Encryption, credential management

### Integration Tests
- **Workflow Tests** (`test_integration.py`): End-to-end case management workflows
- **Multi-module Integration**: Tests interaction between different modules

## Test Data

The `fixtures/sample_data.py` file contains:
- Sample case data for various scenarios
- User authentication test data
- Phone number formatting test cases
- Date parsing test cases
- Search and filter test scenarios

## Mocking Strategy

Tests use extensive mocking to:
- Isolate units under test
- Avoid file system dependencies
- Mock external services (SMTP, encryption)
- Control Streamlit components

## Coverage Goals

- **Target Coverage**: 80% minimum
- **Critical Modules**: Database, Authentication, PDF Generator should have >90% coverage
- **Exclusions**: UI components, external integrations may have lower coverage

## Running Specific Test Types

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Run only security tests
pytest -m security

# Run slow tests separately
pytest -m slow
```

## CI/CD Integration

This test suite is designed for CI/CD integration:
- Coverage reports in XML format
- JUnit XML test results
- Configurable coverage thresholds
- Support for parallel test execution

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from the project root directory
2. **File Permissions**: Tests create temporary files - ensure write permissions
3. **Missing Dependencies**: Install all test requirements before running

### Debug Mode

```bash
# Run with debug output
pytest -s -v --tb=long

# Run single test with debug
pytest tests/test_database.py::test_specific_function -s -v
```

## Test Development Guidelines

1. **Naming**: Test functions should clearly describe what they test
2. **Independence**: Tests should not depend on other tests
3. **Cleanup**: Use fixtures for setup/teardown
4. **Assertions**: Use descriptive assertion messages
5. **Coverage**: Aim for comprehensive edge case coverage

## Mock Data Guidelines

- Use realistic data that matches production formats
- Include edge cases and invalid data scenarios
- Keep test data updated with schema changes
- Document any special test data requirements