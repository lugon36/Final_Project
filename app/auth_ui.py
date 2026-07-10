# app/auth_ui.py
import streamlit as st
from queries import verify_user_login, register_new_user

def render_auth_gateway():
    st.title("🩺 ONCASIS: Clinical Access Portal")
    tab_login, tab_register = st.tabs(["🔐 System Login", "📝 Register New Clinician"])
    
    with tab_login:
        with st.form("login_form"):
            login_user = st.text_input("Username")
            login_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Access ONCASIS"):
                if verify_user_login(login_user, login_pwd):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = login_user
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
                    
    with tab_register:
        with st.form("register_form"):
            reg_user = st.text_input("New Username")
            reg_email = st.text_input("Institutional Email")
            reg_pwd = st.text_input("Secure Password", type="password")
            if st.form_submit_button("Register Account"):
                if register_new_user(reg_user, reg_email, reg_pwd):
                    st.success("Account created! You may now log in.")
                else:
                    st.error("Registration failed. Username may already be in use.")