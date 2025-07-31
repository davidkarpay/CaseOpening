"""
Database module for managing cases in JSON format
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CaseDatabase:
    """JSON-based database for case management"""
    
    def __init__(self, db_path: str = "data/cases.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not self.db_path.exists():
            self._save_data([])
    
    def _load_data(self) -> List[Dict]:
        """Load data from JSON file"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return []
    
    def _save_data(self, data: List[Dict]):
        """Save data to JSON file"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def add_case(self, case_data: Dict) -> bool:
        """Add a new case"""
        try:
            cases = self._load_data()
            cases.append(case_data)
            self._save_data(cases)
            return True
        except Exception as e:
            logger.error(f"Error adding case: {e}")
            return False
    
    def update_case(self, case_id: str, case_data: Dict) -> bool:
        """Update an existing case"""
        try:
            cases = self._load_data()
            for i, case in enumerate(cases):
                if case.get('id') == case_id:
                    cases[i] = case_data
                    self._save_data(cases)
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating case: {e}")
            return False
    
    def delete_case(self, case_id: str) -> bool:
        """Delete a case"""
        try:
            cases = self._load_data()
            cases = [c for c in cases if c.get('id') != case_id]
            self._save_data(cases)
            return True
        except Exception as e:
            logger.error(f"Error deleting case: {e}")
            return False
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """Get a specific case"""
        cases = self._load_data()
        for case in cases:
            if case.get('id') == case_id:
                return case
        return None
    
    def get_all_cases(self) -> List[Dict]:
        """Get all cases"""
        return self._load_data()
    
    def search_cases(self, search_term: str) -> List[Dict]:
        """Search cases by name or case number"""
        search_term = search_term.lower()
        cases = self._load_data()
        
        results = []
        for case in cases:
            # Search in multiple fields
            searchable_fields = [
                case.get('first_name', ''),
                case.get('last_name', ''),
                case.get('middle_name', ''),
                case.get('case_number', ''),
                case.get('charges', ''),
                case.get('asa', '')
            ]
            
            # Check if search term appears in any field
            if any(search_term in str(field).lower() for field in searchable_fields):
                results.append(case)
        
        return results
    
    def get_cases_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get cases within a date range"""
        cases = self._load_data()
        results = []
        
        for case in cases:
            court_date = case.get('court_date')
            if court_date and start_date <= court_date <= end_date:
                results.append(case)
        
        return sorted(results, key=lambda x: x.get('court_date', ''))
    
    def get_cases_by_status(self, status: str) -> List[Dict]:
        """Get cases by status (e.g., 'In Custody', 'On Probation')"""
        cases = self._load_data()
        results = []
        
        status_lower = status.lower()
        for case in cases:
            if status_lower == 'in custody' and case.get('in_custody'):
                results.append(case)
            elif status_lower == 'on probation' and case.get('on_probation'):
                results.append(case)
            elif status_lower == 'veteran' and case.get('veteran'):
                results.append(case)
        
        return results
    
    def export_to_csv(self, filepath: str):
        """Export all cases to CSV"""
        import csv
        
        cases = self._load_data()
        if not cases:
            return
        
        # Get all unique keys
        all_keys = set()
        for case in cases:
            all_keys.update(case.keys())
        
        # Write CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(cases)