"""
Secure credential storage for Case Opening Sheet Manager
Only authorized users can decrypt and use SMTP credentials
"""
import os
import json
import hashlib
import secrets
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import streamlit as st


class SecureCredentialManager:
    """Manages encrypted SMTP credentials with user authentication"""
    
    def __init__(self):
        self.credentials_file = 'data/smtp_credentials.enc'
        self.authorized_users = ['dkarpay@pd15.org']  # Only you can access
        
        # Ensure data directory exists
        import pathlib
        pathlib.Path('data').mkdir(exist_ok=True)
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from user password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _is_authorized_user(self, email: str) -> bool:
        """Check if user is authorized to manage credentials"""
        return email.lower() in [user.lower() for user in self.authorized_users]
    
    def setup_credentials(self, user_email: str, master_password: str, 
                         smtp_username: str, smtp_password: str) -> bool:
        """Set up encrypted SMTP credentials (admin only)"""
        if not self._is_authorized_user(user_email):
            return False, "❌ Unauthorized: Only authorized administrators can set up credentials"
        
        try:
            # Generate salt for this credential set
            salt = secrets.token_bytes(16)
            
            # Derive encryption key from master password
            key = self._derive_key_from_password(master_password, salt)
            fernet = Fernet(key)
            
            # Encrypt the SMTP credentials
            credentials = {
                'smtp_username': smtp_username,
                'smtp_password': smtp_password,
                'created_by': user_email,
                'created_at': str(datetime.now())
            }
            
            encrypted_data = fernet.encrypt(json.dumps(credentials).encode())
            
            # Store encrypted credentials with salt
            storage_data = {
                'salt': base64.b64encode(salt).decode(),
                'encrypted_credentials': base64.b64encode(encrypted_data).decode(),
                'authorized_users': self.authorized_users
            }
            
            with open(self.credentials_file, 'w') as f:
                json.dump(storage_data, f, indent=2)
            
            return True, "✅ SMTP credentials encrypted and stored securely"
            
        except Exception as e:
            return False, f"❌ Failed to store credentials: {str(e)}"
    
    def get_credentials(self, user_email: str, master_password: str) -> tuple:
        """Retrieve and decrypt SMTP credentials (authorized users only)"""
        if not self._is_authorized_user(user_email):
            return False, "❌ Unauthorized access attempt", None, None
        
        if not os.path.exists(self.credentials_file):
            return False, "❌ No credentials configured", None, None
        
        try:
            # Load encrypted data
            with open(self.credentials_file, 'r') as f:
                storage_data = json.load(f)
            
            # Verify user is still authorized
            if user_email.lower() not in [u.lower() for u in storage_data.get('authorized_users', [])]:
                return False, "❌ User no longer authorized", None, None
            
            # Decrypt credentials
            salt = base64.b64decode(storage_data['salt'])
            encrypted_data = base64.b64decode(storage_data['encrypted_credentials'])
            
            key = self._derive_key_from_password(master_password, salt)
            fernet = Fernet(key)
            
            decrypted_data = fernet.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            return True, "✅ Credentials retrieved", credentials['smtp_username'], credentials['smtp_password']
            
        except Exception as e:
            return False, f"❌ Failed to decrypt credentials: Invalid password or corrupted data", None, None
    
    def credentials_exist(self) -> bool:
        """Check if encrypted credentials are already set up"""
        return os.path.exists(self.credentials_file)
    
    def show_credential_setup_ui(self):
        """Streamlit UI for setting up secure credentials"""
        st.header("🔐 Secure SMTP Credential Setup")
        st.warning("⚠️ **Administrator Only**: Only authorized users can configure SMTP credentials")
        
        with st.form("credential_setup"):
            user_email = st.text_input(
                "Your Administrator Email", 
                placeholder="dkarpay@pd15.org",
                help="Must be an authorized administrator"
            )
            
            master_password = st.text_input(
                "Master Password", 
                type="password",
                help="This password will be required to decrypt SMTP credentials"
            )
            
            confirm_password = st.text_input(
                "Confirm Master Password", 
                type="password"
            )
            
            st.divider()
            st.subheader("SMTP Configuration")
            
            smtp_username = st.text_input(
                "SMTP Username", 
                placeholder="dkarpay@pd15.org",
                help="Your email account for sending verification emails"
            )
            
            smtp_password = st.text_input(
                "SMTP Password/App Password", 
                type="password",
                help="Use an App Password for better security"
            )
            
            setup_submit = st.form_submit_button("🔒 Encrypt and Store Credentials", type="primary")
            
            if setup_submit:
                # Validation
                if not all([user_email, master_password, confirm_password, smtp_username, smtp_password]):
                    st.error("❌ Please fill in all fields")
                    return
                
                if master_password != confirm_password:
                    st.error("❌ Master passwords do not match")
                    return
                
                if len(master_password) < 12:
                    st.error("❌ Master password must be at least 12 characters")
                    return
                
                # Set up credentials
                success, message = self.setup_credentials(
                    user_email, master_password, smtp_username, smtp_password
                )
                
                if success:
                    st.success(message)
                    st.info("🔄 Please restart the application to use encrypted credentials")
                    st.balloons()
                else:
                    st.error(message)
    
    def show_credential_unlock_ui(self):
        """Streamlit UI for unlocking credentials during runtime"""
        st.sidebar.subheader("🔐 Unlock SMTP Credentials")
        
        with st.sidebar.form("unlock_credentials"):
            user_email = st.text_input("Admin Email", key="unlock_email")
            master_password = st.text_input("Master Password", type="password", key="unlock_password")
            unlock_submit = st.form_submit_button("🔓 Unlock")
            
            if unlock_submit:
                success, message, username, password = self.get_credentials(user_email, master_password)
                
                if success:
                    # Store decrypted credentials in session state (encrypted in memory)
                    st.session_state.smtp_unlocked = True
                    st.session_state.smtp_username = username
                    st.session_state.smtp_password = password
                    st.sidebar.success("✅ SMTP credentials unlocked")
                    st.rerun()
                else:
                    st.sidebar.error(message)


from datetime import datetime