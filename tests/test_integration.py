"""
Integration tests for Case Opening Sheet Manager
Tests complete workflows and module interactions
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from modules.database import CaseDatabase
from modules.pdf_generator import generate_case_pdf
from modules.auth import AuthManager
from fixtures.sample_data import SAMPLE_CASES, SAMPLE_USERS


class TestCaseManagementWorkflow:
    """Test complete case management workflows"""
    
    def test_create_edit_delete_case_workflow(self, temp_db_path):
        """Test complete case lifecycle: create -> edit -> delete"""
        db = CaseDatabase(temp_db_path)
        
        # Step 1: Create new case
        case_data = SAMPLE_CASES["complete_case"].copy()
        result = db.add_case(case_data)
        assert result is True
        
        # Verify case was created
        all_cases = db.get_all_cases()
        assert len(all_cases) == 1
        
        # Step 2: Edit the case
        case_data["charges"] = "Updated charges"
        case_data["notes"] = "Case has been updated"
        
        update_result = db.update_case("case-123", case_data)
        assert update_result is True
        
        # Verify update
        updated_case = db.get_case("case-123")
        assert updated_case["charges"] == "Updated charges"
        assert updated_case["notes"] == "Case has been updated"
        
        # Step 3: Delete the case
        delete_result = db.delete_case("case-123")
        assert delete_result is True
        
        # Verify deletion
        all_cases = db.get_all_cases()
        assert len(all_cases) == 0
        
        deleted_case = db.get_case("case-123")
        assert deleted_case is None
    
    def test_case_search_and_retrieval_workflow(self, temp_db_path):
        """Test case search and retrieval workflow"""
        db = CaseDatabase(temp_db_path)
        
        # Add multiple cases
        cases_to_add = [
            SAMPLE_CASES["complete_case"].copy(),
            SAMPLE_CASES["minimal_case"].copy(),
            {
                "id": "case-789",
                "first_name": "Bob",
                "last_name": "Johnson",
                "case_number": "23CF000789",
                "charges": "DUI"
            }
        ]
        
        for case in cases_to_add:
            db.add_case(case)
        
        # Test search by name
        john_cases = db.search_cases("john")
        assert len(john_cases) == 1
        assert john_cases[0]["id"] == "case-123"
        
        # Test search by case number
        cf_cases = db.search_cases("23CF")
        assert len(cf_cases) == 3  # All cases have this pattern
        
        # Test search by specific case number
        specific_case = db.search_cases("23CF000456")
        assert len(specific_case) == 1
        assert specific_case[0]["id"] == "case-456"
        
        # Test search with no results
        no_results = db.search_cases("nonexistent")
        assert len(no_results) == 0
        
        # Test get all cases
        all_cases = db.get_all_cases()
        assert len(all_cases) == 3
    
    def test_case_pdf_generation_workflow(self, temp_db_path):
        """Test case creation and PDF generation workflow"""
        db = CaseDatabase(temp_db_path)
        
        # Create case
        case_data = SAMPLE_CASES["complete_case"].copy()
        db.add_case(case_data)
        
        # Retrieve case
        saved_case = db.get_case("case-123")
        assert saved_case is not None
        
        # Generate PDF
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            pdf_filename = generate_case_pdf(saved_case)
            
            # Verify PDF generation was attempted
            mock_doc.assert_called_once()
            mock_doc_instance.build.assert_called_once()
            
            # Verify filename contains case information
            assert "Doe_John" in pdf_filename or "John_Doe" in pdf_filename
            assert "23CF000123" in pdf_filename


class TestAuthenticationWorkflow:
    """Test authentication workflows"""
    
    @patch('modules.auth.AuthManager._send_pin_email')
    def test_user_registration_workflow(self, mock_send_email):
        """Test complete user registration workflow"""
        auth = AuthManager()
        mock_send_email.return_value = True
        
        # Step 1: Request access with valid domain
        with patch.object(auth, '_save_pending_user') as mock_save_pending:
            with patch.object(auth, '_load_users', return_value=[]):
                result = auth.request_access('newuser@pd15.org', 'New', 'User')
                
                assert result[0] is True
                assert "PIN has been sent" in result[1]
                mock_save_pending.assert_called_once()
    
    def test_pin_verification_workflow(self):
        """Test PIN generation and verification workflow"""
        auth = AuthManager()
        
        # Generate PIN
        with patch.object(auth, '_save_pins') as mock_save_pins:
            pin = auth._generate_and_store_pin('user@pd15.org')
            
            assert len(pin) == 6
            assert pin.isdigit()
            mock_save_pins.assert_called_once()
        
        # Mock PIN data for verification
        current_time = datetime.now()
        pin_data = {
            'email': 'user@pd15.org',
            'pin': pin,
            'expires_at': (current_time.replace(minute=current_time.minute + 30)).isoformat(),
            'created_at': current_time.isoformat()
        }
        
        with patch.object(auth, '_load_pins', return_value=[pin_data]):
            # Verify correct PIN
            result = auth._verify_pin('user@pd15.org', pin)
            assert result is True
            
            # Verify incorrect PIN
            result = auth._verify_pin('user@pd15.org', '000000')
            assert result is False
    
    def test_jwt_token_workflow(self):
        """Test JWT token generation and verification workflow"""
        auth = AuthManager()
        user_data = SAMPLE_USERS["valid_user"]
        
        # Generate token
        token = auth._generate_jwt_token(user_data)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        verified_data = auth._verify_jwt_token(token)
        assert verified_data is not None
        assert verified_data['email'] == user_data['email']
        
        # Test invalid token
        invalid_verified = auth._verify_jwt_token("invalid.token")
        assert invalid_verified is None


class TestFormAndDataIntegration:
    """Test form rendering and data integration"""
    
    @patch('streamlit.text_input')
    @patch('streamlit.date_input')
    @patch('streamlit.header')
    @patch('streamlit.columns')
    def test_form_data_population_workflow(self, mock_columns, mock_header, mock_date_input, mock_text_input):
        """Test form rendering with existing case data"""
        from modules.forms import render_defendant_info
        
        # Setup mocks
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Test with existing case data
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        render_defendant_info(case_data)
        
        # Verify form elements were called
        mock_header.assert_called_with("👤 Defendant Information")
        mock_columns.assert_called_with(3)
        
        # Verify text inputs were called (exact number depends on implementation)
        assert mock_text_input.called
    
    def test_case_data_persistence_workflow(self, temp_db_path):
        """Test case data persistence across database operations"""
        db1 = CaseDatabase(temp_db_path)
        
        # Add case with first instance
        case_data = SAMPLE_CASES["complete_case"].copy()
        db1.add_case(case_data)
        
        # Create new instance and verify persistence
        db2 = CaseDatabase(temp_db_path)
        retrieved_case = db2.get_case("case-123")
        
        assert retrieved_case is not None
        assert retrieved_case["first_name"] == "John"
        assert retrieved_case["last_name"] == "Doe"
        
        # Modify and verify persistence
        retrieved_case["charges"] = "Modified charges"
        db2.update_case("case-123", retrieved_case)
        
        # Create third instance and verify update persisted
        db3 = CaseDatabase(temp_db_path)
        final_case = db3.get_case("case-123")
        assert final_case["charges"] == "Modified charges"


class TestErrorHandlingWorkflows:
    """Test error handling in various workflows"""
    
    def test_database_error_recovery_workflow(self, temp_db_path):
        """Test database error handling and recovery"""
        db = CaseDatabase(temp_db_path)
        
        # Test operations on non-existent case
        result = db.update_case("nonexistent-id", {})
        assert result is False
        
        result = db.delete_case("nonexistent-id")
        assert result is False
        
        case = db.get_case("nonexistent-id")
        assert case is None
        
        # Test with invalid file operations
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            case_data = SAMPLE_CASES["complete_case"].copy()
            result = db.add_case(case_data)
            assert result is False
    
    def test_pdf_generation_error_workflow(self):
        """Test PDF generation error handling"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        
        # Test with PDF generation failure
        with patch('modules.pdf_generator.SimpleDocTemplate', side_effect=Exception("PDF error")):
            with pytest.raises(Exception):
                generate_case_pdf(case_data)
    
    def test_authentication_error_workflows(self):
        """Test authentication error handling"""
        auth = AuthManager()
        
        # Test invalid domain
        result = auth.request_access('user@invalid.com', 'User', 'Name')
        assert result[0] is False
        assert "domain not authorized" in result[1]
        
        # Test PIN verification with no PIN
        with patch.object(auth, '_load_pins', return_value=[]):
            result = auth._verify_pin('user@pd15.org', '123456')
            assert result is False


class TestEndToEndWorkflows:
    """End-to-end workflow tests"""
    
    def test_complete_case_management_cycle(self, temp_db_path):
        """Test complete case management from creation to PDF generation"""
        db = CaseDatabase(temp_db_path)
        
        # Step 1: Create multiple cases
        cases = [
            SAMPLE_CASES["complete_case"].copy(),
            SAMPLE_CASES["minimal_case"].copy()
        ]
        
        for case in cases:
            result = db.add_case(case)
            assert result is True
        
        # Step 2: Search and filter cases
        search_results = db.search_cases("john")
        assert len(search_results) == 1
        
        target_case = search_results[0]
        
        # Step 3: Update case information
        target_case["charges"] = "Updated charges after review"
        target_case["notes"] = "Case reviewed and updated"
        
        update_result = db.update_case(target_case["id"], target_case)
        assert update_result is True
        
        # Step 4: Generate PDF for updated case
        with patch('modules.pdf_generator.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            pdf_filename = generate_case_pdf(target_case)
            
            mock_doc.assert_called_once()
            assert "Doe_John" in pdf_filename
        
        # Step 5: Verify final state
        final_case = db.get_case(target_case["id"])
        assert final_case["charges"] == "Updated charges after review"
        
        all_cases = db.get_all_cases()
        assert len(all_cases) == 2
    
    def test_multi_user_simulation_workflow(self, temp_db_path):
        """Test simulation of multiple users working with the system"""
        # Simulate User 1 operations
        db_user1 = CaseDatabase(temp_db_path)
        case1 = SAMPLE_CASES["complete_case"].copy()
        case1["attorney"] = "Attorney Smith (User 1)"
        db_user1.add_case(case1)
        
        # Simulate User 2 operations
        db_user2 = CaseDatabase(temp_db_path)
        case2 = SAMPLE_CASES["minimal_case"].copy()
        case2["attorney"] = "Attorney Jones (User 2)"
        db_user2.add_case(case2)
        
        # Both users should see all cases
        user1_cases = db_user1.get_all_cases()
        user2_cases = db_user2.get_all_cases()
        
        assert len(user1_cases) == 2
        assert len(user2_cases) == 2
        
        # Test concurrent operations
        # User 1 updates case
        user1_cases[0]["notes"] = "Updated by User 1"
        db_user1.update_case(user1_cases[0]["id"], user1_cases[0])
        
        # User 2 should see the update
        updated_cases = db_user2.get_all_cases()
        updated_case = next(c for c in updated_cases if c["id"] == user1_cases[0]["id"])
        assert updated_case["notes"] == "Updated by User 1"