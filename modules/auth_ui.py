"""
Authentication UI components for Streamlit
"""
import streamlit as st
from modules.auth import AuthManager


def show_login_page():
    """Display login/registration page"""
    auth = AuthManager()
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1>🔐 Case Opening Sheet Manager</h1>
        <h3>15th Judicial Circuit Public Defender's Office</h3>
        <p>Secure access for authorized personnel only</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different auth methods
    tab1, tab2, tab3, tab4 = st.tabs(["Email + Password", "Quick PIN Login", "Create Account", "Verify Account"])
    
    with tab1:
        show_login_form(auth)
    
    with tab2:
        show_pin_login_form(auth)
    
    with tab3:
        show_registration_form(auth)
    
    with tab4:
        show_verification_form(auth)


def show_login_form(auth: AuthManager):
    """Display email + password login form"""
    st.header("🔑 Email + Password Login")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your.name@pd15.org", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        submit = st.form_submit_button("Login", use_container_width=True, type="primary")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            
            success, message, token = auth.authenticate_user(email, password)
            
            if success:
                st.session_state.auth_token = token
                st.session_state.authenticated = True
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def show_pin_login_form(auth: AuthManager):
    """Display PIN-based login form"""
    st.header("📱 Quick PIN Login")
    st.info("Enter your email address to receive a 6-digit PIN")
    
    # PIN request form
    if 'pin_requested' not in st.session_state:
        st.session_state.pin_requested = False
    
    if not st.session_state.pin_requested:
        with st.form("pin_request_form"):
            email = st.text_input("Email Address", placeholder="your.name@pd15.org", key="pin_email")
            
            submit = st.form_submit_button("Send PIN to Email", use_container_width=True, type="primary")
            
            if submit:
                if not email:
                    st.error("Please enter your email address.")
                    return
                
                success, message = auth.request_login_pin(email)
                
                if success:
                    st.session_state.pin_requested = True
                    st.session_state.pin_email_stored = email
                    st.success(message)
                    
                    # In mock mode, add a brief delay so user can see the PIN
                    import os
                    if os.environ.get('EMAIL_MOCK_MODE', '').lower() == 'true':
                        import time
                        st.info("⏳ **Page will refresh in 3 seconds** - remember your PIN!")
                        time.sleep(3)
                    
                    st.rerun()
                else:
                    st.error(message)
    else:
        # PIN verification form
        st.success(f"PIN sent to your email address!")
        
        # Show helpful info in development mode
        import os
        if os.environ.get('EMAIL_MOCK_MODE', '').lower() == 'true':
            st.info("💡 **Development Mode**: The PIN was displayed above when you requested it")
        
        with st.form("pin_verify_form"):
            pin = st.text_input("Enter 6-digit PIN from email", key="verify_pin", max_chars=6)
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Verify PIN", use_container_width=True, type="primary")
            with col2:
                if st.form_submit_button("Request New PIN", use_container_width=True):
                    st.session_state.pin_requested = False
                    if 'pin_email_stored' in st.session_state:
                        del st.session_state.pin_email_stored
                    st.rerun()
            
            if submit:
                if not pin:
                    st.error("Please enter the PIN.")
                    return
                
                success, message, token = auth.verify_login_pin(
                    st.session_state.pin_email_stored, pin
                )
                
                if success:
                    st.session_state.auth_token = token
                    st.session_state.authenticated = True
                    st.session_state.pin_requested = False
                    if 'pin_email_stored' in st.session_state:
                        del st.session_state.pin_email_stored
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def show_registration_form(auth: AuthManager):
    """Display registration form"""
    st.header("📝 Create Account")
    st.warning("⚠️ Only @pd15.org and @pd15.state.fl.us email addresses are allowed")
    
    with st.form("registration_form"):
        email = st.text_input(
            "Email Address", 
            placeholder="your.name@pd15.org",
            help="Must end with @pd15.org or @pd15.state.fl.us",
            key="reg_email"
        )
        
        password = st.text_input(
            "Password", 
            type="password",
            help="Minimum 8 characters",
            key="reg_password"
        )
        
        confirm_password = st.text_input(
            "Confirm Password", 
            type="password",
            key="reg_confirm_password"
        )
        
        submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submit:
            # Validation
            if not all([email, password, confirm_password]):
                st.error("Please fill in all fields.")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters long.")
                return
            
            # Register user - use email as username
            success, message = auth.register_user(email, password, email)
            
            if success:
                st.success(message)
                st.info("📧 Check the **Verify Account** tab to complete your registration.")
            else:
                st.error(message)


def show_verification_form(auth: AuthManager):
    """Display account verification form"""
    st.header("✅ Verify Account")
    st.info("Enter the 6-digit verification code sent to your email")
    
    with st.form("verification_form"):
        email = st.text_input("Email Address", key="verify_email", help="Enter the email address you registered with")
        verification_code = st.text_input("Verification Code", key="verification_code", max_chars=6, help="6-digit code from email")
        
        submit = st.form_submit_button("Verify Account", use_container_width=True, type="primary")
        
        if submit:
            if not email or not verification_code:
                st.error("Please enter both email address and verification code.")
                return
            
            success, message = auth.verify_registration(email, verification_code)
            
            if success:
                st.success(message)
                st.info("✅ Account activated! You can now log in using the **Email + Password** tab.")
            else:
                st.error(message)


def check_authentication():
    """Check if user is authenticated and handle authentication flow"""
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'auth_token' not in st.session_state:
        st.session_state.auth_token = None
    
    # If not authenticated, show login page
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    # If authenticated, verify token is still valid
    if st.session_state.auth_token:
        auth = AuthManager()
        user_info = auth.verify_token(st.session_state.auth_token)
        
        if user_info:
            # Store user info in session state
            st.session_state.user_info = user_info
            return True
        else:
            # Token expired or invalid
            st.session_state.authenticated = False
            st.session_state.auth_token = None
            st.error("Your session has expired. Please log in again.")
            st.rerun()
    
    return False


def show_user_info():
    """Display user info and logout button in sidebar"""
    if st.session_state.get('authenticated') and st.session_state.get('user_info'):
        user_info = st.session_state.user_info
        
        with st.sidebar:
            st.divider()
            st.markdown("### 👤 User Info")
            st.write(f"**Name:** {user_info['email'].split('@')[0].replace('.', ' ').title()}")
            st.write(f"**Email:** {user_info['email']}")
            
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session state
                st.session_state.authenticated = False
                st.session_state.auth_token = None
                st.session_state.user_info = None
                if 'pin_requested' in st.session_state:
                    del st.session_state.pin_requested
                if 'pin_email_stored' in st.session_state:
                    del st.session_state.pin_email_stored
                st.rerun()


def require_authentication(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if check_authentication():
            return func(*args, **kwargs)
        else:
            return None
    return wrapper