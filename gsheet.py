import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import streamlit as st
import json
import tempfile

# Define scope
creds_dict = st.secrets["Credentials"]

# Temporary write to a file
with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
    json.dump(creds_dict, tmp)
    tmp.flush()
    creds = ServiceAccountCredentials.from_json_keyfile_name(tmp.name, scope)

client = gspread.authorize(creds)

# Open the spreadsheet
spreadsheet = client.open("X101_Tasks")  # Name of your Google Sheet
worksheet = spreadsheet.worksheet("tasks")

def get_all_tasks():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def append_task(task_dict):
    task_values = list(task_dict.values())
    worksheet.append_row(task_values)

def update_task(task_id, update_dict):
    df = get_all_tasks()
    try:
        row_index = df[df['ID'] == task_id].index[0] + 2  # +2 for header + 1-based indexing
        for col, val in update_dict.items():
            col_index = df.columns.get_loc(col) + 1
            worksheet.update_cell(row_index, col_index, val)
        return True
    except IndexError:
        return False

def log_activity(task_id, message):
    df = get_all_tasks()
    row_index = df[df['ID'] == task_id].index[0] + 2
    col_index = df.columns.get_loc("Activity Log") + 1
    prev_log = worksheet.cell(row_index, col_index).value or ""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_log = f"{prev_log}\n[{timestamp}] {message}"
    worksheet.update_cell(row_index, col_index, new_log)

def get_activity_logs():
    df = get_all_tasks()
    logs = []

    for _, row in df.iterrows():
        task_id = row["ID"]
        title = row["Title"]
        log = row.get("Activity Log", "")
        if log:
            entries = log.strip().split("||")
            for entry in entries:
                logs.append({
                    "Task ID": task_id,
                    "Title": title,
                    "Log": entry
                })

    # Sort by timestamp inside log string (assumes log starts with [YYYY-MM-DD HH:MM:SS])
    logs.sort(key=lambda x: x["Log"].split(']')[0].strip('['), reverse=True)
    return logs

