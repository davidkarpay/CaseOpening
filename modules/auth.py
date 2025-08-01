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
            # Use Office365 SMTP server for pd15.org/pd15.state.fl.us domain
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp-mail.outlook.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            
            # Organization email credentials (should be set by admin)
            smtp_username = os.environ.get('SMTP_USERNAME')  # e.g., 'casemanager@pd15.org'
            smtp_password = os.environ.get('SMTP_PASSWORD')
            
            if not all([smtp_username, smtp_password]):
                st.error("Email service not configured. Please contact your system administrator.")
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
    
    def register_user(self, username: str, password: str, email: str) -> Tuple[bool, str]:
        """Register a new user with email verification"""
        self._cleanup_expired_data()
        
        # Validate email domain
        if not self._is_allowed_email_domain(email):
            return False, "Registration is restricted to members of the 15th Judicial Circuit's Public Defender Office. Please use your @pd15.org or @pd15.state.fl.us email address."
        
        # Check if user already exists
        users = self._load_json(self.users_file)
        if f"user:{username}" in users:
            return False, "Username already exists."
        
        # Check if email already registered
        for user_data in users.values():
            if user_data.get('email', '').lower() == email.lower():
                return False, "Email already registered."
        
        # Generate verification code
        verification_code = self._generate_pin()
        code_expiry = int(time.time() * 1000) + (10 * 60 * 1000)  # 10 minutes
        
        # Create pending user
        salt = self._generate_salt()
        pending_user = {
            'id': secrets.token_hex(16),
            'username': username,
            'password': self._hash_password(password, salt),
            'salt': salt,
            'email': email,
            'verified': False,
            'verificationCode': verification_code,
            'codeExpiry': code_expiry,
            'createdAt': datetime.now().isoformat()
        }
        
        # Save pending user
        pending_users = self._load_json(self.pending_users_file)
        pending_users[f"pending:{username}"] = pending_user
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
    
    def verify_registration(self, username: str, code: str) -> Tuple[bool, str]:
        """Verify user registration with email code"""
        self._cleanup_expired_data()
        
        pending_users = self._load_json(self.pending_users_file)
        pending_key = f"pending:{username}"
        
        if pending_key not in pending_users:
            return False, "No pending registration found for this username."
        
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
            'username': pending_user['username'],
            'password': pending_user['password'],
            'salt': pending_user['salt'],
            'email': pending_user['email'],
            'verified': True,
            'createdAt': pending_user['createdAt'],
            'lastLogin': datetime.now().isoformat()
        }
        
        users = self._load_json(self.users_file)
        users[f"user:{username}"] = user
        self._save_json(self.users_file, users)
        
        # Remove from pending
        del pending_users[pending_key]
        self._save_json(self.pending_users_file, pending_users)
        
        return True, "Account verified successfully! You can now log in."
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """Authenticate user with username and password"""
        users = self._load_json(self.users_file)
        user_key = f"user:{username}"
        
        if user_key not in users:
            return False, "Invalid username or password.", None
        
        user = users[user_key]
        
        # Verify password
        if user['password'] != self._hash_password(password, user['salt']):
            return False, "Invalid username or password.", None
        
        # Update last login
        user['lastLogin'] = datetime.now().isoformat()
        users[user_key] = user
        self._save_json(self.users_file, users)
        
        # Generate JWT token
        token = self._generate_jwt(user['id'])
        
        return True, "Login successful!", token
    
    def request_login_pin(self, username: str) -> Tuple[bool, str]:
        """Request login PIN for quick access"""
        users = self._load_json(self.users_file)
        user_key = f"user:{username}"
        
        if user_key not in users:
            return False, "Username not found."
        
        user = users[user_key]
        
        # Generate PIN
        pin = self._generate_pin()
        pin_expiry = int(time.time() * 1000) + (5 * 60 * 1000)  # 5 minutes
        
        # Save PIN
        pins = self._load_json(self.pins_file)
        pins[f"pin:{username}"] = {
            'pin': pin,
            'expiry': pin_expiry,
            'userId': user['id']
        }
        self._save_json(self.pins_file, pins)
        
        # Send PIN email
        subject = "Case Opening Sheet Manager - Login PIN"
        message = f"""Your login PIN is: {pin}

This PIN expires in 5 minutes.

If you did not request this PIN, please ignore this email.

Best regards,
15th Judicial Circuit Public Defender's Office"""
        
        if self._send_email(user['email'], subject, message):
            return True, "PIN sent to your email address."
        else:
            return False, "Failed to send PIN. Please try again."
    
    def verify_login_pin(self, username: str, pin: str) -> Tuple[bool, str, Optional[str]]:
        """Verify login PIN and return JWT token"""
        self._cleanup_expired_data()
        
        pins = self._load_json(self.pins_file)
        pin_key = f"pin:{username}"
        
        if pin_key not in pins:
            return False, "No PIN request found for this username.", None
        
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