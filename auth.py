import streamlit as st
import pandas as pd
from datetime import datetime
from pytz import timezone
import gspread

IST = timezone("Asia/Kolkata")

def get_sheet_df(sheet):
    return pd.DataFrame(sheet.get_all_records())

def update_cell(sheet, row, col, value):
    sheet.update_cell(row, col, value)

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
