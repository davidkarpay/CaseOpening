"""
Settings page for Case Opening Sheet Manager
"""
import streamlit as st
import os
from modules.secure_credentials import SecureCredentialManager


def show_settings_page():
    """Display the settings page"""
    st.header("⚙️ System Settings")
    
    st.subheader("🔐 Secure SMTP Credentials")
    st.info("Configure encrypted email credentials for production use")
    
    cred_manager = SecureCredentialManager()
    
    if cred_manager.credentials_exist():
        st.success("✅ Secure SMTP credentials are configured")
        st.info("Use the sidebar to unlock credentials when needed")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reconfigure Credentials", type="secondary"):
                # Show reconfiguration option
                st.warning("⚠️ This will replace existing encrypted credentials")
                cred_manager.show_credential_setup_ui()
        
        with col2:
            if st.button("🗑️ Remove Credentials", type="secondary"):
                st.error("⚠️ To remove credentials, delete the file `data/smtp_credentials.enc` manually")
                st.code("rm data/smtp_credentials.enc")
    else:
        st.warning("⚠️ No secure SMTP credentials configured")
        cred_manager.show_credential_setup_ui()
    
    st.divider()
    
    st.subheader("📧 Email Configuration Status")
    
    # Show current configuration
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mock Mode", "✅ Enabled" if os.environ.get('EMAIL_MOCK_MODE', '').lower() == 'true' else "❌ Disabled")
        st.metric("Secure Storage", "✅ Available" if cred_manager.credentials_exist() else "❌ Not Set Up")
    
    with col2:
        st.metric("Session Unlocked", "✅ Yes" if st.session_state.get('smtp_unlocked', False) else "❌ No")
        st.metric("Environment SMTP", "✅ Set" if os.environ.get('SMTP_USERNAME') else "❌ Not Set")
    
    st.divider()
    
    st.subheader("💡 Configuration Help")
    
    with st.expander("🔧 Development Setup"):
        st.code("""
# For development/testing (no real emails sent)
EMAIL_MOCK_MODE=true
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
JWT_SECRET=your-dev-secret
        """)
        st.info("With mock mode enabled, verification codes are shown in the UI instead of sending real emails")
    
    with st.expander("🏢 Production Setup"):
        st.markdown("""
        **For production deployment:**
        1. Set up secure SMTP credentials using the form above
        2. Set `EMAIL_MOCK_MODE=false` in your environment
        3. Ensure your master password is secure and memorable
        4. Only authorized administrators can configure credentials
        """)
    
    with st.expander("🔒 Security Features"):
        st.markdown("""
        **Secure credential storage includes:**
        - PBKDF2 encryption with 100,000 iterations
        - Random salt for each credential set  
        - Master password required for decryption
        - Access restricted to authorized users only
        - Credentials cleared from memory on logout
        - No plaintext storage of SMTP passwords
        """)