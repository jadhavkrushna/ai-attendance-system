import streamlit as st


def footer_home():
    logo = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(
        f"""
        <div style="margin-top: 2rem; display: flex;gap:6px; align-items: center; justify-content: center;">
            <p style="font-weight: bold;color:white">Copyright 2024 SNAP CLASS. All rights reserved.</p>
            <img src="{logo}" style="max-height: 25px;" />
            
        </div>
        """,
        unsafe_allow_html=True,
    )


