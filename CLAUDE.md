# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Case Opening Sheet Manager** - a Streamlit web application designed for public defenders to manage case opening sheets with PDF export functionality. The application stores case data locally in JSON format and generates properly formatted PDFs matching case opening sheet layouts.

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **case-opening-app.py**: Main Streamlit application orchestrating the UI and business logic
- **case-database-module.py**: JSON-based database management (`CaseDatabase` class)
- **case-forms-module.py**: Form rendering components for different case information sections
- **case-pdf-generator.py**: PDF generation using ReportLab for formatted case documents
- **case-utils-module.py**: Utility functions for data formatting and validation

The application uses session state to manage current case data and edit modes, with automatic directory creation for data storage (`data/`) and PDF exports (`exports/pdfs/`).

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r case-requirements.txt
```

### Running the Application
```bash
# Start the Streamlit application
streamlit run case-opening-app.py
```

### Dependencies
- `streamlit>=1.29.0`: Web application framework
- `reportlab>=4.0.7`: PDF generation
- `pandas>=2.1.4`: Data manipulation
- `pathlib`: File path handling (built-in)

## Key Implementation Details

### Data Structure
Cases are stored as JSON objects with comprehensive fields including defendant information, case details, court information, and status flags. Each case gets a UUID and timestamp metadata.

### Module Dependencies
The main app imports from modules using relative paths:
- `from modules.pdf_generator import generate_case_pdf`
- `from modules.database import CaseDatabase`
- `from modules.forms import render_defendant_info, render_case_info, render_court_info`
- `from modules.utils import format_phone, parse_date`

### State Management
Uses Streamlit session state for:
- `current_case`: Active case data being edited
- `edit_mode`: Boolean flag for edit vs. new case mode
- `selected_case_id`: ID of currently selected case

### Module Structure
The application uses a clean `modules/` directory structure:
- `modules/database.py`: CaseDatabase class for JSON-based data management
- `modules/forms.py`: Streamlit form rendering components
- `modules/pdf_generator.py`: PDF generation using ReportLab
- `modules/utils.py`: Utility functions for data formatting and validation
- `modules/auth.py`: Authentication and user management
- `modules/auth_ui.py`: Authentication UI components
- `modules/secure_credentials.py`: Encrypted credential management
- `modules/settings_page.py`: Application settings interface

## Testing and Validation

The project includes comprehensive automated testing with pytest:

### Test Framework
- **pytest**: Test runner with fixtures and parameterized testing
- **Coverage**: 80% minimum coverage requirement with HTML reports
- **Mocking**: Extensive use of unittest.mock for external dependencies
- **Integration**: End-to-end workflow testing

### Running Tests
```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov=case-opening-app

# Run specific test categories
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m security      # Security tests
```

### Test Categories
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Module interaction and workflow testing  
- **Security Tests**: Authentication and data protection testing
- **Performance Tests**: Database and PDF generation benchmarks

### Continuous Integration
All tests run automatically via GitHub Actions on:
- Pull requests to main branches
- Pushes to master/main branches
- Daily security scans

## Security Considerations

- All data is stored locally in `data/cases.json`
- No external API calls or cloud connectivity
- Consider encrypting the data directory for sensitive case information
- Regular backups recommended via JSON export functionality