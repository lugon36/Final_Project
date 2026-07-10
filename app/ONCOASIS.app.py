import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth_ui import render_auth_gateway
from main_ui import render_main_application

# 1. Page configuration (This must be the first Streamlit command)
st.set_page_config(
    page_title="ONCOASIS", 
    page_icon="🩺", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Session state initialization for authentication
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

# 3. Modular interface imports
from auth_ui import render_auth_gateway
from main_ui import render_main_application

# 4. Application Routing Logic 
if not st.session_state["logged_in"]:
    # Show login/registration screen if not authenticated
    render_auth_gateway()
else:
    # Show the main clinical dashboard if authenticated
    render_main_application()