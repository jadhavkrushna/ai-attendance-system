import streamlit as st

from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.database.db import teacher_login, create_teacher, check_teacher_exists


# ---------------------------------------------------------------------------
# Auth helpers – connected to real DB logic
# ---------------------------------------------------------------------------

def login_teacher(username: str, password: str) -> bool:
    """Return True if credentials are valid, False otherwise."""
    try:
        teacher = teacher_login(username, password)
        if teacher:
            st.session_state.teacher_data = teacher
            return True
    except Exception as e:
        st.error(f"Login database error: {str(e)}")
    return False


def register_teacher(username: str, name: str, password: str, password_confirm: str):
    """Register a new teacher. Returns (success: bool, message: str)."""
    if not username or not name or not password:
        return False, "All fields are required."
    if password != password_confirm:
        return False, "Passwords do not match."
    try:
        if check_teacher_exists(username):
            return False, "Username is already taken."
        create_teacher(username, password, name)
        return True, f"Teacher '{name}' registered successfully!"
    except Exception as e:
        return False, f"Registration database error: {str(e)}"


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password')
    st.write("")
    st.write("")

    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')
    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()


def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='registerbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Register your teacher profile')
    st.write("")
    st.write("")

    teacher_username = st.text_input("Enter username", placeholder='Jameslebron_23')
    teacher_name = st.text_input("Enter name", placeholder='James Lebron')
    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")
    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()