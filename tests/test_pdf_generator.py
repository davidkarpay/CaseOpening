"""
Unit tests for the PDF Generator module
"""
import pytest
import os
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from modules.pdf_generator import generate_case_pdf
from fixtures.sample_data import SAMPLE_CASES


class TestPDFGenerator:
    """Test cases for PDF generation functionality"""
    
    def test_generate_case_pdf_creates_file(self, temp_dir):
        """Test that PDF generation creates a file"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.Path') as mock_path:
            mock_path.return_value.mkdir = Mock()
            
            with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
                mock_doc_instance = Mock()
                mock_doc.return_value = mock_doc_instance
                
                result = generate_case_pdf(case_data)
                
                # Verify PDF creation was attempted
                mock_doc.assert_called_once()
                mock_doc_instance.build.assert_called_once()
                
                # Verify filename format
                assert "John_Doe" in result or "Doe_John" in result
                assert "23CF000123" in result
                assert result.endswith(".pdf")
    
    def test_generate_pdf_filename_format(self):
        """Test PDF filename generation with various case data"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            filename = generate_case_pdf(case_data)
            
            # Check filename components
            assert "Doe_John" in filename
            assert "23CF000123" in filename.replace('/', '_')
            assert filename.startswith("exports/pdfs/")
            assert filename.endswith(".pdf")
    
    def test_generate_pdf_minimal_data(self):
        """Test PDF generation with minimal case data"""
        case_data = SAMPLE_CASES["minimal_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            filename = generate_case_pdf(case_data)
            
            # Should handle missing data gracefully
            mock_doc.assert_called_once()
            mock_doc_instance.build.assert_called_once()
    
    def test_generate_pdf_missing_name(self):
        """Test PDF generation with missing defendant name"""
        case_data = {
            "id": "test-case",
            "case_number": "23CF000999"
        }
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            filename = generate_case_pdf(case_data)
            
            # Should use "Unknown" for missing names
            assert "Unknown" in filename
    
    def test_generate_pdf_case_number_sanitization(self):
        """Test that case numbers with slashes are sanitized"""
        case_data = {
            "first_name": "Test",
            "last_name": "User", 
            "case_number": "23CF/000/123"  # Contains slashes
        }
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            filename = generate_case_pdf(case_data)
            
            # Slashes should be replaced with underscores
            assert "23CF_000_123" in filename
            assert "/" not in filename
    
    @patch('modules.pdf_generator.datetime')
    def test_generate_pdf_timestamp(self, mock_datetime):
        """Test that PDF filename includes timestamp"""
        # Mock datetime to return fixed timestamp
        mock_now = Mock()
        mock_now.strftime.return_value = "20230101_120000"
        mock_datetime.now.return_value = mock_now
        
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            filename = generate_case_pdf(case_data)
            
            assert "20230101_120000" in filename
    
    def test_generate_pdf_directory_creation(self):
        """Test that PDF export directory is created"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
                mock_doc_instance = Mock()
                mock_doc.return_value = mock_doc_instance
                
                generate_case_pdf(case_data)
                
                # Verify directory creation
                mock_path.assert_called_with("exports/pdfs")
                mock_path_instance.mkdir.assert_called_with(parents=True, exist_ok=True)
    
    def test_pdf_content_structure(self):
        """Test that PDF contains expected content structure"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            generate_case_pdf(case_data)
            
            # Verify build was called with content
            mock_doc_instance.build.assert_called_once()
            build_args = mock_doc_instance.build.call_args[0]
            
            # Should have content elements
            assert len(build_args[0]) > 0  # Content list should not be empty
    
    @patch('modules.pdf_generator.getSampleStyleSheet')
    def test_pdf_styling(self, mock_styles):
        """Test that PDF uses proper styling"""
        mock_styles.return_value = {
            'Title': Mock(),
            'Heading2': Mock(),
            'Normal': Mock()
        }
        
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            generate_case_pdf(case_data)
            
            # Verify styles were accessed
            mock_styles.assert_called_once()
    
    def test_pdf_page_settings(self):
        """Test that PDF uses correct page settings"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            generate_case_pdf(case_data)
            
            # Verify document creation with proper settings
            mock_doc.assert_called_once()
            call_args = mock_doc.call_args
            
            # Check that pagesize and margins are set
            assert 'pagesize' in call_args[1]
            assert 'rightMargin' in call_args[1]
            assert 'leftMargin' in call_args[1]
            assert 'topMargin' in call_args[1]
            assert 'bottomMargin' in call_args[1]
    
    def test_pdf_error_handling(self):
        """Test PDF generation error handling"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            # Simulate error during PDF creation
            mock_doc.side_effect = Exception("PDF creation failed")
            
            with pytest.raises(Exception):
                generate_case_pdf(case_data)
    
    def test_pdf_special_characters_in_names(self):
        """Test PDF generation with special characters in names"""
        case_data = {
            "first_name": "José",
            "last_name": "García-López",
            "case_number": "23CF000123"
        }
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            filename = generate_case_pdf(case_data)
            
            # Should handle special characters in filename
            assert "García-López_José" in filename or "Garcia-Lopez_Jose" in filename
    
    def test_pdf_empty_case_data(self):
        """Test PDF generation with empty case data"""
        case_data = {}
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            filename = generate_case_pdf(case_data)
            
            # Should handle empty data gracefully
            mock_doc.assert_called_once()
            mock_doc_instance.build.assert_called_once()
            assert "Unknown" in filename
    
    @patch('modules.pdf_generator.Table')
    @patch('modules.pdf_generator.Paragraph')
    def test_pdf_content_elements(self, mock_paragraph, mock_table):
        """Test that PDF includes expected content elements"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            generate_case_pdf(case_data)
            
            # Verify content elements were created
            assert mock_paragraph.called
            mock_doc_instance.build.assert_called_once()