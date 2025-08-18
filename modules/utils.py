"""
Utility functions for the Case Opening Sheet application
"""
import re
import html
import unicodedata
from datetime import datetime, date
from typing import Optional, Union, Dict, Any

def format_phone(phone: str) -> str:
    """Format phone number to (XXX) XXX-XXXX"""
    # Remove all non-numeric characters
    digits = re.sub(r'\D', '', phone)
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 7:
        return f"{digits[:3]}-{digits[3:]}"
    else:
        return phone

def parse_date(date_str: str) -> Optional[date]:
    """Parse date string to date object"""
    if not date_str:
        return None
    
    # Try different date formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%d-%m-%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def format_date(date_obj: Union[date, datetime, str]) -> str:
    """Format date object to MM/DD/YYYY string"""
    if isinstance(date_obj, str):
        return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%m/%d/%Y")
    
    if isinstance(date_obj, date):
        return date_obj.strftime("%m/%d/%Y")
    
    return ""


def sanitize_input(input_str: str, max_length: int = 255, allow_html: bool = False) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not isinstance(input_str, str):
        return ""
    
    # Normalize unicode characters
    input_str = unicodedata.normalize('NFKC', input_str)
    
    # Strip leading/trailing whitespace
    input_str = input_str.strip()
    
    # Truncate to maximum length
    if len(input_str) > max_length:
        input_str = input_str[:max_length]
    
    # HTML escape unless explicitly allowing HTML
    if not allow_html:
        input_str = html.escape(input_str)
    
    # Remove null bytes and control characters (except newline and tab)
    input_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_str)
    
    return input_str


def validate_case_number(case_number: str) -> bool:
    """Validate case number format"""
    if not case_number:
        return False
    
    # Sanitize first
    case_number = sanitize_input(case_number, max_length=50)
    
    # Common case number patterns - adjust for your jurisdiction
    patterns = [
        r'^\d{2}CF\d{6}$',           # 23CF000123
        r'^\d{4}-CF-\d{6}$',         # 2023-CF-000123
        r'^\d{2}[A-Z]{2}\d{6}[A-Z]*$',  # 23CF000123AMB
    ]
    
    return any(re.match(pattern, case_number.upper()) for pattern in patterns)


def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email:
        return False
    
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 254


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Extract digits only
    digits = re.sub(r'\D', '', phone)
    
    # Valid lengths: 7 (local), 10 (US), 11 (US with country code)
    return len(digits) in [7, 10, 11]


def validate_name(name: str) -> bool:
    """Validate person name (letters, spaces, hyphens, apostrophes only)"""
    if not name:
        return False
    
    name = sanitize_input(name, max_length=100)
    
    # Allow letters, spaces, hyphens, apostrophes, periods
    pattern = r'^[a-zA-Z\s\-\'.]+$'
    return bool(re.match(pattern, name)) and len(name.strip()) >= 1


def sanitize_case_data(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize all case data fields"""
    if not isinstance(case_data, dict):
        return {}
    
    sanitized = {}
    
    # Define field-specific sanitization rules
    text_fields = ['first_name', 'last_name', 'middle_name', 'address', 'city', 'state', 
                   'charges', 'attorney', 'judge', 'court', 'notes']
    phone_fields = ['phone', 'emergency_phone']
    email_fields = ['email']
    case_number_fields = ['case_number']
    
    for key, value in case_data.items():
        if value is None:
            sanitized[key] = value
        elif key in text_fields:
            sanitized[key] = sanitize_input(str(value), max_length=500)
        elif key in phone_fields:
            # Sanitize and format phone
            phone_clean = sanitize_input(str(value), max_length=20)
            if validate_phone(phone_clean):
                sanitized[key] = format_phone(phone_clean)
            else:
                sanitized[key] = phone_clean  # Keep original if invalid
        elif key in email_fields:
            email_clean = sanitize_input(str(value), max_length=254).lower()
            sanitized[key] = email_clean if validate_email(email_clean) else ""
        elif key in case_number_fields:
            case_num_clean = sanitize_input(str(value), max_length=50)
            sanitized[key] = case_num_clean
        elif key == 'zip_code':
            # ZIP code validation (US format)
            zip_clean = re.sub(r'\D', '', str(value))[:10]  # Max 10 digits
            sanitized[key] = zip_clean
        else:
            # Generic sanitization for other fields
            sanitized[key] = sanitize_input(str(value), max_length=1000)
    
    return sanitized


def validate_file_path(file_path: str, allowed_extensions: Optional[list] = None) -> bool:
    """Validate file path for security"""
    if not file_path:
        return False
    
    # Normalize path
    file_path = str(file_path).strip()
    
    # Check for path traversal attempts
    if '..' in file_path:
        return False
    
    # Allow absolute paths for legitimate purposes (including temp directories)
    # But block suspicious patterns
    suspicious_patterns = ['../', '..\\', '/etc/', '/proc/', 'C:\\Windows\\System32']
    for pattern in suspicious_patterns:
        if pattern.lower() in file_path.lower():
            return False
    
    # Check file extension if specified
    if allowed_extensions:
        extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
        if extension not in [ext.lower().lstrip('.') for ext in allowed_extensions]:
            return False
    
    return True


def secure_filename(filename: str) -> str:
    """Generate a secure filename by removing dangerous characters"""
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Ensure it doesn't start with a dot (hidden file)
    filename = filename.lstrip('.')
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename or "unnamed_file"


def calculate_age(birth_date: Union[date, datetime]) -> int:
    """Calculate age from birth date"""
    if not birth_date:
        return 0
    
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    
    today = date.today()
    age = today.year - birth_date.year
    
    # Adjust for birthday not yet occurred this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age

def generate_case_summary(case_data: dict) -> str:
    """Generate a brief summary of the case"""
    summary_parts = []
    
    # Defendant name
    name = f"{case_data.get('first_name', '')} {case_data.get('last_name', '')}"
    if name.strip():
        summary_parts.append(f"Defendant: {name.strip()}")
    
    # Case number
    if case_data.get('case_number'):
        summary_parts.append(f"Case #: {case_data['case_number']}")
    
    # Charges
    if case_data.get('charges'):
        charges = case_data['charges']
        if len(charges) > 50:
            charges = charges[:50] + "..."
        summary_parts.append(f"Charges: {charges}")
    
    # Next court date
    if case_data.get('court_date'):
        court_date = format_date(case_data['court_date'])
        summary_parts.append(f"Next: {court_date}")
    
    return " | ".join(summary_parts)

def export_statistics(cases: list) -> dict:
    """Generate statistics from case list"""
    stats = {
        'total_cases': len(cases),
        'in_custody': sum(1 for c in cases if c.get('in_custody')),
        'on_probation': sum(1 for c in cases if c.get('on_probation')),
        'veterans': sum(1 for c in cases if c.get('veteran')),
        'mental_health': sum(1 for c in cases if c.get('mental_health_issues')),
        'pending_charges': sum(1 for c in cases if c.get('pending_charges')),
        'case_types': {},
        'attorneys': {},
        'divisions': {}
    }
    
    # Count case types
    for case in cases:
        case_type = case.get('case_type', 'Unknown')
        stats['case_types'][case_type] = stats['case_types'].get(case_type, 0) + 1
        
        # Count attorneys
        attorney = case.get('attorney', 'Unassigned')
        stats['attorneys'][attorney] = stats['attorneys'].get(attorney, 0) + 1
        
        # Count divisions
        division = case.get('division', 'Unknown')
        stats['divisions'][division] = stats['divisions'].get(division, 0) + 1
    
    return stats

def validate_required_fields(case_data: dict) -> tuple[bool, list]:
    """Validate required fields and return validation status and missing fields"""
    required_fields = [
        'last_name',
        'first_name',
        'case_number'
    ]
    
    missing_fields = []
    for field in required_fields:
        if not case_data.get(field):
            missing_fields.append(field.replace('_', ' ').title())
    
    return len(missing_fields) == 0, missing_fields