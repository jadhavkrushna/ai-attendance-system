import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_background_home, style_base_layout
def home_screen():


    header_home()
    style_background_home()
    style_base_layout()

col1, col2 = st.columns(2,gap="large")

with col1:
    st.header("I'm student")
    st.image("https://i.ibb.co/2sZzj8C/student.png", width=400)
    if st.button("Student portal", type="primary", icon="👩‍🎓", icon_position='right'):
        st.write("Navigating to Student Dashboard...")
        st.session_state['current_screen'] = 'dashboard_student'
        st.rerun()

with col2:
    st.header("I'm teacher")
    st.image("https://i.ibb.co/2sZzj8C/teacher.png", width=400)
    if st.button("Teacher portal", type="primary", icon="👩‍🏫", icon_position='right'):
        st.write("Navigating to Teacher Dashboard...")
        st.session_state['current_screen'] = 'dashboard_teacher'
        st.rerun()

footer_home()