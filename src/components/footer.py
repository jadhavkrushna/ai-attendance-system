import streamlit as st


def _footer():
    logo = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(
        f"""
        <div style="margin-top: 30px; display: flex; align-items: center; justify-content: center; gap:6px;">
            <p style="font-weight: bold; color:#172033;">Copyright 2024 SNAP CLASS. All rights reserved.</p>
            <img src="{logo}" style="max-height: 30px;" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer_home():
    
    logo_url = "https://i.ibb.co/YTYGn5qV/classlogo.png"
    
    st.markdown(f"""
       <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center">
       <p style="font-weight:bold; color:white;">Copyright 2024 SNAP CLASS. All rights reserved.</p>
       <img src="{logo_url}" style="max-height: 25px;" />
       </div>
        
        """, unsafe_allow_html=True)
