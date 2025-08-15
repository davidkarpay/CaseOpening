"""
Sample data fixtures for testing the Case Opening Sheet Manager
"""
from datetime import datetime, date


# Sample case data with various scenarios
SAMPLE_CASES = {
    "complete_case": {
        "id": "case-123",
        "first_name": "John",
        "last_name": "Doe",
        "middle_name": "Michael",
        "dob": "1990-01-15",
        "case_number": "23CF000123",
        "charges": "Battery, Assault",
        "court": "Palm Beach County Circuit Court",
        "judge": "Honorable Judge Smith",
        "attorney": "Public Defender Office",
        "phone": "5551234567",
        "address": "123 Main Street",
        "city": "West Palm Beach",
        "state": "FL",
        "zip_code": "33401",
        "email": "john.doe@example.com",
        "emergency_contact": "Jane Doe - 5559876543",
        "notes": "Client is cooperative and has no prior record",
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-01T12:00:00"
    },
    
    "minimal_case": {
        "id": "case-456",
        "first_name": "Jane",
        "last_name": "Smith",
        "case_number": "23CF000456",
        "created_at": "2023-01-02T10:30:00",
        "updated_at": "2023-01-02T10:30:00"
    },
    
    "invalid_case": {
        "id": "case-789",
        "first_name": "",  # Invalid: empty name
        "last_name": "",   # Invalid: empty name
        "dob": "invalid-date",  # Invalid: bad date format
        "phone": "not-a-phone",  # Invalid: bad phone format
        "created_at": "2023-01-03T15:45:00"
    }
}

# Sample user data for authentication testing
SAMPLE_USERS = {
    "valid_user": {
        "email": "john.doe@pd15.org",
        "first_name": "John",
        "last_name": "Doe",
        "is_verified": True,
        "created_at": "2023-01-01T12:00:00"
    },
    
    "unverified_user": {
        "email": "jane.smith@pd15.org", 
        "first_name": "Jane",
        "last_name": "Smith",
        "is_verified": False,
        "created_at": "2023-01-02T10:00:00"
    },
    
    "invalid_domain_user": {
        "email": "bad.user@gmail.com",
        "first_name": "Bad",
        "last_name": "User"
    }
}

# Sample PIN data for authentication
SAMPLE_PINS = {
    "valid_pin": {
        "email": "john.doe@pd15.org",
        "pin": "123456",
        "expires_at": "2023-01-01T13:00:00",  # 1 hour from creation
        "created_at": "2023-01-01T12:00:00"
    },
    
    "expired_pin": {
        "email": "jane.smith@pd15.org",
        "pin": "654321", 
        "expires_at": "2023-01-01T11:00:00",  # Already expired
        "created_at": "2023-01-01T10:00:00"
    }
}

# Sample PDF data for testing
SAMPLE_PDF_DATA = {
    "basic_pdf": {
        "title": "Case Opening Sheet - John Doe",
        "defendant_info": {
            "name": "John Michael Doe",
            "dob": "01/15/1990",
            "address": "123 Main Street, West Palm Beach, FL 33401"
        },
        "case_info": {
            "case_number": "23CF000123",
            "charges": "Battery, Assault",
            "court": "Palm Beach County Circuit Court"
        }
    }
}

# Phone number test cases
PHONE_TEST_CASES = [
    ("5551234567", "(555) 123-4567"),
    ("555-123-4567", "(555) 123-4567"),
    ("(555) 123-4567", "(555) 123-4567"),
    ("555.123.4567", "(555) 123-4567"),
    ("15551234567", "15551234567"),  # Too long
    ("1234567", "123-4567"),  # 7 digits
    ("123", "123"),  # Too short
    ("", ""),  # Empty
    ("abc123def", "123")  # Non-numeric chars removed
]

# Date parsing test cases
DATE_TEST_CASES = [
    ("2023-01-15", date(2023, 1, 15)),
    ("01/15/2023", date(2023, 1, 15)),
    ("01-15-2023", date(2023, 1, 15)),
    ("2023/01/15", date(2023, 1, 15)),
    ("15/01/2023", date(2023, 1, 15)),
    ("15-01-2023", date(2023, 1, 15)),
    ("invalid-date", None),
    ("", None),
    ("2023-13-45", None)  # Invalid date
]

# Search test cases
SEARCH_TEST_CASES = [
    ("john", ["case-123"]),  # First name match
    ("doe", ["case-123"]),   # Last name match
    ("23CF000123", ["case-123"]),  # Case number match
    ("smith", ["case-456"]),  # Different case
    ("nonexistent", []),      # No matches
    ("", ["case-123", "case-456", "case-789"])  # Empty search returns all
]