import streamlit as st
from src.database.db import enroll_student_to_subject, resolve_subject_registry_code
from src.database.config import supabase

import time


@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write('Enter the registry code provided by your teacher to enroll')
    join_code = st.text_input('Subject Registry Code', placeholder='Eg. WHZ3UW')

    if st.button('Enroll now', type='primary', width='stretch'):
        if join_code:
            subject_id = resolve_subject_registry_code(join_code)
            subject = None

            if subject_id is not None:
                res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_id', subject_id).execute()
                if res.data:
                    subject = res.data[0]
            else:
                res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_code', join_code).execute()
                if res.data:
                    subject = res.data[0]

            if subject:
                student_id = st.session_state.student_data['student_id']

                check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                if check.data:
                    st.warning('You are already enrolled in this program')
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.success('Succesfully enrolled!')
                    time.sleep(1)
                    st.rerun()
            else:
                st.error('Registry code not found!')
        else:
            st.warning('Please enter a subject code')
