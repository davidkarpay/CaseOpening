"""
Pytest configuration and shared fixtures for Case Opening Sheet Manager tests
"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import CaseDatabase


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_db_path(temp_dir):
    """Create a temporary database path"""
    return os.path.join(temp_dir, "test_cases.json")


@pytest.fixture
def case_database(temp_db_path):
    """Create a test CaseDatabase instance"""
    return CaseDatabase(temp_db_path)


@pytest.fixture
def sample_case_data():
    """Sample case data for testing"""
    return {
        "id": "test-case-123",
        "first_name": "John",
        "last_name": "Doe",
        "middle_name": "Michael",
        "dob": "1990-01-15",
        "case_number": "23CF000123",
        "charges": "Battery",
        "court": "Palm Beach County",
        "judge": "Judge Smith",
        "attorney": "Public Defender",
        "phone": "5551234567",
        "address": "123 Main St",
        "city": "West Palm Beach",
        "state": "FL",
        "zip_code": "33401",
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-01T12:00:00"
    }


@pytest.fixture
def multiple_case_data():
    """Multiple cases for testing search and filtering"""
    return [
        {
            "id": "case-1",
            "first_name": "John",
            "last_name": "Doe",
            "case_number": "23CF000123",
            "charges": "Battery",
            "created_at": "2023-01-01T12:00:00"
        },
        {
            "id": "case-2", 
            "first_name": "Jane",
            "last_name": "Smith",
            "case_number": "23CF000456",
            "charges": "Theft",
            "created_at": "2023-01-02T12:00:00"
        },
        {
            "id": "case-3",
            "first_name": "Bob",
            "last_name": "Johnson",
            "case_number": "23CF000789",
            "charges": "DUI",
            "created_at": "2023-01-03T12:00:00"
        }
    ]


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing"""
    with patch('streamlit.text_input') as mock_text_input, \
         patch('streamlit.date_input') as mock_date_input, \
         patch('streamlit.selectbox') as mock_selectbox, \
         patch('streamlit.text_area') as mock_text_area:
        
        mock_text_input.return_value = "test_value"
        mock_date_input.return_value = date.today()
        mock_selectbox.return_value = "option1"
        mock_text_area.return_value = "test text area"
        
        yield {
            'text_input': mock_text_input,
            'date_input': mock_date_input,
            'selectbox': mock_selectbox,
            'text_area': mock_text_area
        }


@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state"""
    session_state = {}
    with patch('streamlit.session_state', session_state):
        yield session_state


@pytest.fixture
def mock_pdf_path(temp_dir):
    """Create a mock PDF file path"""
    pdf_dir = os.path.join(temp_dir, "exports", "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    return os.path.join(pdf_dir, "test_case.pdf")


@pytest.fixture
def mock_smtp():
    """Mock SMTP server for email testing"""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        yield mock_server


@pytest.fixture
def mock_auth_env():
    """Mock environment variables for authentication"""
    env_vars = {
        'JWT_SECRET': 'test-jwt-secret',
        'SMTP_USERNAME': 'test@example.com',
        'SMTP_PASSWORD': 'test-password'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def freeze_time():
    """Fixture to freeze time for consistent testing"""
    from freezegun import freeze_time
    with freeze_time("2023-01-01 12:00:00"):
        yield datetime(2023, 1, 1, 12, 0, 0)