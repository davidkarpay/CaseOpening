"""
Unit tests for the Authentication module
"""
import pytest
import json
import os
import hashlib
import hmac
import base64
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime, timedelta
from modules.auth import AuthManager
from fixtures.sample_data import SAMPLE_USERS, SAMPLE_PINS


class TestAuthManager:
    """Test cases for the AuthManager class"""
    
    def test_init_creates_files(self, temp_dir):
        """Test that AuthManager initialization creates necessary files"""
        with patch('modules.auth.pathlib.Path') as mock_path:
            mock_path.return_value.mkdir = Mock()
            
            auth = AuthManager()
            
            # Verify data directory creation was attempted
            mock_path.assert_called_with('data')
    
    def test_allowed_domains(self):
        """Test that allowed domains are properly configured"""
        auth = AuthManager()
        
        assert '@pd15.org' in auth.allowed_domains
        assert '@pd15.state.fl.us' in auth.allowed_domains
    
    @patch('modules.auth.pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_initialize_storage_empty_files(self, mock_file, mock_exists):
        """Test storage initialization with empty files"""
        mock_exists.return_value = False
        
        auth = AuthManager()
        
        # Should create empty JSON files
        assert mock_file.called
    
    def test_is_domain_allowed_valid(self):
        """Test domain validation with valid domains"""
        auth = AuthManager()
        
        assert auth._is_domain_allowed('user@pd15.org') is True
        assert auth._is_domain_allowed('user@pd15.state.fl.us') is True
    
    def test_is_domain_allowed_invalid(self):
        """Test domain validation with invalid domains"""
        auth = AuthManager()
        
        assert auth._is_domain_allowed('user@gmail.com') is False
        assert auth._is_domain_allowed('user@yahoo.com') is False
        assert auth._is_domain_allowed('invalid-email') is False
    
    def test_generate_pin(self):
        """Test PIN generation"""
        auth = AuthManager()
        pin = auth._generate_pin()
        
        assert len(pin) == 6
        assert pin.isdigit()
        assert 100000 <= int(pin) <= 999999
    
    def test_generate_jwt_token(self):
        """Test JWT token generation"""
        auth = AuthManager()
        user_data = SAMPLE_USERS["valid_user"]
        
        token = auth._generate_jwt_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_jwt_token_valid(self):
        """Test JWT token verification with valid token"""
        auth = AuthManager()
        user_data = SAMPLE_USERS["valid_user"]
        
        token = auth._generate_jwt_token(user_data)
        verified_data = auth._verify_jwt_token(token)
        
        assert verified_data is not None
        assert verified_data['email'] == user_data['email']
    
    def test_verify_jwt_token_invalid(self):
        """Test JWT token verification with invalid token"""
        auth = AuthManager()
        
        # Test with invalid token
        verified_data = auth._verify_jwt_token("invalid.token.here")
        assert verified_data is None
        
        # Test with empty token
        verified_data = auth._verify_jwt_token("")
        assert verified_data is None
    
    @patch('modules.auth.time.time')
    def test_verify_jwt_token_expired(self, mock_time):
        """Test JWT token verification with expired token"""
        auth = AuthManager()
        
        # Generate token in the past
        mock_time.return_value = 1000000  # Past time
        user_data = SAMPLE_USERS["valid_user"]
        token = auth._generate_jwt_token(user_data)
        
        # Verify in the future (token should be expired)
        mock_time.return_value = 2000000  # Future time
        verified_data = auth._verify_jwt_token(token)
        
        assert verified_data is None
    
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_load_users_empty(self, mock_file):
        """Test loading users from empty file"""
        auth = AuthManager()
        users = auth._load_users()
        
        assert users == []
    
    @patch('builtins.open', new_callable=mock_open)
    def test_load_users_with_data(self, mock_file):
        """Test loading users with existing data"""
        user_data = [SAMPLE_USERS["valid_user"]]
        mock_file.return_value.read.return_value = json.dumps(user_data)
        
        auth = AuthManager()
        users = auth._load_users()
        
        assert len(users) == 1
        assert users[0]['email'] == 'john.doe@pd15.org'
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_users_file_not_found(self, mock_file):
        """Test loading users when file doesn't exist"""
        auth = AuthManager()
        users = auth._load_users()
        
        assert users == []
    
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_load_users_invalid_json(self, mock_file):
        """Test loading users with invalid JSON"""
        auth = AuthManager()
        users = auth._load_users()
        
        assert users == []
    
    @patch('modules.auth.AuthManager._save_users')
    @patch('modules.auth.AuthManager._load_users')
    def test_save_user(self, mock_load, mock_save):
        """Test saving a new user"""
        auth = AuthManager()
        mock_load.return_value = []
        
        user_data = SAMPLE_USERS["valid_user"]
        result = auth._save_user(user_data)
        
        assert result is True
        mock_save.assert_called_once()
    
    @patch('modules.auth.AuthManager._save_users')
    @patch('modules.auth.AuthManager._load_users')
    def test_save_user_duplicate_email(self, mock_load, mock_save):
        """Test saving user with duplicate email"""
        auth = AuthManager()
        existing_user = SAMPLE_USERS["valid_user"]
        mock_load.return_value = [existing_user]
        
        # Try to save same user again
        result = auth._save_user(existing_user)
        
        # Should not save duplicate
        assert result is False
        mock_save.assert_not_called()
    
    @patch('modules.auth.AuthManager._load_pins')
    def test_generate_and_store_pin(self, mock_load_pins):
        """Test PIN generation and storage"""
        auth = AuthManager()
        mock_load_pins.return_value = []
        
        with patch.object(auth, '_save_pins') as mock_save:
            email = "test@pd15.org"
            pin = auth._generate_and_store_pin(email)
            
            assert len(pin) == 6
            assert pin.isdigit()
            mock_save.assert_called_once()
    
    @patch('modules.auth.AuthManager._load_pins')
    def test_verify_pin_valid(self, mock_load_pins):
        """Test PIN verification with valid PIN"""
        auth = AuthManager()
        
        # Mock current time
        current_time = datetime.now()
        future_time = current_time + timedelta(minutes=30)
        
        pin_data = {
            'email': 'test@pd15.org',
            'pin': '123456',
            'expires_at': future_time.isoformat(),
            'created_at': current_time.isoformat()
        }
        
        mock_load_pins.return_value = [pin_data]
        
        result = auth._verify_pin('test@pd15.org', '123456')
        assert result is True
    
    @patch('modules.auth.AuthManager._load_pins')
    def test_verify_pin_expired(self, mock_load_pins):
        """Test PIN verification with expired PIN"""
        auth = AuthManager()
        
        # Mock expired PIN
        past_time = datetime.now() - timedelta(hours=1)
        pin_data = {
            'email': 'test@pd15.org',
            'pin': '123456',
            'expires_at': past_time.isoformat(),
            'created_at': past_time.isoformat()
        }
        
        mock_load_pins.return_value = [pin_data]
        
        result = auth._verify_pin('test@pd15.org', '123456')
        assert result is False
    
    @patch('modules.auth.AuthManager._load_pins')
    def test_verify_pin_wrong_pin(self, mock_load_pins):
        """Test PIN verification with wrong PIN"""
        auth = AuthManager()
        
        # Mock valid PIN data
        current_time = datetime.now()
        future_time = current_time + timedelta(minutes=30)
        
        pin_data = {
            'email': 'test@pd15.org',
            'pin': '123456',
            'expires_at': future_time.isoformat(),
            'created_at': current_time.isoformat()
        }
        
        mock_load_pins.return_value = [pin_data]
        
        # Try with wrong PIN
        result = auth._verify_pin('test@pd15.org', '654321')
        assert result is False
    
    @patch('modules.auth.AuthManager._load_pins')
    def test_verify_pin_no_pin_found(self, mock_load_pins):
        """Test PIN verification when no PIN exists for email"""
        auth = AuthManager()
        mock_load_pins.return_value = []
        
        result = auth._verify_pin('test@pd15.org', '123456')
        assert result is False
    
    @patch('modules.auth.smtplib.SMTP')
    def test_send_pin_email_success(self, mock_smtp):
        """Test successful PIN email sending"""
        auth = AuthManager()
        
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        with patch.dict(os.environ, {'SMTP_USERNAME': 'test@example.com', 'SMTP_PASSWORD': 'password'}):
            result = auth._send_pin_email('user@pd15.org', '123456')
            
            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
    
    @patch('modules.auth.smtplib.SMTP')
    def test_send_pin_email_failure(self, mock_smtp):
        """Test PIN email sending failure"""
        auth = AuthManager()
        
        # Mock SMTP failure
        mock_smtp.side_effect = Exception("SMTP Error")
        
        with patch.dict(os.environ, {'SMTP_USERNAME': 'test@example.com', 'SMTP_PASSWORD': 'password'}):
            result = auth._send_pin_email('user@pd15.org', '123456')
            
            assert result is False
    
    def test_send_pin_email_missing_credentials(self):
        """Test PIN email sending with missing SMTP credentials"""
        auth = AuthManager()
        
        # Remove SMTP credentials from environment
        with patch.dict(os.environ, {}, clear=True):
            result = auth._send_pin_email('user@pd15.org', '123456')
            
            assert result is False
    
    def test_request_access_invalid_domain(self):
        """Test access request with invalid domain"""
        auth = AuthManager()
        
        result = auth.request_access('user@gmail.com', 'John', 'Doe')
        
        assert result == (False, "❌ Email domain not authorized. Use @pd15.org or @pd15.state.fl.us email.")
    
    @patch('modules.auth.AuthManager._load_users')
    def test_request_access_existing_user(self, mock_load_users):
        """Test access request for existing user"""
        auth = AuthManager()
        
        existing_user = SAMPLE_USERS["valid_user"]
        mock_load_users.return_value = [existing_user]
        
        result = auth.request_access('john.doe@pd15.org', 'John', 'Doe')
        
        assert result[0] is False
        assert "already has an account" in result[1]


class TestAuthManagerIntegration:
    """Integration tests for AuthManager"""
    
    @patch('modules.auth.AuthManager._send_pin_email')
    @patch('modules.auth.AuthManager._load_users')
    def test_full_authentication_flow(self, mock_load_users, mock_send_email):
        """Test complete authentication flow"""
        auth = AuthManager()
        
        # Setup mocks
        mock_load_users.return_value = []
        mock_send_email.return_value = True
        
        # Request access
        with patch.object(auth, '_save_pending_user') as mock_save_pending:
            result = auth.request_access('user@pd15.org', 'Test', 'User')
            assert result[0] is True
            mock_save_pending.assert_called_once()
    
    def test_auth_with_environment_variables(self):
        """Test AuthManager with environment variables"""
        env_vars = {
            'JWT_SECRET': 'test-secret',
            'SMTP_USERNAME': 'smtp@example.com',
            'SMTP_PASSWORD': 'smtp-password'
        }
        
        with patch.dict(os.environ, env_vars):
            auth = AuthManager()
            
            assert auth.jwt_secret == 'test-secret'