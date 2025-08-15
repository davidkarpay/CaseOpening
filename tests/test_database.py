"""
Unit tests for the CaseDatabase module
"""
import pytest
import json
import os
from unittest.mock import patch, mock_open
from modules.database import CaseDatabase
from fixtures.sample_data import SAMPLE_CASES


class TestCaseDatabase:
    """Test cases for the CaseDatabase class"""
    
    def test_init_creates_db_file(self, temp_db_path):
        """Test that initializing creates the database file"""
        assert not os.path.exists(temp_db_path)
        db = CaseDatabase(temp_db_path)
        assert os.path.exists(temp_db_path)
        
    def test_init_with_existing_file(self, temp_db_path):
        """Test initialization with existing database file"""
        # Create existing file with data
        existing_data = [SAMPLE_CASES["complete_case"]]
        with open(temp_db_path, 'w') as f:
            json.dump(existing_data, f)
            
        db = CaseDatabase(temp_db_path)
        cases = db.get_all_cases()
        assert len(cases) == 1
        assert cases[0]["id"] == "case-123"
    
    def test_add_case_success(self, case_database):
        """Test successfully adding a case"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        result = case_database.add_case(case_data)
        
        assert result is True
        cases = case_database.get_all_cases()
        assert len(cases) == 1
        assert cases[0]["id"] == "case-123"
    
    def test_add_multiple_cases(self, case_database):
        """Test adding multiple cases"""
        case1 = SAMPLE_CASES["complete_case"].copy()
        case2 = SAMPLE_CASES["minimal_case"].copy()
        
        case_database.add_case(case1)
        case_database.add_case(case2)
        
        cases = case_database.get_all_cases()
        assert len(cases) == 2
        
    def test_get_case_by_id_exists(self, case_database):
        """Test getting a case that exists"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        case_database.add_case(case_data)
        
        result = case_database.get_case("case-123")
        assert result is not None
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
    
    def test_get_case_by_id_not_exists(self, case_database):
        """Test getting a case that doesn't exist"""
        result = case_database.get_case("nonexistent-id")
        assert result is None
    
    def test_update_case_exists(self, case_database):
        """Test updating an existing case"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        case_database.add_case(case_data)
        
        updated_data = case_data.copy()
        updated_data["first_name"] = "Johnny"
        updated_data["charges"] = "Updated charges"
        
        result = case_database.update_case("case-123", updated_data)
        assert result is True
        
        updated_case = case_database.get_case("case-123")
        assert updated_case["first_name"] == "Johnny"
        assert updated_case["charges"] == "Updated charges"
    
    def test_update_case_not_exists(self, case_database):
        """Test updating a case that doesn't exist"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        result = case_database.update_case("nonexistent-id", case_data)
        assert result is False
    
    def test_delete_case_exists(self, case_database):
        """Test deleting an existing case"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        case_database.add_case(case_data)
        
        result = case_database.delete_case("case-123")
        assert result is True
        
        cases = case_database.get_all_cases()
        assert len(cases) == 0
        
        deleted_case = case_database.get_case("case-123")
        assert deleted_case is None
    
    def test_delete_case_not_exists(self, case_database):
        """Test deleting a case that doesn't exist"""
        result = case_database.delete_case("nonexistent-id")
        assert result is False
    
    def test_search_cases_by_name(self, case_database):
        """Test searching cases by defendant name"""
        case1 = SAMPLE_CASES["complete_case"].copy()
        case2 = SAMPLE_CASES["minimal_case"].copy()
        case_database.add_case(case1)
        case_database.add_case(case2)
        
        # Search by first name
        results = case_database.search_cases("john")
        assert len(results) == 1
        assert results[0]["id"] == "case-123"
        
        # Search by last name
        results = case_database.search_cases("smith")
        assert len(results) == 1
        assert results[0]["id"] == "case-456"
        
        # Case insensitive search
        results = case_database.search_cases("JOHN")
        assert len(results) == 1
    
    def test_search_cases_by_case_number(self, case_database):
        """Test searching cases by case number"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        case_database.add_case(case_data)
        
        results = case_database.search_cases("23CF000123")
        assert len(results) == 1
        assert results[0]["case_number"] == "23CF000123"
        
        # Partial case number search
        results = case_database.search_cases("23CF")
        assert len(results) == 1
    
    def test_search_cases_no_results(self, case_database):
        """Test searching with no matching results"""
        case_data = SAMPLE_CASES["complete_case"].copy()
        case_database.add_case(case_data)
        
        results = case_database.search_cases("nonexistent")
        assert len(results) == 0
    
    def test_search_cases_empty_query(self, case_database):
        """Test searching with empty query returns all cases"""
        case1 = SAMPLE_CASES["complete_case"].copy()
        case2 = SAMPLE_CASES["minimal_case"].copy()
        case_database.add_case(case1)
        case_database.add_case(case2)
        
        results = case_database.search_cases("")
        assert len(results) == 2
    
    def test_get_all_cases_empty(self, case_database):
        """Test getting all cases when database is empty"""
        cases = case_database.get_all_cases()
        assert cases == []
    
    def test_get_all_cases_with_data(self, case_database):
        """Test getting all cases with data"""
        case1 = SAMPLE_CASES["complete_case"].copy()
        case2 = SAMPLE_CASES["minimal_case"].copy()
        case_database.add_case(case1)
        case_database.add_case(case2)
        
        cases = case_database.get_all_cases()
        assert len(cases) == 2
        
        # Check that cases are returned in order
        case_ids = [case["id"] for case in cases]
        assert "case-123" in case_ids
        assert "case-456" in case_ids
    
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_load_data_permission_error(self, temp_db_path):
        """Test handling permission errors when loading data"""
        db = CaseDatabase(temp_db_path)
        data = db._load_data()
        assert data == []
    
    @patch('builtins.open', side_effect=IOError("File not found"))
    def test_save_data_io_error(self, temp_db_path):
        """Test handling IO errors when saving data"""
        db = CaseDatabase(temp_db_path)
        case_data = SAMPLE_CASES["complete_case"].copy()
        result = db.add_case(case_data)
        assert result is False
    
    def test_load_data_corrupted_json(self, temp_db_path):
        """Test handling corrupted JSON file"""
        # Create corrupted JSON file
        with open(temp_db_path, 'w') as f:
            f.write("invalid json content {")
            
        db = CaseDatabase(temp_db_path)
        cases = db.get_all_cases()
        assert cases == []
    
    def test_database_persistence(self, temp_db_path):
        """Test that data persists between database instances"""
        # Create first instance and add data
        db1 = CaseDatabase(temp_db_path)
        case_data = SAMPLE_CASES["complete_case"].copy()
        db1.add_case(case_data)
        
        # Create second instance and verify data exists
        db2 = CaseDatabase(temp_db_path)
        cases = db2.get_all_cases()
        assert len(cases) == 1
        assert cases[0]["id"] == "case-123"
    
    def test_case_ordering(self, case_database):
        """Test that cases maintain insertion order"""
        cases_to_add = [
            SAMPLE_CASES["complete_case"].copy(),
            SAMPLE_CASES["minimal_case"].copy(),
            SAMPLE_CASES["invalid_case"].copy()
        ]
        
        for case in cases_to_add:
            case_database.add_case(case)
            
        all_cases = case_database.get_all_cases()
        assert len(all_cases) == 3
        
        # Verify order
        expected_ids = ["case-123", "case-456", "case-789"]
        actual_ids = [case["id"] for case in all_cases]
        assert actual_ids == expected_ids