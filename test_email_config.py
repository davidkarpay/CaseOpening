#!/usr/bin/env python3
"""
Quick email configuration test script
Run this to verify email settings are working correctly
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv is installed and loaded")
except ImportError:
    print("❌ python-dotenv not installed. Run: pip install python-dotenv")

def test_email_config():
    """Test email configuration"""
    print("\n🔍 Email Configuration Test")
    print("=" * 40)
    
    # Check environment variables
    mock_mode = os.environ.get('EMAIL_MOCK_MODE', '').lower()
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = os.environ.get('SMTP_PORT')
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    jwt_secret = os.environ.get('JWT_SECRET')
    
    print(f"Mock Mode: {mock_mode}")
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP Username: {smtp_username}")
    print(f"SMTP Password: {'*' * len(smtp_password) if smtp_password else 'Not set'}")
    print(f"JWT Secret: {'Set' if jwt_secret else 'Not set'}")
    
    print("\n📋 Configuration Status:")
    print("=" * 40)
    
    if mock_mode == 'true':
        print("✅ Mock mode is ENABLED")
        print("   → Verification codes will display in the UI")
        print("   → No real emails will be sent")
        print("   → Perfect for development and testing")
    elif mock_mode == 'false':
        print("⚠️  Mock mode is DISABLED")
        print("   → Real emails will be attempted")
        if smtp_username and smtp_password:
            print("   ✅ SMTP credentials are set")
        else:
            print("   ❌ SMTP credentials are missing")
            print("   → Check .env file or use secure credential storage")
    else:
        print("❓ Mock mode not set")
        print("   → Defaulting to production mode")
        print("   → May cause email sending errors")
    
    # Check for .env file
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"✅ .env file exists: {env_file}")
    else:
        print(f"❌ .env file not found: {env_file}")
    
    # Check secure credentials
    creds_file = project_root / 'data' / 'smtp_credentials.enc'
    if creds_file.exists():
        print(f"✅ Encrypted credentials exist: {creds_file}")
    else:
        print(f"❌ No encrypted credentials: {creds_file}")
    
    print("\n🎯 Recommendations:")
    print("=" * 40)
    
    if mock_mode == 'true':
        print("✅ Configuration looks good for development!")
        print("   1. Restart Streamlit application")
        print("   2. Try registering with your @pd15.org email")
        print("   3. Look for verification code in the UI")
    else:
        print("⚠️  For development, consider enabling mock mode:")
        print("   1. Set EMAIL_MOCK_MODE=true in .env file")
        print("   2. Restart Streamlit application")
        print("   3. This will display codes instead of sending emails")

def test_auth_import():
    """Test importing auth module"""
    print("\n🔧 Auth Module Test")
    print("=" * 40)
    
    try:
        from modules.auth import AuthManager
        auth = AuthManager()
        print("✅ AuthManager imported successfully")
        
        # Test domain validation
        test_email = "dkarpay@pd15.org"
        if auth._is_allowed_email_domain(test_email):
            print(f"✅ Domain validation works: {test_email}")
        else:
            print(f"❌ Domain validation failed: {test_email}")
            
    except Exception as e:
        print(f"❌ Error importing AuthManager: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("📧 Case Opening Sheet Manager - Email Configuration Test")
    print("=" * 60)
    
    test_email_config()
    test_auth_import()
    
    print("\n" + "=" * 60)
    print("🔄 Next Steps:")
    print("1. If mock mode is enabled, restart Streamlit and try registering")
    print("2. If you see issues, check the troubleshooting guide: EMAIL_TROUBLESHOOTING.md")
    print("3. For production email setup, use the Settings page in the app")