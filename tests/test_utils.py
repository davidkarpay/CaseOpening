"""
Unit tests for the Utils module
"""
import pytest
from datetime import date, datetime
from modules.utils import format_phone, parse_date, format_date
from fixtures.sample_data import PHONE_TEST_CASES, DATE_TEST_CASES


class TestFormatPhone:
    """Test cases for phone number formatting"""
    
    @pytest.mark.parametrize("input_phone,expected", PHONE_TEST_CASES)
    def test_format_phone_various_inputs(self, input_phone, expected):
        """Test phone formatting with various input formats"""
        result = format_phone(input_phone)
        assert result == expected
    
    def test_format_phone_ten_digits(self):
        """Test formatting 10-digit phone number"""
        result = format_phone("5551234567")
        assert result == "(555) 123-4567"
    
    def test_format_phone_with_dashes(self):
        """Test formatting phone with existing dashes"""
        result = format_phone("555-123-4567")
        assert result == "(555) 123-4567"
    
    def test_format_phone_with_parentheses(self):
        """Test formatting phone with existing parentheses"""
        result = format_phone("(555) 123-4567")
        assert result == "(555) 123-4567"
    
    def test_format_phone_with_dots(self):
        """Test formatting phone with dots"""
        result = format_phone("555.123.4567")
        assert result == "(555) 123-4567"
    
    def test_format_phone_seven_digits(self):
        """Test formatting 7-digit phone number"""
        result = format_phone("1234567")
        assert result == "123-4567"
    
    def test_format_phone_with_country_code(self):
        """Test formatting phone with country code (too long)"""
        result = format_phone("15551234567")
        assert result == "15551234567"  # Should return as-is
    
    def test_format_phone_too_short(self):
        """Test formatting phone that's too short"""
        result = format_phone("123")
        assert result == "123"  # Should return as-is
    
    def test_format_phone_empty_string(self):
        """Test formatting empty phone string"""
        result = format_phone("")
        assert result == ""
    
    def test_format_phone_non_numeric(self):
        """Test formatting phone with non-numeric characters"""
        result = format_phone("abc123def4567ghi")
        assert result == "123-4567"  # Only digits extracted
    
    def test_format_phone_spaces_only(self):
        """Test formatting phone with only spaces"""
        result = format_phone("   ")
        assert result == "   "  # Should return as-is


class TestParseDate:
    """Test cases for date parsing"""
    
    @pytest.mark.parametrize("input_date,expected", DATE_TEST_CASES)
    def test_parse_date_various_formats(self, input_date, expected):
        """Test date parsing with various input formats"""
        result = parse_date(input_date)
        assert result == expected
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO format date"""
        result = parse_date("2023-01-15")
        assert result == date(2023, 1, 15)
    
    def test_parse_date_us_format(self):
        """Test parsing US format date"""
        result = parse_date("01/15/2023")
        assert result == date(2023, 1, 15)
    
    def test_parse_date_us_dash_format(self):
        """Test parsing US dash format date"""
        result = parse_date("01-15-2023")
        assert result == date(2023, 1, 15)
    
    def test_parse_date_year_first_slash(self):
        """Test parsing year-first slash format"""
        result = parse_date("2023/01/15")
        assert result == date(2023, 1, 15)
    
    def test_parse_date_day_first(self):
        """Test parsing day-first format"""
        result = parse_date("15/01/2023")
        assert result == date(2023, 1, 15)
    
    def test_parse_date_day_first_dash(self):
        """Test parsing day-first dash format"""
        result = parse_date("15-01-2023")
        assert result == date(2023, 1, 15)
    
    def test_parse_date_invalid_format(self):
        """Test parsing invalid date format"""
        result = parse_date("invalid-date")
        assert result is None
    
    def test_parse_date_empty_string(self):
        """Test parsing empty date string"""
        result = parse_date("")
        assert result is None
    
    def test_parse_date_none_input(self):
        """Test parsing None input"""
        result = parse_date(None)
        assert result is None
    
    def test_parse_date_invalid_date_values(self):
        """Test parsing date with invalid values"""
        result = parse_date("2023-13-45")  # Invalid month and day
        assert result is None
    
    def test_parse_date_february_29_leap_year(self):
        """Test parsing February 29 in leap year"""
        result = parse_date("2024-02-29")  # 2024 is a leap year
        assert result == date(2024, 2, 29)
    
    def test_parse_date_february_29_non_leap_year(self):
        """Test parsing February 29 in non-leap year"""
        result = parse_date("2023-02-29")  # 2023 is not a leap year
        assert result is None


class TestFormatDate:
    """Test cases for date formatting"""
    
    def test_format_date_from_date_object(self):
        """Test formatting from date object"""
        input_date = date(2023, 1, 15)
        result = format_date(input_date)
        assert result == "01/15/2023"
    
    def test_format_date_from_datetime_object(self):
        """Test formatting from datetime object"""
        input_datetime = datetime(2023, 1, 15, 12, 30, 45)
        result = format_date(input_datetime)
        assert result == "01/15/2023"
    
    def test_format_date_from_string(self):
        """Test formatting from string (should return as-is)"""
        input_string = "01/15/2023"
        result = format_date(input_string)
        assert result == "01/15/2023"
    
    def test_format_date_single_digit_month_day(self):
        """Test formatting with single digit month and day"""
        input_date = date(2023, 5, 8)
        result = format_date(input_date)
        assert result == "05/08/2023"
    
    def test_format_date_december_31(self):
        """Test formatting December 31"""
        input_date = date(2023, 12, 31)
        result = format_date(input_date)
        assert result == "12/31/2023"
    
    def test_format_date_january_1(self):
        """Test formatting January 1"""
        input_date = date(2023, 1, 1)
        result = format_date(input_date)
        assert result == "01/01/2023"
    
    def test_format_date_leap_year_february_29(self):
        """Test formatting February 29 in leap year"""
        input_date = date(2024, 2, 29)
        result = format_date(input_date)
        assert result == "02/29/2024"
    
    def test_format_date_none_input(self):
        """Test formatting None input"""
        with pytest.raises(AttributeError):
            format_date(None)
    
    def test_format_date_empty_string(self):
        """Test formatting empty string"""
        result = format_date("")
        assert result == ""


class TestUtilsIntegration:
    """Integration tests for utility functions"""
    
    def test_phone_format_roundtrip(self):
        """Test that formatted phone numbers remain consistent"""
        original = "5551234567"
        formatted = format_phone(original)
        reformatted = format_phone(formatted)
        assert formatted == reformatted
    
    def test_date_parse_format_roundtrip(self):
        """Test date parsing and formatting roundtrip"""
        original_string = "2023-01-15"
        parsed_date = parse_date(original_string)
        formatted_string = format_date(parsed_date)
        reparsed_date = parse_date(formatted_string)
        
        assert parsed_date == reparsed_date
    
    def test_utils_with_sample_case_data(self):
        """Test utility functions with sample case data"""
        from fixtures.sample_data import SAMPLE_CASES
        
        case_data = SAMPLE_CASES["complete_case"]
        
        # Test phone formatting
        if 'phone' in case_data:
            formatted_phone = format_phone(case_data['phone'])
            assert len(formatted_phone) > 0
        
        # Test date parsing
        if 'dob' in case_data:
            parsed_dob = parse_date(case_data['dob'])
            assert parsed_dob is not None
            
            formatted_dob = format_date(parsed_dob)
            assert len(formatted_dob) > 0
    
    def test_edge_cases_combination(self):
        """Test combination of edge cases"""
        # Test with empty/None values
        assert format_phone("") == ""
        assert parse_date("") is None
        assert format_date("") == ""
        
        # Test with whitespace
        assert format_phone("   ") == "   "
        assert parse_date("   ") is None
        
        # Test with special characters
        phone_with_special = "555-123-4567 ext. 123"
        formatted = format_phone(phone_with_special)
        # Should extract only digits and format basic number
        assert "555" in formatted and "123" in formatted and "4567" in formatted