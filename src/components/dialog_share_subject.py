import streamlit as st

import segno
import io
from src.database.db import generate_subject_registry_code


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    app_domain = "fluentia-main.streamlit.app"
    registry_code = generate_subject_registry_code(subject_code) if str(subject_code).isdigit() else subject_code
    join_url = f"{app_domain}/?join-code={registry_code}"

    st.header("Scan to Join")

    qr = segno.make(join_url)

    out = io.BytesIO()

    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language="text")
        st.code(registry_code, language="text")
        st.info('Copy this link to share on Whatsapp or Email')

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption='QRCODE for class joining')

        
