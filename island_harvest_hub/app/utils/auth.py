"""
Simple authentication utility for Island Harvest Hub.
Uses Streamlit secrets for credential storage.
"""

import streamlit as st
import hashlib
import hmac
import os

def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hmac.compare_digest(hash_password(password), password_hash)

def get_credentials():
    """Get credentials from Streamlit secrets or environment variables."""
    # Try to get from Streamlit secrets first (for Streamlit Cloud)
    if hasattr(st, 'secrets'):
        try:
            # Check if auth section exists in secrets
            if 'auth' in st.secrets:
                auth_secrets = st.secrets['auth']
                password_hash = auth_secrets.get('password_hash', '') if isinstance(auth_secrets, dict) else ''
                username = auth_secrets.get('username', 'admin') if isinstance(auth_secrets, dict) else 'admin'
                
                if password_hash:  # Only return if password_hash is not empty
                    return {
                        'username': username,
                        'password_hash': password_hash
                    }
        except Exception as e:
            # Debug: uncomment to see errors
            # st.error(f"Error reading secrets: {e}")
            pass
    
    # Fallback to environment variables
    username = os.getenv('APP_USERNAME', 'admin')
    password_hash = os.getenv('APP_PASSWORD_HASH', '')
    
    return {
        'username': username,
        'password_hash': password_hash
    }

def check_password():
    """Check if user is authenticated."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login():
    """Display login form and handle authentication."""
    st.title("🔐 Island Harvest Hub - Login")
    st.markdown("---")
    
    credentials = get_credentials()
    
    # If no password is set, show setup instructions
    if not credentials.get('password_hash'):
        st.warning("⚠️ No password configured. Please set up authentication.")
        st.info("""
        **To set up authentication, add to Streamlit Cloud Secrets:**
        
        ```toml
        [auth]
        username = "admin"
        password_hash = "<hashed_password>"
        ```
        
        Or set environment variables:
        - `APP_USERNAME=admin`
        - `APP_PASSWORD_HASH=<hashed_password>`
        
        **Generate password hash:**
        ```python
        import hashlib
        password = "your_password"
        hash = hashlib.sha256(password.encode()).hexdigest()
        print(hash)
        ```
        """)
        
        # Allow temporary access for setup (not recommended for production)
        if st.button("Continue Without Authentication (Setup Mode)"):
            st.session_state.authenticated = True
            st.rerun()
        return False
    
    with st.form("login_form"):
        st.subheader("Enter your credentials")
        
        username = st.text_input("Username", value=credentials.get('username', ''))
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if username == credentials.get('username'):
                if verify_password(password, credentials.get('password_hash', '')):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
            else:
                st.error("❌ Invalid username")
    
    return False

def logout():
    """Logout the current user."""
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'username' in st.session_state:
        del st.session_state.username
    st.rerun()

def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        if not check_password():
            login()
            return
        return func(*args, **kwargs)
    return wrapper

def show_logout_button():
    """Display logout button in sidebar."""
    if check_password():
        with st.sidebar:
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                logout()

