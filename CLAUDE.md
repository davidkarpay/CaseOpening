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

### File Structure Issue
**IMPORTANT**: The code expects a `modules/` directory structure but the current implementation has all module files in the root directory with `case-` prefixes. Before running the application, you need to either:

1. Create the expected structure:
   ```bash
   mkdir modules
   touch modules/__init__.py
   mv case-database-module.py modules/database.py
   mv case-forms-module.py modules/forms.py
   mv case-pdf-generator.py modules/pdf_generator.py
   mv case-utils-module.py modules/utils.py
   ```

2. Or update the imports in `case-opening-app.py` to match the current structure:
   ```python
   from case_pdf_generator import generate_case_pdf
   from case_database_module import CaseDatabase
   from case_forms_module import render_defendant_info, render_case_info, render_court_info
   from case_utils_module import format_phone, parse_date
   ```

## Testing and Validation

No specific test framework is configured. Manual testing involves:
1. Running the Streamlit app
2. Testing case creation, editing, and deletion
3. Verifying PDF generation functionality
4. Testing search and export features

## Security Considerations

- All data is stored locally in `data/cases.json`
- No external API calls or cloud connectivity
- Consider encrypting the data directory for sensitive case information
- Regular backups recommended via JSON export functionality