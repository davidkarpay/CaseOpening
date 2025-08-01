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
    tab1, tab2, tab3, tab4 = st.tabs(["Login", "Quick PIN Login", "Register", "Verify Account"])
    
    with tab1:
        show_login_form(auth)
    
    with tab2:
        show_pin_login_form(auth)
    
    with tab3:
        show_registration_form(auth)
    
    with tab4:
        show_verification_form(auth)


def show_login_form(auth: AuthManager):
    """Display standard login form"""
    st.header("🔑 Standard Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
                return
            
            success, message, token = auth.authenticate_user(username, password)
            
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
    st.info("Get a PIN sent to your email for quick access")
    
    # PIN request form
    if 'pin_requested' not in st.session_state:
        st.session_state.pin_requested = False
    
    if not st.session_state.pin_requested:
        with st.form("pin_request_form"):
            username = st.text_input("Username", key="pin_username")
            
            submit = st.form_submit_button("Send PIN to Email", use_container_width=True)
            
            if submit:
                if not username:
                    st.error("Please enter your username.")
                    return
                
                success, message = auth.request_login_pin(username)
                
                if success:
                    st.session_state.pin_requested = True
                    st.session_state.pin_username = username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        # PIN verification form
        st.success(f"PIN sent to your email address!")
        
        with st.form("pin_verify_form"):
            pin = st.text_input("Enter PIN from email", key="verify_pin")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Verify PIN", use_container_width=True)
            with col2:
                if st.form_submit_button("Request New PIN", use_container_width=True):
                    st.session_state.pin_requested = False
                    st.rerun()
            
            if submit:
                if not pin:
                    st.error("Please enter the PIN.")
                    return
                
                success, message, token = auth.verify_login_pin(
                    st.session_state.pin_username, pin
                )
                
                if success:
                    st.session_state.auth_token = token
                    st.session_state.authenticated = True
                    st.session_state.pin_requested = False
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def show_registration_form(auth: AuthManager):
    """Display registration form"""
    st.header("📝 Create Account")
    st.info("Registration is restricted to @pd15.org and @pd15.state.fl.us email addresses")
    
    with st.form("registration_form"):
        username = st.text_input(
            "Username", 
            help="Choose a unique username",
            key="reg_username"
        )
        
        email = st.text_input(
            "Email Address", 
            help="Must be @pd15.org or @pd15.state.fl.us",
            key="reg_email"
        )
        
        password = st.text_input(
            "Password", 
            type="password",
            help="Choose a strong password",
            key="reg_password"
        )
        
        confirm_password = st.text_input(
            "Confirm Password", 
            type="password",
            key="reg_confirm_password"
        )
        
        submit = st.form_submit_button("Register Account", use_container_width=True)
        
        if submit:
            # Validation
            if not all([username, email, password, confirm_password]):
                st.error("Please fill in all fields.")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters long.")
                return
            
            # Register user
            success, message = auth.register_user(username, password, email)
            
            if success:
                st.success(message)
                st.info("Please check the 'Verify Account' tab to complete your registration.")
            else:
                st.error(message)


def show_verification_form(auth: AuthManager):
    """Display account verification form"""
    st.header("✅ Verify Account")
    st.info("Enter the verification code sent to your email")
    
    with st.form("verification_form"):
        username = st.text_input("Username", key="verify_username")
        verification_code = st.text_input("Verification Code", key="verification_code")
        
        submit = st.form_submit_button("Verify Account", use_container_width=True)
        
        if submit:
            if not username or not verification_code:
                st.error("Please enter both username and verification code.")
                return
            
            success, message = auth.verify_registration(username, verification_code)
            
            if success:
                st.success(message)
                st.info("You can now log in using the 'Login' tab.")
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
            st.write(f"**Username:** {user_info['username']}")
            st.write(f"**Email:** {user_info['email']}")
            
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session state
                st.session_state.authenticated = False
                st.session_state.auth_token = None
                st.session_state.user_info = None
                if 'pin_requested' in st.session_state:
                    del st.session_state.pin_requested
                if 'pin_username' in st.session_state:
                    del st.session_state.pin_username
                st.rerun()


def require_authentication(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if check_authentication():
            return func(*args, **kwargs)
        else:
            return None
    return wrapper