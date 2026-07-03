import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.db import resolve_subject_registry_code
from src.database.config import supabase

import time


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data['student_id']

    subject_id = resolve_subject_registry_code(subject_code)
    subject = None

    if subject_id is not None:
        res = supabase.table('subjects').select('subject_id, name').eq('subject_id', subject_id).execute()
        if res.data:
            subject = res.data[0]
    else:
        res = supabase.table('subjects').select('subject_id, name').eq('subject_code', subject_code).execute()
        if res.data:
            subject = res.data[0]

    if not subject:
        st.error('Registry code not found!')
        if st.button('Close'):
            st.query_params.clear()
            st.rerun()
        return

    check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
    if check.data:
        st.info('Youre already enrolled!')
        if st.button('Got it!'):
            st.query_params.clear()
            st.rerun()
        return
    st.markdown(f"Would you like to enroll in **{subject['name']}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('No thanks'):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button('Yes enroll now!', type='primary', width='stretch'):
            enroll_student_to_subject(student_id, subject['subject_id'])
            st.success('Joined succesfully!')
            st.query_params.clear()
            time.sleep(2)
            st.rerun()
