import streamlit as st

from src.components.header import header_home
from src.components.footer import footer_home

from src.ui.base_layout import style_background_home, style_base_layout


def home_screen():
    header_home()
    style_background_home()
    style_base_layout()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.header("I'm a student")
        st.image("https://i.ibb.co/84409Lrt/mascot-student.png", width=120)
        if st.button("Student portal", type="primary", use_container_width=True):
            st.session_state['Login_Type'] = "student"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.header("I'm a teacher")
        st.image("https://i.ibb.co/CsmQQV6X/mascot-prof.png", width=145)
        if st.button("Teacher portal", type="primary"):
            st.session_state['Login_Type'] = "teacher"
            st.rerun()
        
    footer_home()
