import streamlit as st
import json

# Load from Streamlit secrets
def load_users():
    return st.secrets["users"]

def authenticate_user(username):
    users = load_users()
    role = users.get(username)
    if role:
        return role
    return None
