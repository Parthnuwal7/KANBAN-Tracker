import streamlit as st
import pandas as pd
from datetime import datetime
from pytz import timezone
import gspread_utils
from gspread_utils import get_sheet_df, update_cell

IST = timezone("Asia/Kolkata")

def load_users():
    df = get_sheet_df("Users")
    df['Password'] = df['Password'].astype(str)
    return df

def authenticate_user(username, password):
    users_df = load_users()
    user_row = users_df[users_df['Username'] == username]

    if not user_row.empty:
        stored_password = user_row.iloc[0]['Password']
        if password == stored_password:  # plaintext match
            now_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            update_cell("Users", username, "Username", "Last Login", now_ist)
            return {
                "role": user_row.iloc[0]['Role'],
                "name": user_row.iloc[0]['Name']
            }

    return None
