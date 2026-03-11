"""
YojnaMitra-AI Authentication Components
Handles user registration, login, and session management
"""

import streamlit as st
import requests
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

# Configuration
API_BASE_URL = "http://localhost:5000/auth"  # Will be replaced with actual API Gateway URL
MOCK_MODE = True  # Set to False when backend is deployed

# Mock database for development (will be replaced with DynamoDB)
if 'mock_users' not in st.session_state:
    st.session_state.mock_users = {}
if 'mock_otps' not in st.session_state:
    st.session_state.mock_otps = {}
if 'mock_email_users' not in st.session_state:
    st.session_state.mock_email_users = {}

# Initialize demo user account for hackathon judges
def _init_demo_user():
    """Create a pre-registered demo user for quick testing"""
    demo_phone = "9876543210"
    demo_phone_hash = hashlib.sha256(demo_phone.encode()).hexdigest()
    
    if demo_phone_hash not in st.session_state.mock_users:
        st.session_state.mock_users[demo_phone_hash] = {
            'user_id': 'usr_demo_hackathon_2026',
            'phone': demo_phone,
            'phone_hash': demo_phone_hash,
            'created_at': '2026-03-01T10:00:00Z',
            'last_login': '2026-03-06T08:00:00Z',
            'profile': {
                'name': 'Rajesh Kumar',
                'age': 35,
                'state': 'Bihar',
                'district': 'Patna',
                'income': 300000,
                'occupation': 'Farmer'
            }
        }

# Initialize demo user on module load
_init_demo_user()


class SessionManager:
    """Manages user session state"""
    
    def __init__(self):
        self.session_key = "yojnamitra_auth_token"
        self.user_key = "yojnamitra_user_id"
        self.profile_key = "yojnamitra_user_profile"
        self.expiry_key = "yojnamitra_session_expiry"
    
    def create_session(self, token: str, user_id: str, user_data: dict):
        """Create authenticated session"""
        expiry = datetime.now() + timedelta(hours=24)
        st.session_state[self.session_key] = token
        st.session_state[self.user_key] = user_id
        st.session_state[self.profile_key] = user_data
        st.session_state[self.expiry_key] = expiry.isoformat()
        st.session_state['authenticated'] = True
    
    def is_authenticated(self) -> bool:
        """Check if current session is valid"""
        if not st.session_state.get('authenticated', False):
            return False
        
        # Check token exists
        if self.session_key not in st.session_state:
            return False
        
        # Check expiration
        expiry_str = st.session_state.get(self.expiry_key)
        if expiry_str:
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.now() > expiry:
                self.clear_session()
                return False
        
        return True
    
    def get_user_id(self) -> Optional[str]:
        """Retrieve current user ID"""
        return st.session_state.get(self.user_key)
    
    def get_user_profile(self) -> Optional[dict]:
        """Retrieve current user profile"""
        return st.session_state.get(self.profile_key)
    
    def clear_session(self):
        """Clear session data on logout"""
        keys_to_clear = [
            self.session_key, self.user_key, self.profile_key, 
            self.expiry_key, 'authenticated'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def logout(self):
        """Logout user"""
        self.clear_session()
        st.rerun()


class ErrorHandler:
    """Centralized error handling for authentication UI"""
    
    @staticmethod
    def handle_api_error(error_response: dict):
        """Display appropriate error message based on error code"""
        code = error_response.get('code', 'UNKNOWN_ERROR')
        message = error_response.get('message', 'An error occurred')
        
        if code == 'INVALID_EMAIL':
            st.error(f"❌ {message}")
            st.info("💡 Example: user@example.com")
        
        elif code == 'WEAK_PASSWORD':
            st.error(f"❌ {message}")
            st.info("💡 Use at least 6 characters with letters and numbers")
        
        elif code == 'EMAIL_EXISTS':
            st.error(f"❌ {message}")
            st.info("💡 Please use the login page instead")
        
        elif code == 'INVALID_PASSWORD':
            st.error(f"❌ {message}")
            st.info("💡 Check your password and try again")
        
        elif code == 'INVALID_PHONE_FORMAT':
            st.error(f"❌ {message}")
            st.info("💡 Example: 9876543210 (10 digits starting with 6-9)")
        
        elif code == 'INVALID_OTP':
            attempts = error_response.get('attempts_remaining', 0)
            st.error(f"❌ {message}")
            if attempts > 0:
                st.warning(f"⚠️ {attempts} attempts remaining")
        
        elif code == 'OTP_EXPIRED':
            st.error(f"❌ {message}")
            st.info("💡 Click 'Resend OTP' to get a new code")
        
        elif code == 'USER_EXISTS':
            st.error(f"❌ {message}")
            st.info("💡 Please use the login page instead")
        
        elif code == 'USER_NOT_FOUND':
            st.error(f"❌ {message}")
            st.info("💡 Please register first")
        
        elif code == 'ACCOUNT_LOCKED':
            unlock_time = error_response.get('unlock_at', 'soon')
            st.error(f"🔒 {message}")
            st.info(f"⏰ Account will unlock at: {unlock_time}")
        
        elif code == 'RESEND_COOLDOWN':
            retry_after = error_response.get('retry_after', 30)
            st.warning(f"⏳ {message}")
            st.info(f"Please wait {retry_after} seconds")
        
        else:
            st.error(f"❌ {message}")


class MockAuthBackend:
    """Mock authentication backend for development"""
    
    @staticmethod
    def hash_phone(phone: str) -> str:
        """Hash phone number for lookup"""
        return hashlib.sha256(phone.encode()).hexdigest()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(secrets.randbelow(1000000)).zfill(6)
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Indian phone number format"""
        if len(phone) != 10:
            return False
        if not phone.isdigit():
            return False
        if phone[0] not in '6789':
            return False
        return True
    
    @staticmethod
    def register_email(email: str, password: str, name: str) -> dict:
        """Register new user with email/password"""
        # Validate email
        if not MockAuthBackend.validate_email(email):
            return {
                'status': 'error',
                'code': 'INVALID_EMAIL',
                'message': 'Please enter a valid email address'
            }
        
        # Validate password
        if len(password) < 6:
            return {
                'status': 'error',
                'code': 'WEAK_PASSWORD',
                'message': 'Password must be at least 6 characters'
            }
        
        # Check if email exists
        if email.lower() in st.session_state.mock_email_users:
            return {
                'status': 'error',
                'code': 'EMAIL_EXISTS',
                'message': 'An account with this email already exists'
            }
        
        # Create user
        user_id = f"usr_{secrets.token_hex(8)}"
        password_hash = MockAuthBackend.hash_password(password)
        
        st.session_state.mock_email_users[email.lower()] = {
            'user_id': user_id,
            'email': email.lower(),
            'password_hash': password_hash,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'profile': {
                'name': name,
                'age': None,
                'state': None,
                'district': None,
                'income': None,
                'occupation': None
            }
        }
        
        # Generate token
        token = secrets.token_urlsafe(32)
        
        return {
            'status': 'success',
            'token': token,
            'user_id': user_id,
            'user_profile': st.session_state.mock_email_users[email.lower()],
            'expires_in': 86400
        }
    
    @staticmethod
    def login_email(email: str, password: str) -> dict:
        """Login with email/password"""
        # Check if user exists
        if email.lower() not in st.session_state.mock_email_users:
            return {
                'status': 'error',
                'code': 'USER_NOT_FOUND',
                'message': 'No account found with this email'
            }
        
        user_data = st.session_state.mock_email_users[email.lower()]
        password_hash = MockAuthBackend.hash_password(password)
        
        # Verify password
        if password_hash != user_data['password_hash']:
            return {
                'status': 'error',
                'code': 'INVALID_PASSWORD',
                'message': 'Incorrect password'
            }
        
        # Update last login
        user_data['last_login'] = datetime.now().isoformat()
        
        # Generate token
        token = secrets.token_urlsafe(32)
        
        return {
            'status': 'success',
            'token': token,
            'user_id': user_data['user_id'],
            'user_profile': user_data,
            'expires_in': 86400
        }
    
    @staticmethod
    def register(phone: str) -> dict:
        """Mock registration - send OTP"""
        if not MockAuthBackend.validate_phone(phone):
            return {
                'status': 'error',
                'code': 'INVALID_PHONE_FORMAT',
                'message': 'Phone number must be 10 digits starting with 6-9'
            }
        
        phone_hash = MockAuthBackend.hash_phone(phone)
        
        # Check if user exists
        if phone_hash in st.session_state.mock_users:
            return {
                'status': 'error',
                'code': 'USER_EXISTS',
                'message': 'Account already exists with this phone number'
            }
        
        # Generate OTP
        otp = MockAuthBackend.generate_otp()
        st.session_state.mock_otps[phone_hash] = {
            'otp': otp,
            'created_at': time.time(),
            'expires_at': time.time() + 600,  # 10 minutes
            'attempts': 0,
            'type': 'registration'
        }
        
        # In development, show OTP in console/UI
        st.info(f"🔐 **Development Mode**: Your OTP is **{otp}** (valid for 10 minutes)")
        
        return {
            'status': 'success',
            'message': 'OTP sent to your phone',
            'expires_in': 600
        }
    
    @staticmethod
    def verify_registration(phone: str, otp: str) -> dict:
        """Mock OTP verification for registration"""
        phone_hash = MockAuthBackend.hash_phone(phone)
        
        # Check OTP exists
        if phone_hash not in st.session_state.mock_otps:
            return {
                'status': 'error',
                'code': 'OTP_NOT_FOUND',
                'message': 'No OTP found. Please request a new one'
            }
        
        otp_data = st.session_state.mock_otps[phone_hash]
        
        # Check expiration
        if time.time() > otp_data['expires_at']:
            return {
                'status': 'error',
                'code': 'OTP_EXPIRED',
                'message': 'OTP has expired. Please request a new one'
            }
        
        # Check attempts
        if otp_data['attempts'] >= 3:
            return {
                'status': 'error',
                'code': 'MAX_ATTEMPTS_EXCEEDED',
                'message': 'Too many failed attempts. Please request a new OTP'
            }
        
        # Verify OTP
        if otp != otp_data['otp']:
            otp_data['attempts'] += 1
            attempts_left = 3 - otp_data['attempts']
            return {
                'status': 'error',
                'code': 'INVALID_OTP',
                'message': 'Invalid OTP',
                'attempts_remaining': attempts_left
            }
        
        # Create user
        user_id = f"usr_{secrets.token_hex(8)}"
        st.session_state.mock_users[phone_hash] = {
            'user_id': user_id,
            'phone': phone,
            'phone_hash': phone_hash,
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'profile': {
                'name': None,
                'age': None,
                'state': None,
                'district': None,
                'income': None,
                'occupation': None
            }
        }
        
        # Generate token
        token = secrets.token_urlsafe(32)
        
        # Clear OTP
        del st.session_state.mock_otps[phone_hash]
        
        return {
            'status': 'success',
            'token': token,
            'user_id': user_id,
            'user_profile': st.session_state.mock_users[phone_hash],
            'expires_in': 86400
        }
    
    @staticmethod
    def login(phone: str) -> dict:
        """Mock login - send OTP"""
        if not MockAuthBackend.validate_phone(phone):
            return {
                'status': 'error',
                'code': 'INVALID_PHONE_FORMAT',
                'message': 'Phone number must be 10 digits starting with 6-9'
            }
        
        phone_hash = MockAuthBackend.hash_phone(phone)
        
        # Check if user exists
        if phone_hash not in st.session_state.mock_users:
            return {
                'status': 'error',
                'code': 'USER_NOT_FOUND',
                'message': 'No account found with this phone number'
            }
        
        # Generate OTP
        otp = MockAuthBackend.generate_otp()
        st.session_state.mock_otps[phone_hash] = {
            'otp': otp,
            'created_at': time.time(),
            'expires_at': time.time() + 600,
            'attempts': 0,
            'type': 'login'
        }
        
        # In development, show OTP
        st.info(f"🔐 **Development Mode**: Your OTP is **{otp}** (valid for 10 minutes)")
        
        return {
            'status': 'success',
            'message': 'OTP sent to your phone',
            'expires_in': 600
        }
    
    @staticmethod
    def verify_login(phone: str, otp: str) -> dict:
        """Mock OTP verification for login"""
        phone_hash = MockAuthBackend.hash_phone(phone)
        
        # Check OTP exists
        if phone_hash not in st.session_state.mock_otps:
            return {
                'status': 'error',
                'code': 'OTP_NOT_FOUND',
                'message': 'No OTP found. Please request a new one'
            }
        
        otp_data = st.session_state.mock_otps[phone_hash]
        
        # Check expiration
        if time.time() > otp_data['expires_at']:
            return {
                'status': 'error',
                'code': 'OTP_EXPIRED',
                'message': 'OTP has expired. Please request a new one'
            }
        
        # Check attempts
        if otp_data['attempts'] >= 5:
            return {
                'status': 'error',
                'code': 'ACCOUNT_LOCKED',
                'message': 'Account temporarily locked due to too many failed attempts',
                'unlock_at': datetime.now() + timedelta(minutes=30)
            }
        
        # Verify OTP
        if otp != otp_data['otp']:
            otp_data['attempts'] += 1
            attempts_left = 5 - otp_data['attempts']
            return {
                'status': 'error',
                'code': 'INVALID_OTP',
                'message': 'Invalid OTP',
                'attempts_remaining': attempts_left
            }
        
        # Get user
        user_data = st.session_state.mock_users[phone_hash]
        user_data['last_login'] = datetime.now().isoformat()
        
        # Generate token
        token = secrets.token_urlsafe(32)
        
        # Clear OTP
        del st.session_state.mock_otps[phone_hash]
        
        return {
            'status': 'success',
            'token': token,
            'user_id': user_data['user_id'],
            'user_profile': user_data,
            'expires_in': 86400
        }


class RegistrationPage:
    """Handles new user registration"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        if 'reg_step' not in st.session_state:
            st.session_state.reg_step = 'phone'  # phone, otp, email
        if 'reg_phone' not in st.session_state:
            st.session_state.reg_phone = ''
        if 'reg_mode' not in st.session_state:
            st.session_state.reg_mode = 'email'  # email, phone
    
    def render(self):
        """Display registration form"""
        st.markdown("### 📝 Create New Account")
        st.markdown("Join YojnaMitra-AI to discover government schemes tailored for you")
        
        # Registration mode selector
        col1, col2 = st.columns(2)
        
        with col1:
            is_email_active = st.session_state.reg_mode == 'email'
            button_type = "primary" if is_email_active else "secondary"
            if st.button("📧 Email Registration", use_container_width=True, type=button_type, key="reg_email_mode_btn"):
                st.session_state.reg_mode = 'email'
                st.rerun()
        
        with col2:
            is_phone_active = st.session_state.reg_mode == 'phone'
            button_type = "primary" if is_phone_active else "secondary"
            if st.button("📱 Phone Registration", use_container_width=True, type=button_type, key="reg_phone_mode_btn"):
                st.session_state.reg_mode = 'phone'
                st.session_state.reg_step = 'phone'
                st.rerun()
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Render based on mode
        if st.session_state.reg_mode == 'email':
            self._render_email_registration()
        else:
            if st.session_state.reg_step == 'phone':
                self._render_phone_step()
            elif st.session_state.reg_step == 'otp':
                self._render_otp_step()
    
    def _render_email_registration(self):
        """Render email/password registration"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    padding: 1.5rem;
                    border-radius: 16px;
                    text-align: center;
                    color: white;
                    margin-bottom: 1.5rem;'>
            <h3 style='margin: 0 0 0.5rem 0; font-weight: 700;'>📧 Quick Email Registration</h3>
            <p style='margin: 0; opacity: 0.95; font-size: 0.95rem;'>
                Create your account in seconds - No OTP required!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Registration form
        name = st.text_input(
            "👤 Full Name",
            placeholder="Enter your full name",
            key="reg_name_input",
            help="Your name will be used to personalize your experience"
        )
        
        email = st.text_input(
            "📧 Email Address",
            placeholder="your.email@example.com",
            key="reg_email_input",
            help="We'll use this email for your account"
        )
        
        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Create a strong password (min 6 characters)",
            key="reg_password_input",
            help="Choose a secure password with at least 6 characters"
        )
        
        confirm_password = st.text_input(
            "🔑 Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="reg_confirm_password_input",
            help="Make sure it matches your password"
        )
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("✨ Create Account", use_container_width=True, type="primary", key="create_email_account_btn"):
                if name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Passwords do not match")
                    else:
                        response = MockAuthBackend.register_email(email, password, name)
                        
                        if response['status'] == 'success':
                            # Create session
                            session_manager = SessionManager()
                            session_manager.create_session(
                                response['token'],
                                response['user_id'],
                                response['user_profile']
                            )
                            st.success("🎉 Account created successfully! Welcome to YojnaMitra-AI!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            self.error_handler.handle_api_error(response)
                else:
                    st.error("❌ Please fill in all fields")
        
        with col2:
            if st.button("🔙 Back to Login", use_container_width=True, key="back_to_login_from_reg_btn"):
                st.session_state.auth_page = 'login'
                st.rerun()
    
    def _render_phone_step(self):
        """Render phone number input step"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem;
                    border-radius: 16px;
                    text-align: center;
                    color: white;
                    margin-bottom: 1.5rem;'>
            <h3 style='margin: 0 0 0.5rem 0; font-weight: 700;'>📱 Phone Registration</h3>
            <p style='margin: 0; opacity: 0.95; font-size: 0.95rem;'>
                Register with your mobile number - OTP verification required
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        phone = st.text_input(
            "📞 Mobile Number",
            placeholder="9876543210",
            max_chars=10,
            help="Enter your 10-digit Indian mobile number"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📨 Send OTP", use_container_width=True, type="primary"):
                if phone:
                    response = MockAuthBackend.register(phone)
                    
                    if response['status'] == 'success':
                        st.session_state.reg_phone = phone
                        st.session_state.reg_step = 'otp'
                        st.success("✅ OTP sent successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        self.error_handler.handle_api_error(response)
                else:
                    st.error("❌ Please enter your phone number")
        
        with col2:
            if st.button("🔙 Back to Login", use_container_width=True):
                st.session_state.auth_page = 'login'
                st.rerun()
    
    def _render_otp_step(self):
        """Render OTP verification step"""
        st.info(f"📱 OTP sent to {st.session_state.reg_phone}")
        
        otp = st.text_input(
            "🔐 Enter OTP",
            placeholder="123456",
            max_chars=6,
            help="Enter the 6-digit code sent to your phone"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Verify & Register", use_container_width=True, type="primary"):
                if otp:
                    response = MockAuthBackend.verify_registration(
                        st.session_state.reg_phone, otp
                    )
                    
                    if response['status'] == 'success':
                        # Create session
                        session_manager = SessionManager()
                        session_manager.create_session(
                            response['token'],
                            response['user_id'],
                            response['user_profile']
                        )
                        st.success("🎉 Registration successful! Welcome to YojnaMitra-AI!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        self.error_handler.handle_api_error(response)
                else:
                    st.error("❌ Please enter the OTP")
        
        with col2:
            if st.button("🔄 Resend OTP", use_container_width=True):
                response = MockAuthBackend.register(st.session_state.reg_phone)
                if response['status'] == 'success':
                    st.success("✅ New OTP sent!")
                else:
                    self.error_handler.handle_api_error(response)


class LoginPage:
    """Handles user login interface"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        if 'login_step' not in st.session_state:
            st.session_state.login_step = 'phone'  # phone, otp
        if 'login_phone' not in st.session_state:
            st.session_state.login_phone = ''
        if 'login_mode' not in st.session_state:
            st.session_state.login_mode = 'demo'  # demo, email, otp
    
    def render(self):
        """Display modern professional login form"""
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #333; font-weight: 700; margin-bottom: 0.5rem;'>Welcome Back!</h2>
            <p style='color: #666; font-size: 1rem;'>Choose your preferred login method</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Modern login mode selector with cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            is_demo_active = st.session_state.login_mode == 'demo'
            button_type = "primary" if is_demo_active else "secondary"
            if st.button("⚡ Demo Login", use_container_width=True, type=button_type, key="demo_mode_btn"):
                st.session_state.login_mode = 'demo'
                st.rerun()
        
        with col2:
            is_email_active = st.session_state.login_mode == 'email'
            button_type = "primary" if is_email_active else "secondary"
            if st.button("📧 Email Login", use_container_width=True, type=button_type, key="email_mode_btn"):
                st.session_state.login_mode = 'email'
                st.rerun()
        
        with col3:
            is_otp_active = st.session_state.login_mode == 'otp'
            button_type = "primary" if is_otp_active else "secondary"
            if st.button("📱 OTP Login", use_container_width=True, type=button_type, key="otp_mode_btn"):
                st.session_state.login_mode = 'otp'
                st.session_state.login_step = 'phone'
                st.rerun()
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Render based on mode
        if st.session_state.login_mode == 'demo':
            self._render_demo_login()
        elif st.session_state.login_mode == 'email':
            self._render_email_login()
        else:
            if st.session_state.login_step == 'phone':
                self._render_phone_step()
            elif st.session_state.login_step == 'otp':
                self._render_otp_step()
    
    def _render_demo_login(self):
        """Render modern instant demo login"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 1.5rem;
                    border-radius: 16px;
                    text-align: center;
                    color: white;
                    margin-bottom: 1.5rem;'>
            <h3 style='margin: 0 0 0.5rem 0; font-weight: 700;'>🚀 Instant Demo Access</h3>
            <p style='margin: 0; opacity: 0.95; font-size: 0.95rem;'>
                For hackathon judges & quick testing - No OTP required!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with modern styling
        username = st.text_input(
            "👤 Username",
            placeholder="Enter: demo",
            key="demo_username",
            help="Use 'demo' for instant access"
        )
        
        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Enter: demo123",
            key="demo_password",
            help="Use 'demo123' for instant access"
        )
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 Login Instantly", use_container_width=True, type="primary", key="demo_login_btn"):
                if username == "demo" and password == "demo123":
                    # Create demo session
                    session_manager = SessionManager()
                    demo_user = {
                        'user_id': 'usr_demo_hackathon_2026',
                        'phone': '9876543210',
                        'profile': {
                            'name': 'Rajesh Kumar (Demo)',
                            'age': 35,
                            'state': 'Bihar',
                            'district': 'Patna',
                            'income': 300000,
                            'occupation': 'Farmer'
                        }
                    }
                    session_manager.create_session(
                        token='demo_token_' + secrets.token_hex(16),
                        user_id=demo_user['user_id'],
                        user_data=demo_user
                    )
                    st.success("🎉 Demo login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Use: demo / demo123")
        
        with col2:
            if st.button("📝 Register", use_container_width=True, key="goto_register_btn"):
                st.session_state.auth_page = 'register'
                st.rerun()
        
        # Alternative demo accounts
        with st.expander("🎭 More Demo Accounts", expanded=False):
            st.markdown("""
            <div style='background: #f8f9fa; padding: 1rem; border-radius: 12px;'>
                <p style='font-weight: 600; margin-bottom: 1rem; color: #333;'>Try different user profiles:</p>
            </div>
            """, unsafe_allow_html=True)
            
            demo_accounts = [
                {"username": "farmer", "password": "farmer123", "profile": "👨‍🌾 Farmer from Bihar", "color": "#27ae60"},
                {"username": "student", "password": "student123", "profile": "👨‍🎓 Student from UP", "color": "#3498db"},
                {"username": "woman", "password": "woman123", "profile": "👩‍💼 Woman Entrepreneur", "color": "#e74c3c"}
            ]
            
            for account in demo_accounts:
                st.markdown(f"""
                <div style='background: {account['color']}15;
                            border-left: 4px solid {account['color']};
                            padding: 1rem;
                            margin: 0.5rem 0;
                            border-radius: 8px;'>
                    <div style='font-weight: 600; color: {account['color']}; margin-bottom: 0.5rem;'>
                        {account['profile']}
                    </div>
                    <div style='display: flex; gap: 2rem; font-size: 0.9rem;'>
                        <div><strong>Username:</strong> <code>{account['username']}</code></div>
                        <div><strong>Password:</strong> <code>{account['password']}</code></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_email_login(self):
        """Render email/password login"""
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem;
                    border-radius: 16px;
                    text-align: center;
                    color: white;
                    margin-bottom: 1.5rem;'>
            <h3 style='margin: 0 0 0.5rem 0; font-weight: 700;'>📧 Email Login</h3>
            <p style='margin: 0; opacity: 0.95; font-size: 0.95rem;'>
                Login with your registered email and password
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Email login form
        email = st.text_input(
            "📧 Email Address",
            placeholder="your.email@example.com",
            key="email_login_input",
            help="Enter your registered email address"
        )
        
        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Enter your password",
            key="email_password_input",
            help="Enter your account password"
        )
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🔓 Login", use_container_width=True, type="primary", key="email_login_btn"):
                if email and password:
                    response = MockAuthBackend.login_email(email, password)
                    
                    if response['status'] == 'success':
                        # Create session
                        session_manager = SessionManager()
                        session_manager.create_session(
                            response['token'],
                            response['user_id'],
                            response['user_profile']
                        )
                        st.success("🎉 Login successful! Welcome back!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        self.error_handler.handle_api_error(response)
                else:
                    st.error("❌ Please enter both email and password")
        
        with col2:
            if st.button("📝 Register", use_container_width=True, key="goto_register_from_email_btn"):
                st.session_state.auth_page = 'register'
                st.rerun()
    
    def _render_phone_step(self):
        """Render phone number input step"""
        st.markdown("#### 📱 Login with OTP")
        
        phone = st.text_input(
            "📞 Mobile Number",
            placeholder="9876543210",
            max_chars=10,
            help="Enter your registered mobile number"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📨 Send OTP", use_container_width=True, type="primary"):
                if phone:
                    response = MockAuthBackend.login(phone)
                    
                    if response['status'] == 'success':
                        st.session_state.login_phone = phone
                        st.session_state.login_step = 'otp'
                        st.success("✅ OTP sent successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        self.error_handler.handle_api_error(response)
                else:
                    st.error("❌ Please enter your phone number")
        
        with col2:
            if st.button("📝 New User? Register", use_container_width=True):
                st.session_state.auth_page = 'register'
                st.rerun()
    
    def _render_otp_step(self):
        """Render OTP verification step"""
        st.info(f"📱 OTP sent to {st.session_state.login_phone}")
        
        otp = st.text_input(
            "🔐 Enter OTP",
            placeholder="123456",
            max_chars=6,
            help="Enter the 6-digit code sent to your phone"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Verify & Login", use_container_width=True, type="primary"):
                if otp:
                    response = MockAuthBackend.verify_login(
                        st.session_state.login_phone, otp
                    )
                    
                    if response['status'] == 'success':
                        # Create session
                        session_manager = SessionManager()
                        session_manager.create_session(
                            response['token'],
                            response['user_id'],
                            response['user_profile']
                        )
                        st.success("🎉 Login successful! Welcome back!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        self.error_handler.handle_api_error(response)
                else:
                    st.error("❌ Please enter the OTP")
        
        with col2:
            if st.button("🔄 Resend OTP", use_container_width=True):
                response = MockAuthBackend.login(st.session_state.login_phone)
                if response['status'] == 'success':
                    st.success("✅ New OTP sent!")
                else:
                    self.error_handler.handle_api_error(response)


def render_auth_page():
    """Main authentication page router with PREMIUM professional design"""
    # Initialize auth page state
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = 'login'
    
    # PREMIUM Professional CSS - Best of the Best
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Global font */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Animated gradient background */
        .stApp {
            background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Glassmorphism card */
        .auth-card {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border-radius: 32px;
            padding: 3.5rem 3rem;
            box-shadow: 
                0 8px 32px 0 rgba(31, 38, 135, 0.37),
                0 0 0 1px rgba(255, 255, 255, 0.18) inset;
            max-width: 520px;
            margin: 3rem auto;
            border: 1px solid rgba(255, 255, 255, 0.4);
            position: relative;
            overflow: hidden;
            animation: slideUp 0.6s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Decorative elements */
        .auth-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* Logo and header */
        .auth-header {
            text-align: center;
            margin-bottom: 2.5rem;
            position: relative;
            z-index: 1;
        }
        
        .auth-logo {
            font-size: 5rem;
            margin-bottom: 1rem;
            animation: float 3s ease-in-out infinite, glow 2s ease-in-out infinite;
            filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.4));
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-15px) rotate(5deg); }
        }
        
        @keyframes glow {
            0%, 100% { filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.4)); }
            50% { filter: drop-shadow(0 8px 24px rgba(102, 126, 234, 0.8)); }
        }
        
        .auth-title {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 3rem;
            font-weight: 900;
            margin-bottom: 0.75rem;
            letter-spacing: -2px;
            line-height: 1.1;
        }
        
        .auth-subtitle {
            color: #555;
            font-size: 1.15rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            letter-spacing: -0.3px;
        }
        
        .auth-tagline {
            color: #888;
            font-size: 0.9rem;
            font-weight: 400;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        /* Premium demo badge */
        .demo-badge {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 1.5rem 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 
                0 10px 30px rgba(17, 153, 142, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.2) inset;
            animation: pulse 3s ease-in-out infinite;
            position: relative;
            overflow: hidden;
        }
        
        .demo-badge::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); box-shadow: 0 10px 30px rgba(17, 153, 142, 0.4); }
            50% { transform: scale(1.02); box-shadow: 0 15px 40px rgba(17, 153, 142, 0.6); }
        }
        
        .demo-badge-title {
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .demo-credentials {
            display: flex;
            justify-content: space-around;
            margin-top: 1.25rem;
            gap: 1rem;
        }
        
        .demo-cred-item {
            text-align: center;
            flex: 1;
        }
        
        .demo-cred-label {
            font-size: 0.85rem;
            opacity: 0.95;
            margin-bottom: 0.5rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .demo-cred-value {
            font-size: 1.4rem;
            font-weight: 800;
            font-family: 'Courier New', monospace;
            background: rgba(255, 255, 255, 0.25);
            padding: 0.75rem 1.25rem;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .demo-cred-value:hover {
            background: rgba(255, 255, 255, 0.35);
            transform: scale(1.05);
        }
        
        /* Premium stats section */
        .stats-container {
            display: flex;
            justify-content: space-around;
            margin: 2.5rem 0;
            padding: 2rem 1.5rem;
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 20px;
            box-shadow: 0 8px 24px rgba(252, 182, 159, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .stats-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            background-size: 200% 100%;
            animation: shimmer 3s linear infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .stat-item {
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-item:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #d63031 0%, #e17055 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 0.85rem;
            color: #666;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Premium features grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin: 2.5rem 0;
        }
        
        .feature-item {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1.5rem 1rem;
            border-radius: 16px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            position: relative;
            overflow: hidden;
        }
        
        .feature-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .feature-item:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 12px 28px rgba(102, 126, 234, 0.3);
        }
        
        .feature-item:hover::before {
            opacity: 1;
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            animation: bounce 2s ease-in-out infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .feature-text {
            font-size: 0.95rem;
            color: #333;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }
        
        /* Premium footer */
        .auth-footer {
            text-align: center;
            margin-top: 2.5rem;
            padding-top: 2rem;
            border-top: 2px solid transparent;
            border-image: linear-gradient(90deg, transparent, #e0e0e0, transparent) 1;
            color: #888;
            font-size: 0.9rem;
        }
        
        .powered-by {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.75rem;
            margin-top: 1.25rem;
            flex-wrap: wrap;
        }
        
        .tech-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 24px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: all 0.3s ease;
        }
        
        .tech-badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
        }
        
        /* Streamlit input styling */
        .stTextInput > div > div > input {
            border-radius: 12px !important;
            border: 2px solid #e0e0e0 !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            border: none !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            font-size: 0.9rem !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Success/Error messages */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            font-weight: 500 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    # Header with premium logo and title
    st.markdown("""
    <div class="auth-header">
        <div class="auth-logo">
            <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="logoGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#764ba2;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#f093fb;stop-opacity:1" />
                    </linearGradient>
                    <linearGradient id="logoGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#F7931E;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#FFBB00;stop-opacity:1" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <circle cx="60" cy="60" r="55" fill="none" stroke="url(#logoGradient1)" stroke-width="3" opacity="0.3">
                    <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="20s" repeatCount="indefinite"/>
                </circle>
                <circle cx="60" cy="60" r="45" fill="none" stroke="url(#logoGradient1)" stroke-width="2" opacity="0.5">
                    <animateTransform attributeName="transform" type="rotate" from="360 60 60" to="0 60 60" dur="15s" repeatCount="indefinite"/>
                </circle>
                <circle cx="60" cy="60" r="40" fill="url(#logoGradient1)" filter="url(#glow)">
                    <animate attributeName="r" values="40;42;40" dur="3s" repeatCount="indefinite"/>
                </circle>
                <rect x="35" y="35" width="50" height="6" fill="#FF9933" rx="2"/>
                <rect x="35" y="44" width="50" height="6" fill="white" rx="2"/>
                <rect x="35" y="53" width="50" height="6" fill="#138808" rx="2"/>
                <circle cx="60" cy="47" r="4" fill="none" stroke="#000080" stroke-width="0.5"/>
                <circle cx="60" cy="47" r="2" fill="#000080"/>
                <g transform="translate(60, 72)">
                    <path d="M -8,-5 Q -10,-8 -8,-10 Q -5,-12 0,-10 Q 5,-12 8,-10 Q 10,-8 8,-5 Q 10,-2 8,2 Q 5,5 0,3 Q -5,5 -8,2 Q -10,-2 -8,-5 Z" 
                          fill="url(#logoGradient2)" stroke="white" stroke-width="1" opacity="0.9"/>
                    <circle cx="-4" cy="-3" r="1.5" fill="white">
                        <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="4" cy="-3" r="1.5" fill="white">
                        <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="0" cy="0" r="1.5" fill="white">
                        <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite" begin="0.5s"/>
                    </circle>
                    <line x1="-4" y1="-3" x2="0" y2="0" stroke="white" stroke-width="0.5" opacity="0.6"/>
                    <line x1="4" y1="-3" x2="0" y2="0" stroke="white" stroke-width="0.5" opacity="0.6"/>
                </g>
                <g opacity="0.8">
                    <circle cx="20" cy="30" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="100" cy="40" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="1s"/>
                    </circle>
                    <circle cx="30" cy="90" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="2s"/>
                    </circle>
                    <circle cx="90" cy="85" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="1.5s"/>
                    </circle>
                </g>
            </svg>
        </div>
        <h1 class="auth-title">YojnaMitra-AI</h1>
        <p class="auth-subtitle">Your Intelligent Government Scheme Assistant</p>
        <p class="auth-tagline">
            <span style="display: inline-flex; align-items: center; gap: 0.5rem;">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <circle cx="8" cy="8" r="7" fill="#FF6B35"/>
                    <path d="M8 4 L8 9 L11 11" stroke="white" stroke-width="1.5" stroke-linecap="round" fill="none"/>
                </svg>
                Powered by AWS Bedrock • Qwen3 235B • RAG Workflow
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo credentials badge (prominent)
    st.markdown("""
    <div class="demo-badge">
        <div class="demo-badge-title">🎯 HACKATHON DEMO - INSTANT ACCESS</div>
        <div class="demo-credentials">
            <div class="demo-cred-item">
                <div class="demo-cred-label">👤 Username</div>
                <div class="demo-cred-value">demo</div>
            </div>
            <div class="demo-cred-item">
                <div class="demo-cred-label">🔑 Password</div>
                <div class="demo-cred-value">demo123</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats section
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">500M+</div>
            <div class="stat-label">Target Users</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">500+</div>
            <div class="stat-label">Schemes</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">95%</div>
            <div class="stat-label">Accuracy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render appropriate page
    if st.session_state.auth_page == 'login':
        login_page = LoginPage()
        login_page.render()
    elif st.session_state.auth_page == 'register':
        registration_page = RegistrationPage()
        registration_page.render()
    
    # Features grid
    st.markdown("""
    <div class="features-grid">
        <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <div class="feature-text">AI-Powered Matching</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🗣️</div>
            <div class="feature-text">Hinglish Support</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📱</div>
            <div class="feature-text">Mobile Friendly</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🔒</div>
            <div class="feature-text">Secure & Private</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="auth-footer">
        <p>🏆 AI for Bharat Hackathon 2026 Finals</p>
        <div class="powered-by">
            <span>Powered by:</span>
            <span class="tech-badge">AWS Bedrock</span>
            <span class="tech-badge">Qwen3 235B</span>
            <span class="tech-badge">Titan Embeddings v2</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
