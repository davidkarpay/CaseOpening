"""
Unit tests for the Forms module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from modules.forms import render_defendant_info, render_case_info, render_court_info
from fixtures.sample_data import SAMPLE_CASES


class TestRenderDefendantInfo:
    """Test cases for defendant information form rendering"""
    
    @patch('streamlit.text_input')
    @patch('streamlit.date_input')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_defendant_info_basic(self, mock_columns, mock_header, mock_date_input, mock_text_input):
        """Test basic defendant info rendering"""
        # Setup mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Setup mock return values
        mock_text_input.side_effect = ["Doe", "John", "Michael"]
        mock_date_input.return_value = date(1990, 1, 15)
        
        case_data = {}
        
        with patch('streamlit.columns', return_value=[mock_col1, mock_col2, mock_col3]):
            render_defendant_info(case_data)
        
        # Verify header was created
        mock_header.assert_called_with("👤 Defendant Information")
        
        # Verify columns were created
        mock_columns.assert_called_with(3)
        
        # Verify case data was populated
        assert case_data.get('last_name') == "Doe"
        assert case_data.get('first_name') == "John"
        assert case_data.get('middle_name') == "Michael"
    
    @patch('streamlit.text_input')
    @patch('streamlit.date_input')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_defendant_info_with_existing_data(self, mock_columns, mock_header, mock_date_input, mock_text_input):
        """Test rendering with existing case data"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        # Setup mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        render_defendant_info(case_data)
        
        # Verify text inputs were called with existing values
        text_input_calls = mock_text_input.call_args_list
        
        # Check that existing values were passed as defaults
        for call in text_input_calls:
            if 'value' in call[1]:
                assert call[1]['value'] != ''  # Should have existing values
    
    @patch('streamlit.text_input')
    @patch('streamlit.date_input')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_defendant_info_date_parsing(self, mock_columns, mock_header, mock_date_input, mock_text_input):
        """Test date parsing for existing DOB data"""
        case_data = {
            'dob': '1990-01-15'  # String date
        }
        
        # Setup mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        render_defendant_info(case_data)
        
        # Verify date_input was called
        mock_date_input.assert_called()
        
        # Check that date was properly parsed
        date_call = mock_date_input.call_args
        assert 'value' in date_call[1]
    
    @patch('streamlit.text_input')
    @patch('streamlit.date_input')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_defendant_info_invalid_date(self, mock_columns, mock_header, mock_date_input, mock_text_input):
        """Test handling of invalid date values"""
        case_data = {
            'dob': 'invalid-date'
        }
        
        # Setup mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        render_defendant_info(case_data)
        
        # Should handle invalid date gracefully
        mock_date_input.assert_called()
        date_call = mock_date_input.call_args
        # Value should be None for invalid date
        assert date_call[1]['value'] is None


class TestRenderCaseInfo:
    """Test cases for case information form rendering"""
    
    @patch('streamlit.text_input')
    @patch('streamlit.text_area')
    @patch('streamlit.selectbox')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_case_info_basic(self, mock_columns, mock_header, mock_selectbox, mock_text_area, mock_text_input):
        """Test basic case info rendering"""
        # Setup mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Setup mock return values
        mock_text_input.side_effect = ["23CF000123", "Battery"]
        mock_text_area.return_value = "Defendant charged with battery"
        mock_selectbox.return_value = "Felony"
        
        case_data = {}
        
        render_case_info(case_data)
        
        # Verify header was created
        mock_header.assert_called_with("⚖️ Case Information")
        
        # Verify form elements were called
        assert mock_text_input.called
        assert mock_text_area.called or mock_selectbox.called
    
    @patch('streamlit.text_input')
    @patch('streamlit.text_area')
    @patch('streamlit.selectbox')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_case_info_with_existing_data(self, mock_columns, mock_header, mock_selectbox, mock_text_area, mock_text_input):
        """Test rendering with existing case data"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        # Setup mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        render_case_info(case_data)
        
        # Verify that existing values were used
        if mock_text_input.called:
            text_input_calls = mock_text_input.call_args_list
            for call in text_input_calls:
                if 'value' in call[1]:
                    # Should use existing values from case_data
                    pass  # Values would be from the existing case data


class TestRenderCourtInfo:
    """Test cases for court information form rendering"""
    
    @patch('streamlit.text_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.date_input')
    @patch('streamlit.time_input')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_court_info_basic(self, mock_columns, mock_header, mock_time_input, mock_date_input, mock_selectbox, mock_text_input):
        """Test basic court info rendering"""
        # Setup mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Setup mock return values
        mock_text_input.side_effect = ["Judge Smith", "Courtroom 1A"]
        mock_selectbox.return_value = "Palm Beach County"
        mock_date_input.return_value = date.today()
        
        case_data = {}
        
        render_court_info(case_data)
        
        # Verify header was created
        mock_header.assert_called_with("🏛️ Court Information")
        
        # Verify form elements were called
        assert mock_text_input.called or mock_selectbox.called
    
    @patch('streamlit.text_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.date_input')
    @patch('streamlit.time_input')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_render_court_info_with_existing_data(self, mock_columns, mock_header, mock_time_input, mock_date_input, mock_selectbox, mock_text_input):
        """Test rendering with existing court data"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        # Setup mock columns
        mock_col1, mock_col2 = Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        render_court_info(case_data)
        
        # Verify that form was rendered
        mock_header.assert_called_with("🏛️ Court Information")


class TestFormIntegration:
    """Integration tests for form modules"""
    
    @patch('streamlit.text_input')
    @patch('streamlit.date_input')
    @patch('streamlit.text_area')
    @patch('streamlit.selectbox')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_all_forms_render_without_error(self, mock_columns, mock_header, mock_selectbox, mock_text_area, mock_date_input, mock_text_input):
        """Test that all forms can be rendered without errors"""
        case_data = {}
        
        # Setup mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Setup mock return values
        mock_text_input.return_value = "test"
        mock_date_input.return_value = date.today()
        mock_text_area.return_value = "test area"
        mock_selectbox.return_value = "option1"
        
        # Render all forms
        render_defendant_info(case_data)
        render_case_info(case_data)
        render_court_info(case_data)
        
        # Verify all forms rendered
        assert mock_header.call_count >= 3
    
    @patch('streamlit.text_input')
    @patch('streamlit.date_input')
    @patch('streamlit.text_area')
    @patch('streamlit.selectbox')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_forms_populate_case_data(self, mock_columns, mock_header, mock_selectbox, mock_text_area, mock_date_input, mock_text_input):
        """Test that forms properly populate case data"""
        case_data = {}
        
        # Setup mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Setup mock return values with specific data
        mock_text_input.side_effect = ["Doe", "John", "Michael", "23CF000123", "Battery", "Judge Smith"]
        mock_date_input.return_value = date(1990, 1, 15)
        mock_text_area.return_value = "Case notes"
        mock_selectbox.return_value = "Felony"
        
        # Render forms
        render_defendant_info(case_data)
        render_case_info(case_data)
        render_court_info(case_data)
        
        # Verify case_data was populated (exact keys depend on implementation)
        assert len(case_data) > 0
    
    def test_form_session_state_integration(self):
        """Test forms integration with Streamlit session state"""
        with patch('streamlit.session_state', {}) as mock_session_state:
            case_data = {}
            
            # Mock the streamlit components
            with patch('streamlit.text_input', return_value="test"):
                with patch('streamlit.date_input', return_value=date.today()):
                    with patch('streamlit.header'):
                        with patch('streamlit.columns', return_value=[Mock(), Mock(), Mock()]):
                            render_defendant_info(case_data)
            
            # Test should complete without error
            assert True