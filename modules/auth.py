"""
Authentication module for Case Opening Sheet Manager
Implements email verification, time-limited PIN codes, JWT tokens, and domain restrictions
"""
import hashlib
import hmac
import base64
import json
import secrets
import time
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Tuple
import streamlit as st
from modules.secure_credentials import SecureCredentialManager

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    import pathlib
    # Load from the project root directory
    env_path = pathlib.Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # dotenv not installed, environment variables must be set manually
    pass


class AuthManager:
    """Handles authentication for the Case Opening Sheet Manager"""
    
    def __init__(self):
        self.allowed_domains = ['@pd15.org', '@pd15.state.fl.us']
        self.jwt_secret = os.environ.get('JWT_SECRET', 'case-opening-jwt-secret-key')
        self.users_file = 'data/users.json'
        self.pending_users_file = 'data/pending_users.json'
        self.pins_file = 'data/login_pins.json'
        
        # Ensure data directory exists
        import pathlib
        pathlib.Path('data').mkdir(exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage files if they don't exist"""
        for file_path in [self.users_file, self.pending_users_file, self.pins_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def _load_json(self, file_path: str) -> dict:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: str, data: dict):
        """Save JSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_salt(self) -> str:
        """Generate random salt"""
        return secrets.token_hex(32)
    
    def _generate_pin(self) -> str:
        """Generate 6-digit PIN"""
        return str(secrets.randbelow(900000) + 100000)
    
    def _is_allowed_email_domain(self, email: str) -> bool:
        """Check if email domain is allowed"""
        email_lower = email.lower()
        return any(email_lower.endswith(domain) for domain in self.allowed_domains)
    
    def _send_email(self, to_email: str, subject: str, message: str) -> bool:
        """Send email using organization's Outlook/Office365 SMTP server"""
        try:
            # Check for development/mock mode
            if os.environ.get('EMAIL_MOCK_MODE', '').lower() == 'true':
                # Mock mode for development - just log the email instead of sending
                print(f"\n=== MOCK EMAIL ===")
                print(f"To: {to_email}")
                print(f"Subject: {subject}")
                print(f"Message:\n{message}")
                print(f"==================\n")
                
                # Extract PIN/code from message for display
                import re
                code_match = re.search(r'(?:PIN is|code is|Code):\s*(\d{6})', message)
                if code_match:
                    code = code_match.group(1)
                    st.success(f"📧 **Development Mode**: Email sent to {to_email}")
                    st.info(f"🔑 **Your Code**: {code}")
                    st.warning("⚠️ **Remember this code** - you'll need it on the next screen!")
                else:
                    st.info(f"📧 **Development Mode**: Email sent to {to_email}")
                    st.code(f"Subject: {subject}\n\n{message}")
                return True
            
            # Use Office365 SMTP server for pd15.org/pd15.state.fl.us domain
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp-mail.outlook.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            
            # Try to get credentials from secure storage first
            smtp_username = None
            smtp_password = None
            
            # Check if credentials are unlocked in session state
            if st.session_state.get('smtp_unlocked', False):
                smtp_username = st.session_state.get('smtp_username')
                smtp_password = st.session_state.get('smtp_password')
            
            # Fallback to environment variables if not using secure storage
            if not all([smtp_username, smtp_password]):
                smtp_username = os.environ.get('SMTP_USERNAME')
                smtp_password = os.environ.get('SMTP_PASSWORD')
            
            if not all([smtp_username, smtp_password]):
                # Check if secure credentials are set up
                cred_manager = SecureCredentialManager()
                if cred_manager.credentials_exist():
                    st.error("🔒 SMTP credentials are encrypted. Please unlock them in the sidebar.")
                    cred_manager.show_credential_unlock_ui()
                else:
                    st.error("Email service not configured. Please contact your system administrator.")
                    st.info("💡 **For development**: Add `EMAIL_MOCK_MODE=true` to your .env file to enable mock email mode.")
                    st.info("🔐 **For production**: Go to the **Settings** page to configure secure credentials.")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = f"Case Opening Sheet Manager <{smtp_username}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add organization signature
            full_message = f"{message}\n\n---\n15th Judicial Circuit Public Defender's Office\nCase Opening Sheet Manager\nThis is an automated message."
            
            msg.attach(MIMEText(full_message, 'plain'))
            
            # Connect and send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            st.error(f"Failed to send verification email. Please contact your system administrator. Error: {str(e)}")
            return False
    
    def _generate_jwt(self, user_id: str) -> str:
        """Generate JWT token"""
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + (24 * 60 * 60)  # 24 hours
        }
        
        # Encode header and payload
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip('=')
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = hmac.new(
            self.jwt_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        return f"{header_encoded}.{payload_encoded}.{signature_encoded}"
    
    def _verify_jwt(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload if valid"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_encoded, payload_encoded, signature_encoded = parts
            
            # Verify signature
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = hmac.new(
                self.jwt_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            # Add padding if needed
            signature_encoded += '=' * (4 - len(signature_encoded) % 4)
            signature = base64.urlsafe_b64decode(signature_encoded)
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Decode payload
            payload_encoded += '=' * (4 - len(payload_encoded) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_encoded))
            
            # Check expiration
            if payload.get('exp', 0) < time.time():
                return None
            
            return payload
        except Exception:
            return None
    
    def _cleanup_expired_data(self):
        """Clean up expired pending users and PINs"""
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Clean expired pending users
        pending_users = self._load_json(self.pending_users_file)
        expired_keys = [
            key for key, user in pending_users.items()
            if user.get('codeExpiry', 0) < current_time
        ]
        for key in expired_keys:
            del pending_users[key]
        if expired_keys:
            self._save_json(self.pending_users_file, pending_users)
        
        # Clean expired PINs
        pins = self._load_json(self.pins_file)
        expired_keys = [
            key for key, pin_data in pins.items()
            if pin_data.get('expiry', 0) < current_time
        ]
        for key in expired_keys:
            del pins[key]
        if expired_keys:
            self._save_json(self.pins_file, pins)
    
    def register_user(self, email: str, password: str, email_confirm: str) -> Tuple[bool, str]:
        """Register a new user with email verification"""
        self._cleanup_expired_data()
        
        # Validate email domain
        if not self._is_allowed_email_domain(email):
            return False, "Registration is restricted to members of the 15th Judicial Circuit's Public Defender Office. Please use your @pd15.org or @pd15.state.fl.us email address."
        
        # Check if email already registered
        users = self._load_json(self.users_file)
        for user_data in users.values():
            if user_data.get('email', '').lower() == email.lower():
                return False, "Email already registered."
        
        # Generate verification code
        verification_code = self._generate_pin()
        code_expiry = int(time.time() * 1000) + (10 * 60 * 1000)  # 10 minutes
        
        # Create pending user - use email as username
        salt = self._generate_salt()
        pending_user = {
            'id': secrets.token_hex(16),
            'username': email,  # Use email as username
            'password': self._hash_password(password, salt),
            'salt': salt,
            'email': email,
            'verified': False,
            'verificationCode': verification_code,
            'codeExpiry': code_expiry,
            'createdAt': datetime.now().isoformat()
        }
        
        # Save pending user - use email as key
        pending_users = self._load_json(self.pending_users_file)
        pending_users[f"pending:{email.lower()}"] = pending_user
        self._save_json(self.pending_users_file, pending_users)
        
        # Send verification email
        subject = "Verify Your Case Opening Sheet Manager Account"
        message = f"""Welcome to the Case Opening Sheet Manager!

Your verification code is: {verification_code}

This code expires in 10 minutes. Please enter this code on the verification page to complete your registration.

If you did not request this registration, please ignore this email.

Best regards,
15th Judicial Circuit Public Defender's Office"""
        
        if self._send_email(email, subject, message):
            return True, "Registration successful! Please check your email for a verification code."
        else:
            return False, "Failed to send verification email. Please try again."
    
    def verify_registration(self, email: str, code: str) -> Tuple[bool, str]:
        """Verify user registration with email code"""
        self._cleanup_expired_data()
        
        pending_users = self._load_json(self.pending_users_file)
        pending_key = f"pending:{email.lower()}"
        
        if pending_key not in pending_users:
            return False, "No pending registration found for this email address."
        
        pending_user = pending_users[pending_key]
        
        # Check code expiry
        if pending_user.get('codeExpiry', 0) < time.time() * 1000:
            del pending_users[pending_key]
            self._save_json(self.pending_users_file, pending_users)
            return False, "Verification code has expired. Please register again."
        
        # Verify code
        if pending_user.get('verificationCode') != code:
            return False, "Invalid verification code."
        
        # Move user to active users
        user = {
            'id': pending_user['id'],
            'username': pending_user['username'],  # This is the email
            'password': pending_user['password'],
            'salt': pending_user['salt'],
            'email': pending_user['email'],
            'verified': True,
            'createdAt': pending_user['createdAt'],
            'lastLogin': datetime.now().isoformat()
        }
        
        users = self._load_json(self.users_file)
        users[f"user:{email.lower()}"] = user
        self._save_json(self.users_file, users)
        
        # Remove from pending
        del pending_users[pending_key]
        self._save_json(self.pending_users_file, pending_users)
        
        return True, "Account verified successfully! You can now log in."
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """Authenticate user with email and password"""
        users = self._load_json(self.users_file)
        
        # Find user by email
        user_found = None
        user_key = None
        for key, user in users.items():
            if user.get('email', '').lower() == email.lower():
                user_found = user
                user_key = key
                break
        
        if not user_found:
            return False, "Invalid email or password.", None
        
        # Verify password
        if user_found['password'] != self._hash_password(password, user_found['salt']):
            return False, "Invalid email or password.", None
        
        # Update last login
        user_found['lastLogin'] = datetime.now().isoformat()
        users[user_key] = user_found
        self._save_json(self.users_file, users)
        
        # Generate JWT token
        token = self._generate_jwt(user_found['id'])
        
        return True, "Login successful!", token
    
    def request_login_pin(self, email: str) -> Tuple[bool, str]:
        """Request login PIN for quick access"""
        users = self._load_json(self.users_file)
        
        # Find user by email
        user_found = None
        for user in users.values():
            if user.get('email', '').lower() == email.lower():
                user_found = user
                break
        
        if not user_found:
            return False, "Email address not found."
        
        # Generate PIN
        pin = self._generate_pin()
        pin_expiry = int(time.time() * 1000) + (5 * 60 * 1000)  # 5 minutes
        
        # Save PIN
        pins = self._load_json(self.pins_file)
        pins[f"pin:{email.lower()}"] = {
            'pin': pin,
            'expiry': pin_expiry,
            'userId': user_found['id']
        }
        self._save_json(self.pins_file, pins)
        
        # Send PIN email
        subject = "Case Opening Sheet Manager - Login PIN"
        message = f"""Your login PIN is: {pin}

This PIN expires in 5 minutes.

If you did not request this PIN, please ignore this email."""
        
        if self._send_email(user_found['email'], subject, message):
            return True, "PIN sent to your email address."
        else:
            return False, "Failed to send PIN. Please try again."
    
    def verify_login_pin(self, email: str, pin: str) -> Tuple[bool, str, Optional[str]]:
        """Verify login PIN and return JWT token"""
        self._cleanup_expired_data()
        
        pins = self._load_json(self.pins_file)
        pin_key = f"pin:{email.lower()}"
        
        if pin_key not in pins:
            return False, "No PIN request found for this email address.", None
        
        pin_data = pins[pin_key]
        
        # Check expiry
        if pin_data.get('expiry', 0) < time.time() * 1000:
            del pins[pin_key]
            self._save_json(self.pins_file, pins)
            return False, "PIN has expired. Please request a new one.", None
        
        # Verify PIN
        if pin_data.get('pin') != pin:
            return False, "Invalid PIN.", None
        
        # Update last login
        users = self._load_json(self.users_file)
        for user_key, user in users.items():
            if user['id'] == pin_data['userId']:
                user['lastLogin'] = datetime.now().isoformat()
                users[user_key] = user
                self._save_json(self.users_file, users)
                break
        
        # Clean up used PIN
        del pins[pin_key]
        self._save_json(self.pins_file, pins)
        
        # Generate JWT token
        token = self._generate_jwt(pin_data['userId'])
        
        return True, "Login successful!", token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user info"""
        payload = self._verify_jwt(token)
        if not payload:
            return None
        
        # Get user info
        users = self._load_json(self.users_file)
        for user in users.values():
            if user['id'] == payload['sub']:
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'verified': user['verified']
                }
        
        return None