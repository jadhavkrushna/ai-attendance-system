import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen


def main():
    if "Login_Type" not in st.session_state:
        st.session_state["Login_Type"] = None

    login_type = st.session_state["Login_Type"]

    if login_type == "student":
        student_screen()
    elif login_type == "teacher":
        teacher_screen()
    else:
        home_screen()


if __name__ == "__main__":
    main()
