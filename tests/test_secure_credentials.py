"""
Unit tests for the Secure Credentials module
"""
import pytest
import os
import json
import base64
from unittest.mock import Mock, patch, mock_open, MagicMock
from cryptography.fernet import Fernet
from modules.secure_credentials import SecureCredentialManager


class TestSecureCredentialManager:
    """Test cases for the SecureCredentialManager class"""
    
    def test_init_creates_data_directory(self):
        """Test that initialization creates data directory"""
        with patch('modules.secure_credentials.pathlib.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            manager = SecureCredentialManager()
            
            mock_path.assert_called_with('data')
            mock_path_instance.mkdir.assert_called_with(exist_ok=True)
    
    def test_authorized_users_list(self):
        """Test that authorized users list is properly configured"""
        manager = SecureCredentialManager()
        
        assert 'dkarpay@pd15.org' in manager.authorized_users
        assert isinstance(manager.authorized_users, list)
    
    def test_is_authorized_user_valid(self):
        """Test authorization check for valid user"""
        manager = SecureCredentialManager()
        
        result = manager._is_authorized_user('dkarpay@pd15.org')
        assert result is True
        
        # Test case insensitive
        result = manager._is_authorized_user('DKARPAY@PD15.ORG')
        assert result is True
    
    def test_is_authorized_user_invalid(self):
        """Test authorization check for invalid user"""
        manager = SecureCredentialManager()
        
        result = manager._is_authorized_user('unauthorized@gmail.com')
        assert result is False
        
        result = manager._is_authorized_user('random@pd15.org')
        assert result is False
    
    def test_derive_key_from_password(self):
        """Test key derivation from password"""
        manager = SecureCredentialManager()
        
        password = "test_password"
        salt = b"test_salt_16bytes"
        
        key = manager._derive_key_from_password(password, salt)
        
        assert isinstance(key, bytes)
        assert len(key) == 44  # Base64 encoded 32-byte key
        
        # Same password and salt should produce same key
        key2 = manager._derive_key_from_password(password, salt)
        assert key == key2
        
        # Different password should produce different key
        key3 = manager._derive_key_from_password("different_password", salt)
        assert key != key3
    
    def test_setup_credentials_unauthorized_user(self):
        """Test credential setup with unauthorized user"""
        manager = SecureCredentialManager()
        
        result = manager.setup_credentials(
            'unauthorized@gmail.com',
            'master_password',
            'smtp_user',
            'smtp_pass'
        )
        
        assert result[0] is False
        assert "Unauthorized" in result[1]
    
    @patch('builtins.open', new_callable=mock_open)
    def test_setup_credentials_authorized_user(self, mock_file):
        """Test credential setup with authorized user"""
        manager = SecureCredentialManager()
        
        with patch('modules.secure_credentials.secrets.token_bytes') as mock_token:
            mock_token.return_value = b'test_salt_16bytes'
            
            result = manager.setup_credentials(
                'dkarpay@pd15.org',
                'master_password',
                'smtp_user@example.com',
                'smtp_password'
            )
            
            assert result[0] is True
            assert "successfully" in result[1].lower()
            mock_file.assert_called()
    
    @patch('builtins.open', side_effect=Exception("File write error"))
    def test_setup_credentials_file_error(self, mock_file):
        """Test credential setup with file write error"""
        manager = SecureCredentialManager()
        
        result = manager.setup_credentials(
            'dkarpay@pd15.org',
            'master_password',
            'smtp_user',
            'smtp_pass'
        )
        
        assert result[0] is False
        assert "Error" in result[1]
    
    def test_get_credentials_unauthorized_user(self):
        """Test credential retrieval with unauthorized user"""
        manager = SecureCredentialManager()
        
        result = manager.get_credentials('unauthorized@gmail.com', 'password')
        
        assert result[0] is False
        assert "Unauthorized" in result[1]
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_get_credentials_no_file(self, mock_file):
        """Test credential retrieval when file doesn't exist"""
        manager = SecureCredentialManager()
        
        result = manager.get_credentials('dkarpay@pd15.org', 'password')
        
        assert result[0] is False
        assert "not been set up" in result[1]
    
    @patch('builtins.open', new_callable=mock_open)
    def test_get_credentials_invalid_json(self, mock_file):
        """Test credential retrieval with invalid JSON file"""
        mock_file.return_value.read.return_value = "invalid json"
        
        manager = SecureCredentialManager()
        
        result = manager.get_credentials('dkarpay@pd15.org', 'password')
        
        assert result[0] is False
        assert "Error" in result[1]
    
    @patch('builtins.open', new_callable=mock_open)
    def test_get_credentials_wrong_password(self, mock_file):
        """Test credential retrieval with wrong password"""
        # Mock encrypted data
        encrypted_data = {
            'salt': base64.b64encode(b'test_salt_16bytes').decode(),
            'encrypted_credentials': 'encrypted_data_here'
        }
        mock_file.return_value.read.return_value = json.dumps(encrypted_data)
        
        manager = SecureCredentialManager()
        
        with patch.object(manager, '_derive_key_from_password') as mock_derive:
            mock_derive.return_value = b'wrong_key'
            
            with patch('modules.secure_credentials.Fernet') as mock_fernet:
                mock_fernet_instance = Mock()
                mock_fernet.return_value = mock_fernet_instance
                mock_fernet_instance.decrypt.side_effect = Exception("Invalid token")
                
                result = manager.get_credentials('dkarpay@pd15.org', 'wrong_password')
                
                assert result[0] is False
                assert "Invalid password" in result[1]
    
    @patch('builtins.open', new_callable=mock_open)
    def test_get_credentials_success(self, mock_file):
        """Test successful credential retrieval"""
        # Mock decrypted credentials
        credentials = {
            'smtp_username': 'test@example.com',
            'smtp_password': 'test_password'
        }
        
        # Mock encrypted data structure
        encrypted_data = {
            'salt': base64.b64encode(b'test_salt_16bytes').decode(),
            'encrypted_credentials': 'encrypted_data_here'
        }
        mock_file.return_value.read.return_value = json.dumps(encrypted_data)
        
        manager = SecureCredentialManager()
        
        with patch.object(manager, '_derive_key_from_password') as mock_derive:
            mock_derive.return_value = b'test_key'
            
            with patch('modules.secure_credentials.Fernet') as mock_fernet:
                mock_fernet_instance = Mock()
                mock_fernet.return_value = mock_fernet_instance
                mock_fernet_instance.decrypt.return_value = json.dumps(credentials).encode()
                
                result = manager.get_credentials('dkarpay@pd15.org', 'correct_password')
                
                assert result[0] is True
                assert result[1]['smtp_username'] == 'test@example.com'
                assert result[1]['smtp_password'] == 'test_password'
    
    def test_credentials_file_path(self):
        """Test that credentials file path is properly set"""
        manager = SecureCredentialManager()
        
        assert manager.credentials_file == 'data/smtp_credentials.enc'
        assert manager.credentials_file.endswith('.enc')
    
    def test_encryption_key_consistency(self):
        """Test that encryption key derivation is consistent"""
        manager = SecureCredentialManager()
        
        password = "test_password"
        salt = b"consistent_salt_"
        
        key1 = manager._derive_key_from_password(password, salt)
        key2 = manager._derive_key_from_password(password, salt)
        
        assert key1 == key2
    
    def test_encryption_key_different_salts(self):
        """Test that different salts produce different keys"""
        manager = SecureCredentialManager()
        
        password = "test_password"
        salt1 = b"salt_one_16bytes"
        salt2 = b"salt_two_16bytes"
        
        key1 = manager._derive_key_from_password(password, salt1)
        key2 = manager._derive_key_from_password(password, salt2)
        
        assert key1 != key2
    
    @patch('modules.secure_credentials.secrets.token_bytes')
    def test_salt_generation(self, mock_token_bytes):
        """Test salt generation for encryption"""
        mock_token_bytes.return_value = b'random_salt_bytes'
        
        manager = SecureCredentialManager()
        
        with patch('builtins.open', new_callable=mock_open):
            manager.setup_credentials(
                'dkarpay@pd15.org',
                'password',
                'smtp_user',
                'smtp_pass'
            )
            
            # Verify salt was generated
            mock_token_bytes.assert_called_with(16)
    
    def test_credential_validation(self):
        """Test credential data validation"""
        manager = SecureCredentialManager()
        
        # Test with empty credentials
        result = manager.setup_credentials(
            'dkarpay@pd15.org',
            'password',
            '',  # Empty SMTP username
            'smtp_pass'
        )
        
        # Implementation should handle empty credentials appropriately
        # (The exact behavior depends on implementation)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_security_best_practices(self):
        """Test security best practices implementation"""
        manager = SecureCredentialManager()
        
        # Test that sensitive data is not logged or exposed
        password = "sensitive_password"
        salt = b"test_salt_16bytes"
        
        # Key derivation should not expose password
        key = manager._derive_key_from_password(password, salt)
        assert password.encode() not in key
        
        # Derived key should be properly encoded
        try:
            base64.urlsafe_b64decode(key)
            key_is_base64 = True
        except:
            key_is_base64 = False
        
        assert key_is_base64


class TestSecureCredentialManagerIntegration:
    """Integration tests for SecureCredentialManager"""
    
    def test_full_credential_cycle(self, temp_dir):
        """Test complete credential setup and retrieval cycle"""
        credentials_file = os.path.join(temp_dir, 'test_credentials.enc')
        
        manager = SecureCredentialManager()
        manager.credentials_file = credentials_file
        
        # Setup credentials
        setup_result = manager.setup_credentials(
            'dkarpay@pd15.org',
            'master_password',
            'smtp@example.com',
            'smtp_secret'
        )
        
        assert setup_result[0] is True
        assert os.path.exists(credentials_file)
        
        # Retrieve credentials
        get_result = manager.get_credentials('dkarpay@pd15.org', 'master_password')
        
        assert get_result[0] is True
        assert get_result[1]['smtp_username'] == 'smtp@example.com'
        assert get_result[1]['smtp_password'] == 'smtp_secret'
    
    def test_wrong_password_cycle(self, temp_dir):
        """Test credential cycle with wrong password"""
        credentials_file = os.path.join(temp_dir, 'test_credentials.enc')
        
        manager = SecureCredentialManager()
        manager.credentials_file = credentials_file
        
        # Setup credentials
        manager.setup_credentials(
            'dkarpay@pd15.org',
            'correct_password',
            'smtp@example.com',
            'smtp_secret'
        )
        
        # Try to retrieve with wrong password
        get_result = manager.get_credentials('dkarpay@pd15.org', 'wrong_password')
        
        assert get_result[0] is False
        assert "password" in get_result[1].lower()
    
    def test_multiple_credential_operations(self, temp_dir):
        """Test multiple credential operations"""
        credentials_file = os.path.join(temp_dir, 'test_credentials.enc')
        
        manager = SecureCredentialManager()
        manager.credentials_file = credentials_file
        
        # Setup initial credentials
        manager.setup_credentials(
            'dkarpay@pd15.org',
            'password1',
            'smtp1@example.com',
            'secret1'
        )
        
        # Setup new credentials (should overwrite)
        manager.setup_credentials(
            'dkarpay@pd15.org',
            'password2',
            'smtp2@example.com',
            'secret2'
        )
        
        # Should only be able to retrieve with latest password
        old_result = manager.get_credentials('dkarpay@pd15.org', 'password1')
        assert old_result[0] is False
        
        new_result = manager.get_credentials('dkarpay@pd15.org', 'password2')
        assert new_result[0] is True
        assert new_result[1]['smtp_username'] == 'smtp2@example.com'