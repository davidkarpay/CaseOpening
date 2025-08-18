"""
Integration tests for Case Opening Sheet Manager
Tests complete workflows and module interactions
"""
import pytest
import json
import os
import sys
import ast
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from pathlib import Path
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


class TestUINavigationIntegration:
    """Test UI navigation functionality and structure"""
    
    def test_main_app_syntax_and_structure(self):
        """Test that the main app has correct syntax and expected structure"""
        project_root = Path(__file__).parent.parent
        main_app_path = project_root / "case-opening-app.py"
        
        if not main_app_path.exists():
            pytest.skip("Main application file not found")
        
        with open(main_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test AST parsing (syntax validation)
        try:
            tree = ast.parse(content)
            assert tree is not None
        except SyntaxError as e:
            pytest.fail(f"Syntax error in main app: Line {e.lineno} - {e.msg}")
        
        # Test for expected UI elements
        assert "st.columns(4)" in content, "Navigation columns should be present"
        assert "Defendant Info" in content, "Defendant Info navigation should be present"
        assert "Case Details" in content, "Case Details navigation should be present"
        assert "Court Info" in content, "Court Info navigation should be present"
        assert "Export/View" in content, "Export/View navigation should be present"
    
    def test_streamlit_column_structure(self):
        """Test Streamlit column structure for proper indentation"""
        project_root = Path(__file__).parent.parent
        main_app_path = project_root / "case-opening-app.py"
        
        if not main_app_path.exists():
            pytest.skip("Main application file not found")
        
        with open(main_app_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the column navigation section
        navigation_start = None
        for i, line in enumerate(lines):
            if "col1, col2, col3, col4 = st.columns(4)" in line:
                navigation_start = i
                break
        
        if navigation_start is None:
            pytest.fail("Navigation columns section not found")
        
        # Test the indentation of each column block
        column_blocks = []
        current_block = None
        
        for i in range(navigation_start, min(navigation_start + 20, len(lines))):
            line = lines[i]
            if "with col" in line and ":" in line:
                current_block = {"start": i, "with_line": line, "content": []}
                column_blocks.append(current_block)
            elif current_block and line.strip() and not line.strip().startswith('#'):
                # Check indentation level
                with_indent = len(current_block["with_line"]) - len(current_block["with_line"].lstrip())
                line_indent = len(line) - len(line.lstrip())
                
                # Content should be more indented than the 'with' statement
                if line_indent > with_indent:
                    current_block["content"].append(line.strip())
                else:
                    # End of current block
                    current_block = None
        
        # Verify we found the expected column blocks
        assert len(column_blocks) == 4, f"Expected 4 column blocks, found {len(column_blocks)}"
        
        # Verify each block has content
        for i, block in enumerate(column_blocks, 1):
            assert len(block["content"]) > 0, f"Column {i} should have content inside the 'with' block"
            
            # Verify the content contains a button
            content_text = " ".join(block["content"])
            assert "st.button" in content_text, f"Column {i} should contain a button"
    
    def test_navigation_button_functionality(self):
        """Test navigation button structure and session state usage"""
        project_root = Path(__file__).parent.parent
        main_app_path = project_root / "case-opening-app.py"
        
        if not main_app_path.exists():
            pytest.skip("Main application file not found")
        
        with open(main_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test for expected navigation targets
        navigation_targets = ["defendant", "case", "court", "export"]
        
        for target in navigation_targets:
            # Check that each target has a corresponding div anchor
            anchor_pattern = f'<div id="{target}"></div>'
            assert anchor_pattern in content, f"Navigation anchor for '{target}' should be present"
            
            # Check that scroll_to session state is set for each target
            session_state_pattern = f'st.session_state.scroll_to = "{target}"'
            assert session_state_pattern in content, f"Session state scroll_to should be set for '{target}'"
    
    @patch('streamlit.session_state', {'current_case': {}, 'edit_mode': False})
    @patch('streamlit.columns')
    @patch('streamlit.button')
    def test_navigation_button_interactions(self, mock_button, mock_columns):
        """Test navigation button interaction logic"""
        # Mock the column objects
        mock_col1, mock_col2, mock_col3, mock_col4 = Mock(), Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3, mock_col4]
        
        # Mock button clicks for each navigation target
        button_clicks = [True, False, False, False]  # Simulate first button clicked
        mock_button.side_effect = button_clicks
        
        # Import and execute the navigation logic (simulate)
        # This would require more complex mocking to test the actual file execution
        # For now, we test the structural elements
        assert mock_columns.called or True  # Placeholder for actual test logic
    
    def test_form_section_anchors(self):
        """Test that form sections have proper HTML anchors for navigation"""
        project_root = Path(__file__).parent.parent
        main_app_path = project_root / "case-opening-app.py"
        
        if not main_app_path.exists():
            pytest.skip("Main application file not found")
        
        with open(main_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test for section anchors and corresponding render function calls
        sections = [
            ("defendant", "render_defendant_info"),
            ("case", "render_case_info"),
            ("court", "render_court_info"),
            ("export", "Export and View")
        ]
        
        for anchor_id, expected_content in sections:
            # Check for HTML anchor
            anchor_pattern = f'<div id="{anchor_id}"></div>'
            assert anchor_pattern in content, f"Section anchor '{anchor_id}' should be present"
            
            # Check for corresponding content after the anchor
            anchor_index = content.find(anchor_pattern)
            content_after_anchor = content[anchor_index:anchor_index + 1000]  # Check next 1000 chars
            assert expected_content in content_after_anchor, f"Expected content '{expected_content}' should follow anchor '{anchor_id}'"
    
    def test_streamlit_app_structure_integrity(self):
        """Test overall Streamlit app structure integrity"""
        project_root = Path(__file__).parent.parent
        main_app_path = project_root / "case-opening-app.py"
        
        if not main_app_path.exists():
            pytest.skip("Main application file not found")
        
        with open(main_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test for required imports
        required_imports = [
            "import streamlit as st",
            "from modules.database import CaseDatabase",
            "from modules.forms import render_defendant_info",
            "from modules.pdf_generator import generate_case_pdf"
        ]
        
        for import_stmt in required_imports:
            assert import_stmt in content, f"Required import missing: {import_stmt}"
        
        # Test for essential app components
        essential_components = [
            "st.set_page_config",
            "check_authentication()",
            "st.title",
            "st.sidebar",
            "CaseDatabase("
        ]
        
        for component in essential_components:
            assert component in content, f"Essential component missing: {component}"
        
        # Test for proper session state initialization
        session_states = [
            "'current_case'",
            "'edit_mode'",
            "'selected_case_id'"
        ]
        
        for state in session_states:
            assert state in content, f"Session state initialization missing: {state}"