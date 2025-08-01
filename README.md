# Case Opening Sheet Manager

A Streamlit web application designed for public defenders to manage case opening sheets with PDF export functionality.

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

## Contributing

Contributions are welcome! Please ensure any modifications maintain the security and privacy features of the application.