# Case Opening Sheet Manager

[![CI/CD Pipeline](https://github.com/davidkarpay/CaseOpening/actions/workflows/ci.yml/badge.svg)](https://github.com/davidkarpay/CaseOpening/actions/workflows/ci.yml)
[![Security Scanning](https://github.com/davidkarpay/CaseOpening/actions/workflows/security.yml/badge.svg)](https://github.com/davidkarpay/CaseOpening/actions/workflows/security.yml)
[![Code Quality](https://github.com/davidkarpay/CaseOpening/actions/workflows/code-quality.yml/badge.svg)](https://github.com/davidkarpay/CaseOpening/actions/workflows/code-quality.yml)
[![codecov](https://codecov.io/gh/davidkarpay/CaseOpening/branch/master/graph/badge.svg)](https://codecov.io/gh/davidkarpay/CaseOpening)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0+-red.svg)](https://streamlit.io/)

A Streamlit web application designed for public defenders to manage case opening sheets with PDF export functionality.

🚀 **[Live Demo](https://caseopeninggit-nmtak66hzexfgyxzcxa38b.streamlit.app/)**

## Overview

This application provides a comprehensive case management system that allows public defenders to:
- Create and manage defendant case information
- Track court dates and case details
- Generate professional PDF case opening sheets
- Search and filter cases
- Export data for reporting

## Features

- **Complete Case Management**: Store all case opening sheet information in a searchable JSON database
- **PDF Generation**: Create properly formatted PDFs matching official case opening sheet layouts
- **Search & Filter**: Quickly find cases by name, case number, or other criteria
- **Edit & Update**: Modify existing cases with full history tracking
- **Secure Local Storage**: All data stored locally for privacy and security

## Installation

1. Clone the repository:
```bash
git clone https://github.com/davidkarpay/CaseOpening.git
cd CaseOpening
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r case-requirements.txt
```

## Usage

Run the Streamlit application:
```bash
streamlit run case-opening-app.py
```

The application will open in your web browser at `http://localhost:8501`

### Basic Operations

1. **Creating a New Case**: Click "➕ New Case" in the sidebar
2. **Finding Cases**: Use the search box to filter by name or case number
3. **Editing a Case**: Click on any case in the sidebar to load it for editing
4. **Generating PDFs**: Save the case first, then a PDF is automatically generated
5. **Exporting Data**: Use "Export All Cases (JSON)" to backup your database

## Project Structure

```
case-opening-sheet/
│
├── case-opening-app.py     # Main Streamlit application
├── case-requirements.txt   # Python dependencies
│
├── modules/                # Application modules
│   ├── __init__.py        # Python package marker
│   ├── database.py        # JSON database management
│   ├── forms.py           # Form rendering components
│   ├── pdf_generator.py   # PDF generation
│   └── utils.py           # Utility functions
│
├── data/                  # Database storage (created automatically)
│   └── cases.json        # JSON database file
│
└── exports/              # Export directory (created automatically)
    └── pdfs/            # Generated PDFs
```

## Data Structure

Cases are stored with comprehensive fields including:
- Defendant information (name, DOB, address, contact)
- Case details (number, charges, type)
- Court information (dates, division, actions)
- Status flags (custody, probation, veteran, etc.)
- Notes and disposition information

## Security Notes

- All data is stored locally in `data/cases.json`
- No cloud connectivity or external API calls
- The `.gitignore` file excludes sensitive data directories
- Regular backups recommended via JSON export functionality

## Requirements

- Python 3.8+
- Streamlit 1.29.0+
- ReportLab 4.0.7+
- Pandas 2.1.4+

## License

This project is intended for use by public defenders and legal aid organizations. Please ensure compliance with your jurisdiction's data privacy requirements when handling case information.

## Deployment

### Deploy to Streamlit Community Cloud (Free)

1. Fork this repository to your GitHub account
2. Sign up for free at [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Click "New app" and select your forked repository
4. Set the main file path to `case-opening-app.py`
5. Click "Deploy"

Your app will be available at `https://[your-username]-caseopening-case-opening-app-[random].streamlit.app/`

### Alternative Deployment Options

- **Heroku**: Add a `Procfile` with `web: sh setup.sh && streamlit run case-opening-app.py`
- **Railway**: Connect your GitHub repo and it will auto-detect Streamlit
- **Render**: Use their web service with a Docker container

## Testing

This project includes comprehensive testing with pytest:

### Running Tests

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov=case-opening-app

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m security      # Security tests only
```

### Test Coverage

The project maintains high test coverage with automated reporting:
- **Target Coverage**: 80% minimum
- **Critical Modules**: Database, Authentication, PDF Generator (>90% coverage)
- **Coverage Reports**: Available in HTML format after running tests

### Continuous Integration

All code changes are automatically tested through GitHub Actions:
- ✅ **Unit & Integration Tests** across Python 3.9, 3.10, 3.11
- ✅ **Security Scanning** with Bandit, Safety, and Semgrep
- ✅ **Code Quality** checks with flake8, mypy, and pylint
- ✅ **Dependency Scanning** for vulnerabilities
- ✅ **Performance Testing** for database operations

## Development Workflow

### Setting Up for Development

1. **Clone and setup:**
   ```bash
   git clone https://github.com/davidkarpay/CaseOpening.git
   cd CaseOpening
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r case-requirements.txt
   pip install -r tests/requirements-test.txt
   ```

2. **Run tests before making changes:**
   ```bash
   pytest
   ```

3. **Make your changes and test:**
   ```bash
   # Run specific tests
   pytest tests/test_database.py -v
   
   # Check code quality
   flake8 modules/ case-opening-app.py
   ```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the full test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

All PRs must:
- ✅ Pass all automated tests
- ✅ Include appropriate test coverage
- ✅ Pass security scans
- ✅ Follow code quality standards

### Code Quality Standards

- **Linting**: flake8 for code style
- **Type Checking**: mypy for type safety
- **Security**: Bandit for security issues
- **Testing**: pytest with >80% coverage
- **Documentation**: Clear docstrings and comments

## CI/CD Pipeline

### Automated Workflows

- **🔄 CI/CD Pipeline** (`.github/workflows/ci.yml`)
  - Runs on push/PR to main branches
  - Tests across Python 3.9, 3.10, 3.11
  - Generates coverage reports
  - Uploads artifacts

- **🔒 Security Scanning** (`.github/workflows/security.yml`)
  - Daily dependency vulnerability scans
  - Code security analysis
  - License compliance checking
  - PII/sensitive data detection

- **📊 Code Quality** (`.github/workflows/code-quality.yml`)
  - Linting and formatting checks
  - Complexity analysis
  - Documentation coverage
  - Performance benchmarks

- **🚀 Deployment** (`.github/workflows/deploy.yml`)
  - Automated deployment to Streamlit Cloud
  - Release management
  - Production health checks

- **📦 Release Management** (`.github/workflows/release.yml`)
  - Semantic versioning
  - Automated changelog generation
  - GitHub releases with artifacts

### Dependency Management

- **🤖 Dependabot** automatically creates PRs for dependency updates
- **Weekly updates** for Python packages and GitHub Actions
- **Security patches** are prioritized and auto-merged when safe
- **Grouped updates** for related packages (testing, security, etc.)

## Contributing

Contributions are welcome! Please ensure any modifications maintain the security and privacy features of the application.

### Issue Templates

Use the appropriate issue template:
- 🐛 **Bug Report**: For reporting bugs
- ✨ **Feature Request**: For suggesting new features
- ❓ **Question**: For asking questions
- 🔒 **Security Issue**: For reporting security vulnerabilities (private)

### Security

For security vulnerabilities, please:
1. **DO NOT** create a public issue
2. Email dkarpay@pd15.org with subject "SECURITY: Case Opening Manager"
3. Include details about the vulnerability
4. Allow time for a fix before public disclosure