"""
Utility functions for the Case Opening Sheet application
"""
import re
from datetime import datetime, date
from typing import Optional, Union

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

def validate_case_number(case_number: str) -> bool:
    """Validate case number format"""
    # Basic validation - can be customized based on your jurisdiction's format
    if not case_number:
        return False
    
    # Example pattern: YYYY-CF-XXXXXX or YYYY-MM-XXXXXX
    pattern = r'^\d{4}-[A-Z]{2}-\d{6}$'
    return bool(re.match(pattern, case_number.upper()))

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename.strip('_')

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