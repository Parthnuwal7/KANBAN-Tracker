import streamlit as st
import pandas as pd
from datetime import datetime
from pytz import timezone
import gspread

IST = timezone("Asia/Kolkata")

# Connect to Google Sheet
gc = gspread.service_account_from_dict(st.secrets["google"])
sheet = gc.open("X101_Tasks")  
users_sheet = sheet.worksheet("Users")

def get_sheet_df(sheet_obj):
    return pd.DataFrame(sheet_obj.get_all_records())

def update_cell_by_username(sheet_obj, username, match_col, update_col, value):
    data = sheet_obj.get_all_records()
    for idx, row in enumerate(data, start=2):  # start=2 to account for headers
        if row.get(match_col) == username:
            col_names = sheet_obj.row_values(1)
            col_idx = col_names.index(update_col) + 1
            sheet_obj.update_cell(idx, col_idx, value)
            break

def load_users():
    df = get_sheet_df(users_sheet)
    df['Password'] = df['Password'].astype(str)
    return df

def authenticate_user(username, password):
    users_df = load_users()
    user_row = users_df[users_df['Username'] == username]

    if not user_row.empty:
        stored_password = user_row.iloc[0]['Password']
        if password == stored_password:  # plaintext match
            now_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            update_cell_by_username(users_sheet, username, "Username", "Last Login", now_ist)
            return {
                "role": user_row.iloc[0]['Role'],
                "name": user_row.iloc[0]['Name']
            }

    return None


# def get_sheet_df(sheet):
#     return pd.DataFrame(sheet.get_all_records())

# def update_cell(sheet, row, col, value):
#     sheet.update_cell(row, col, value)

# def load_users():
#     df = get_sheet_df("Users")
#     df['Password'] = df['Password'].astype(str)
#     return df

# def authenticate_user(username, password):
#     users_df = load_users()
#     user_row = users_df[users_df['Username'] == username]

#     if not user_row.empty:
#         stored_password = user_row.iloc[0]['Password']
#         if password == stored_password:  # plaintext match
#             now_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
#             update_cell("Users", username, "Username", "Last Login", now_ist)
#             return {
#                 "role": user_row.iloc[0]['Role'],
#                 "name": user_row.iloc[0]['Name']
#             }

#     return None
