# Case Opening Sheet Manager - Setup Instructions

## Project Structure

Create the following folder structure:

```
case-opening-sheet/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
│
├── modules/               # Application modules
│   ├── __init__.py       # Empty file to make it a package
│   ├── database.py       # JSON database management
│   ├── forms.py          # Form rendering components
│   ├── pdf_generator.py  # PDF generation
│   └── utils.py          # Utility functions
│
├── data/                 # Database storage (created automatically)
│   └── cases.json       # JSON database file
│
└── exports/              # Export directory (created automatically)
    └── pdfs/            # Generated PDFs

```

## Installation & Setup

1. **Create the project directory:**
   ```bash
   mkdir case-opening-sheet
   cd case-opening-sheet
   ```

2. **Create the modules directory:**
   ```bash
   mkdir modules
   ```

3. **Create an empty `__init__.py` file in modules:**
   ```bash
   touch modules/__init__.py
   ```

4. **Copy all the provided code files to their respective locations**

5. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

6. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

7. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Features

### 📋 Core Functionality
- **Complete Case Management**: Store all case opening sheet information in a searchable JSON database
- **PDF Generation**: Create properly formatted PDFs matching the original case opening sheet layout
- **Search & Filter**: Quickly find cases by name, case number, or other criteria
- **Edit & Update**: Modify existing cases with full history tracking

### 🔧 Technical Features
- **Modular Design**: Clean separation of concerns with dedicated modules
- **Local Storage**: All data stored locally on your machine for privacy
- **No External Dependencies**: Works offline once installed
- **Export Options**: Export individual PDFs or bulk JSON data

### 📊 Data Structure
Cases are stored with comprehensive fields including:
- Defendant information (name, DOB, address, contact)
- Case details (number, charges, type)
- Court information (dates, division, actions)
- Status flags (custody, probation, veteran, etc.)
- Notes and disposition information

## Usage Tips

1. **Starting a New Case**: Click "➕ New Case" in the sidebar
2. **Finding Cases**: Use the search box to filter by name or case number
3. **Editing**: Click on any case in the sidebar to load it for editing
4. **PDF Export**: Save the case first, then PDF is generated automatically
5. **Bulk Export**: Use "Export All Cases (JSON)" to backup your database

## Customization

You can easily modify:
- **Form Fields**: Edit `forms.py` to add/remove fields
- **PDF Layout**: Modify `pdf_generator.py` for different formatting
- **Search Logic**: Enhance `database.py` search methods
- **Validation**: Add custom validation in `utils.py`

## Security Notes

- All data is stored locally in `data/cases.json`
- No cloud connectivity or external API calls
- Regular backups recommended via JSON export
- Consider encrypting the data directory for sensitive information

## Future Enhancements

Consider adding:
- PostgreSQL support for larger datasets
- Case timeline visualization
- Document attachment support
- Multi-user access with authentication
- Integration with court calendar systems
- Automated reminder system for court dates