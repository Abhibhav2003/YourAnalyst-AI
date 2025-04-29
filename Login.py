import streamlit as st
import re
import time
from utils.user_manager import UserManager
from utils.password_recovery import PasswordRecovery
import json
from pathlib import Path

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'remember_me' not in st.session_state:
    st.session_state.remember_me = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "login"
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = {}
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()

# Initialize managers
user_manager = UserManager()
password_recovery = PasswordRecovery()

# Session timeout (30 minutes)
SESSION_TIMEOUT = 1800
# Rate limiting (5 attempts per 15 minutes)
MAX_ATTEMPTS = 5
ATTEMPT_WINDOW = 900  # 15 minutes

def check_session_timeout():
    if time.time() - st.session_state.last_activity > SESSION_TIMEOUT:
        st.session_state.logged_in = False
        return True
    return False

def check_rate_limit(username):
    current_time = time.time()
    if username in st.session_state.login_attempts:
        attempts = st.session_state.login_attempts[username]
        if len(attempts) >= MAX_ATTEMPTS:
            if current_time - attempts[0] < ATTEMPT_WINDOW:
                return False
            else:
                st.session_state.login_attempts[username] = []
    return True

def update_login_attempts(username):
    current_time = time.time()
    if username not in st.session_state.login_attempts:
        st.session_state.login_attempts[username] = []
    st.session_state.login_attempts[username].append(current_time)
    # Remove old attempts
    st.session_state.login_attempts[username] = [
        t for t in st.session_state.login_attempts[username]
        if current_time - t < ATTEMPT_WINDOW
    ]

def calculate_password_strength(password):
    strength = 0
    if len(password) >= 8:
        strength += 1
    if re.search(r'[A-Z]', password):
        strength += 1
    if re.search(r'[a-z]', password):
        strength += 1
    if re.search(r'\d', password):
        strength += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 1
    return strength

def show_password_strength(password):
    strength = calculate_password_strength(password)
    if not password:
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    colors = {
        0: "red",
        1: "orange",
        2: "yellow",
        3: "lightgreen",
        4: "green",
        5: "darkgreen"
    }
    
    for i in range(5):
        with eval(f"col{i+1}"):
            st.markdown(f"""
            <div style="
                height: 5px;
                background-color: {colors.get(strength, 'gray')};
                border-radius: 2px;
            "></div>
            """, unsafe_allow_html=True)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    if not username:
        return False
    if len(username) < 3:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True

def validate_password(password):
    if not password:
        return False
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def forgot_password():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.title("Reset Password 🔑")
        st.markdown("""
        <style>
        .stTitle {
            color: #1f77b4;
            font-size: 2.5em;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with col2:
        with st.container(key="ForgotPasswordForm"):
            st.markdown("### Enter your email to reset password")
            email = st.text_input("Email", placeholder="Enter your registered email")
            
            if st.button("Send Recovery Link", type="primary", use_container_width=True):
                if not validate_email(email):
                    st.error("Please enter a valid email address!")
                else:
                    token = password_recovery.generate_token(email)
                    success, message = password_recovery.send_recovery_email(email, token)
                    if success:
                        st.success(message)
                        st.session_state.current_page = "login"
                        st.rerun()
                    else:
                        st.error(message)
            
            st.markdown("---")
            if st.button("Back to Login", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()

def signup():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.title("Create Account 🚀")
        st.markdown("""
        <style>
        .stTitle {
            color: #1f77b4;
            font-size: 2.5em;
        }
        </style>
        """, unsafe_allow_html=True)
        
    with col2:
        with st.container(key="SignupForm"):
            st.markdown("### Join Our Platform")
            
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email")
            
            col_pass1, col_pass2 = st.columns([3, 1])
            with col_pass1:
                password = st.text_input("Password", type="password", placeholder="Create a password")
            with col_pass2:
                show_pass = st.checkbox("Show", key="show_signup_pass")
                if show_pass:
                    st.text_input("", value=password, disabled=True)
            
            show_password_strength(password)
            
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            st.markdown("""
            Password requirements:
            - At least 8 characters long
            - Contains at least one uppercase letter
            - Contains at least one lowercase letter
            - Contains at least one number
            - Contains at least one special character (!@#$%^&*(),.?":{}|<>)
            """)
            
            if st.button("Sign Up", type="primary", use_container_width=True):
                if not validate_username(username):
                    st.error("Username must be at least 3 characters long and can only contain letters, numbers, and underscores!")
                elif not validate_email(email):
                    st.error("Please enter a valid email address!")
                elif not validate_password(password):
                    st.error("Password does not meet the requirements!")
                elif password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, message = user_manager.create_user(username, password, email)
                    if success:
                        st.success(message)
                        st.session_state.current_page = "login"
                        st.rerun()
                    else:
                        st.error(message)
            
            st.markdown("---")
            st.markdown("Already have an account?")
            if st.button("Login", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()

def login():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.title("Welcome Back! 👋")
        
    with col2:
        with st.container(key="LoginForm"):
            st.markdown("### Login to Your Account")
            
            username = st.text_input("Username", placeholder="Enter your username")
            
            col_pass1, col_pass2 = st.columns([3, 1])
            with col_pass1:
                password = st.text_input("Password", type="password", placeholder="Enter your password")
            with col_pass2:
                show_pass = st.checkbox("Show", key="show_login_pass")
                if show_pass:
                    st.text_input("", value=password, disabled=True)
            
            col3, col4 = st.columns([1, 1])
            with col3:
                remember_me = st.checkbox("Remember me")
                st.session_state.remember_me = remember_me
                
            with col4:
                if st.button("Forgot Password?"):
                    st.session_state.current_page = "forgot_password"
                    st.rerun()
            
            if st.button("Login", type="primary", use_container_width=True):
                if not validate_username(username):
                    st.error("Please enter a valid username!")
                elif not validate_password(password):
                    st.error("Please enter a valid password!")
                else:
                    if not check_rate_limit(username):
                        st.error("Too many login attempts. Please try again later.")
                    else:
                        success, message = user_manager.verify_user(username, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.last_activity = time.time()
                            if remember_me:
                                st.session_state.username = username
                            st.success(message)
                            st.rerun()
                        else:
                            update_login_attempts(username)
                            st.error(message)
            
            st.markdown("---")
            st.markdown("Don't have an account?")
            if st.button("Sign Up", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()

# Check session timeout
if st.session_state.logged_in and check_session_timeout():
    st.warning("Your session has expired. Please login again.")
    st.session_state.logged_in = False

if st.session_state.current_page == "login":
    login_page = st.Page(login, title="Login")
elif st.session_state.current_page == "signup":
    signup_page = st.Page(signup, title="Sign Up")
else:
    forgot_password_page = st.Page(forgot_password, title="Forgot Password")

Home = st.Page(
    "Pages/Home.py", title="Home", default=True
)
Upload = st.Page(
    "Pages/1_Upload.py", title="Upload"
)
Analyse = st.Page(
    "Pages/2_Analyse.py", title="Analyse"
)
Visualize = st.Page(
    "Pages/3_Visualize.py", title="Visualize"
)
Queries = st.Page(
    "Pages/4_AutoAnalysis.py",title = "Queries"
)
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Pages": [Home, Upload, Analyse, Visualize,Queries]
        }
    )
else:
    if st.session_state.current_page == "login":
        pg = st.navigation([login_page])
    elif st.session_state.current_page == "signup":
        pg = st.navigation([signup_page])
    else:
        pg = st.navigation([forgot_password_page])

pg.run()