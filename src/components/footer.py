import streamlit as st


def footer_home():
    
    logo_url = "https://i.ibb.co/YTYGn5qV/classlogo.png"
    
    st.markdown(f"""
       <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center">
       <p style="font-weight:bold; color:white;">Copyright 2024 SNAP CLASS. All rights reserved.</p>
       <img src="{logo_url}" style="max-height: 25px;" />
       </div>
        
        """, unsafe_allow_html=True)


def footer_dashboard():
       
    logo_url = "https://i.ibb.co/YTYGn5qV/classlogo.png"
    
    st.markdown(f"""
       <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center">
       <p style="font-weight:bold; color:black;">Copyright 2024 SNAP CLASS. All rights reserved.</p>
       <img src="{logo_url}" style="max-height: 25px;" />
       </div>
        """,
        unsafe_allow_html=True,
    )

