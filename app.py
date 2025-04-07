import streamlit as st
import pandas as pd
from datetime import datetime,timedelta, timezone
import streamlit.components.v1 as components
import gsheet as gs
from streamlit_autorefresh import st_autorefresh
import pytz

from auth import authenticate_user
from gsheet import get_all_tasks, append_task, update_task, log_activity

st.set_page_config(page_title="X-101 Kanban Board", layout="wide")
st.title("🧠 Project X-101 Kanban Board")
ist = pytz.timezone('Asia/Kolkata')

#-- LOGIN Module ---
if "user" not in st.session_state:
    st.title("🔐 Login to Project X101")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user_info = authenticate_user(username, password)
            if user_info:
                st.session_state["user"] = {
                    "username": username,
                    "role": user_info["role"],
                    "name": user_info["name"]
                }
                st.success(f"Welcome {user_info['name']}!")
                st.rerun()

            else:
                st.error("Invalid username or password")

else:
    user = st.session_state["user"]
    role = user["role"]
    username = user["username"]
    st.sidebar.write(f"👋 Logged in as {user['name']} ({user['role']})")
    if st.sidebar.button("Logout"):
        del st.session_state["user"]
        st.rerun()


tab1, tab2, tab3,tab4 = st.tabs(["🏠 Home", "➕ Add Task", "📜 Activity Log","📌 My Tasks"])


# --- Load Tasks ---
df = get_all_tasks()

# Find tasks currently under voting
voting_tasks = df[
    (df["Status"] == "Voting") & 
    (df["Upvotes"] != "AUTO-MOVED")
]

role = st.session_state["user"]["role"] if "user" in st.session_state else None

# role = user["role"]
with tab2:
    st.header("➕ Add New Task")
    # show Kanban in read-only mode
    if role in ["Editor", "Admin"]:
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        deadline = st.date_input("Deadline")

        assignees = ["Parth", "Arka", "Mohit", "Rajat", "Nishtha"]
        if role == "Admin":
            assigned_to = st.selectbox("Assign to", assignees)
        else:
            assigned_to = user["name"]

        if st.button("Add Task"):
            task_id = f"TSK{int(datetime.now(ist).timestamp())}"  # unique task ID
            now = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

            task_data = {
                "ID": task_id,
                "Title": title,
                "Description": description,
                "Assigned To": assigned_to,
                "Created By": user["name"] ,
                "Status": "To Be Done",
                "Priority": priority,
                "Deadline": deadline.strftime('%Y-%m-%d'),
                "Timestamp": now,
                "Last Updated": now,
                "Activity Log": f"[{now}] Task created by {user["name"]}",
                "Upvotes": "",
                "Downvotes": "",
                "Voted By": "",
                "Previous Status":""
            }

            append_task(task_data)
            st.success("Task added!")
            st.rerun()

with tab1:
    if not voting_tasks.empty:
        st.markdown("### 🔔 Tasks Under Voting")
        for _, task in voting_tasks.iterrows():
            anchor_id = f"vote_{task['ID']}"
            # Use custom anchor for scroll
            st.markdown(f"- [{task['Title']}](#{anchor_id})")
            # Add invisible anchor in the card itself later (already handled)

    # --- Display Kanban Board ---
    statuses = ["To Be Done", "In Progress", "Completed","Voting"]
    columns = st.columns(4)

    for i, status in enumerate(statuses):
        with columns[i]:
            st.subheader(status)
            if not df.empty and "Status" in df.columns:
                for _, task in df[df["Status"] == status].iterrows():
                    with st.container(border=True):
                        st.markdown(f'<div id="vote_{task["ID"]}"></div>', unsafe_allow_html=True)
                        st.markdown(f"**{task['Title']}**")
                        if task["Status"] == "Completed":
                            st.success("✅ Task marked as Completed")
                        st.caption(f"Assigned to: {task['Assigned To']}")
                        st.markdown(f"Priority: `{task['Priority']}` | Due: {task['Deadline']}")
                        st.markdown(task['Description'])

                        status_flow = {
                            "To Be Done": "In Progress",
                            "In Progress": "Completed",
                            "Completed": "Archived"
                        }

                        is_voting = task["Status"] == "Voting" and task["Upvotes"] != "AUTO-MOVED"
                        if is_voting:
                            upvotes = task.get("Upvotes", "").split(",") if task["Upvotes"] else []
                            downvotes_raw = task.get("Downvotes", "").split("|") if task["Downvotes"] else []
                            downvotes = [entry.split(":")[0] for entry in downvotes_raw if ":" in entry]

                            st.markdown("🗳️ **Voting In Progress**")
                            st.progress(min(len(upvotes) / 5, 1.0))
                            st.write(f"👍 Upvotes: `{len(upvotes)}`")
                            st.write(f"👎 Downvotes: `{len(downvotes)}`")

                            voted_by = task.get("Voted By", "").split(",") if task["Voted By"] else []
                            not_voted = [u for u in ["Parth", "Arka", "Mohit", "Rajat", "Nishtha"] if u not in voted_by]
                            st.caption(f"Not Voted: {', '.join(not_voted)}")
                            if task["Status"] == "Voting" and task["Previous Status"] == "Completed" and role in ["Editor", "Admin"]:
                                st.success("✅ Task is completed. No further voting allowed.")
                                continue  # Skip further voting logic


                            last_updated = datetime.strptime(task["Last Updated"], '%Y-%m-%d %H:%M:%S')
                            last_updated = last_updated.replace(tzinfo=timezone.utc).astimezone(ist)
                            elapsed_time = datetime.now(ist) - last_updated

                            if len(upvotes) >= 4:
                                next_status = status_flow.get(task.get("Previous Status", ""), "Completed")

                                update_task(task["ID"], {
                                    "Status": next_status,
                                    "Upvotes": "",  # Reset
                                    "Downvotes": "",  # Reset
                                    "Voted By": "",  # Reset
                                    "Previous Status": "",  # Reset
                                    "Last Updated": datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
                                })
                                log_activity(task["ID"], f"Task auto-moved from Voting to {next_status}")
                                st.rerun()

                            elif elapsed_time > timedelta(hours=12) and role == "Admin":
                                if st.button("🛠️ Override & Move (12h passed)", key=f"{task['ID']}_override"):
                                    next_status = status_flow.get(task["Previous Status"], "Completed")
                                    update_task(task["ID"], {
                                        "Status": next_status,
                                        "Upvotes": "AUTO-MOVED",
                                        "Last Updated": datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
                                    })
                                    log_activity(task["ID"], f"{user["name"]} manually moved task to {next_status} after timeout")
                                    st.rerun()

                        if task["Status"] not in ["Voting","Completed"] and role in ["Editor", "Admin"]:
                            if role == "Admin" or task["Created By"] == user["name"]:
                                if st.button("📤 Send for Voting", key=f"{task['ID']}_send_vote"):
                                    now = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
                                    update_task(task["ID"], {
                                        "Status": "Voting",
                                        "Voting Start": now,
                                        "Previous Status": task["Status"],
                                        "Last Updated": now
                                    })
                                    log_activity(task["ID"], f"{user["name"]} initiated voting to move task from {task['Status']}")
                                    st.success("Task sent for voting!")
                                    st.rerun()

                        if task["Status"] == "Voting" and role in ["Editor", "Admin"]:
                            voted_by = task.get("Voted By", "")
                            already_voted = user["name"] in voted_by.split(",") if voted_by else False

                            if not already_voted:
                                st.markdown("#### 🗳 Voting In Progress")
                                cols = st.columns([1, 1])
                                with cols[0]:
                                    if st.button("👍 Upvote", key=f"{task['ID']}_upvote"):
                                        update_task(task["ID"], {
                                            "Upvotes": (task.get("Upvotes", "") + f",{user["name"]}").strip(","),
                                            "Voted By": (voted_by + f",{user["name"]}").strip(","),
                                            "Last Updated": datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
                                        })
                                        log_activity(task["ID"], f"{user["name"]} upvoted the task.")
                                        st.success("You voted 👍")
                                        st.rerun()
                                with cols[1]:
                                    downvote_reason = st.text_input("Reason for 👎 downvote", key=f"{task['ID']}_reason")
                                    if st.button("👎 Downvote", key=f"{task['ID']}_downvote"):
                                        reason_log = f"{user["name"]}:{downvote_reason}" if downvote_reason else f"{user["name"]}:No reason"
                                        update_task(task["ID"], {
                                            "Downvotes": (task.get("Downvotes", "") + f"|{reason_log}").strip("|"),
                                            "Voted By": (voted_by + f",{user["name"]}").strip(","),
                                            "Last Updated": datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
                                        })
                                        log_activity(task["ID"], f"{user["name"]} downvoted the task with reason: {downvote_reason}")
                                        st.error("You downvoted 👎")
                                        st.rerun()

                        if role == "Admin":
                            assignees = ["Parth", "Arka", "Mohit", "Rajat", "Nishtha"]
                            if task["Assigned To"] not in assignees:
                                assignees.append(task["Assigned To"])

                            new_assignee = st.selectbox(
                                "Reassign to",
                                assignees,
                                index=assignees.index(task['Assigned To']),
                                key=f"{task['ID']}_assign"
                            )

                            if st.button("Update Assignee", key=f"{task['ID']}_assign_btn"):
                                update_task(task["ID"], {
                                    "Assigned To": new_assignee,
                                    "Last Updated": datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
                                })
                                log_activity(task["ID"], f"{user["name"]} reassigned task to {new_assignee}")
                                st.rerun()
            else:
                st.info("No tasks to display yet. Start by adding one.")
                    # Allow moving only own tasks (editors), or any task (admin)
                if role == "Admin" or task["Assigned To"] == user["name"]:
                    if status != "Completed":
                        next_status = statuses[statuses.index(status)+1]
                        if st.button(f"Move to {next_status}", key=f"{task['ID']}_move"):
                            update_task(task["ID"], {
                                "Status": next_status,
                                "Last Updated": datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
                            })
                            log_activity(task["ID"], f"{user["name"]} moved task to {next_status}")
                            st.rerun()

with tab3:
    st.header("📜 Activity Log")

    logs = gs.get_activity_logs()
    st_autorefresh(interval=10 * 1000, key="activity_refresh")
    
    if logs:
        entries = []

        for log in logs:
            title = log['Title']
            task_id = log['Task ID']
            for line in log['Log'].split("\n"):
                if line.strip():
                    try:
                        ts_part, message = line.strip().split("]", 1)
                        timestamp = datetime.strptime(ts_part.strip("["), "%Y-%m-%d %H:%M:%S")
                        entries.append({
                            "timestamp": timestamp,
                            "title": title,
                            "task_id": task_id,
                            "message": message.strip()
                        })
                    except Exception:
                        continue
        
        # Sort entries by timestamp (newest first)
        sorted_entries = sorted(entries, key=lambda x: x["timestamp"], reverse=True)

        # Initialize session state to track last seen timestamp
        if "last_seen_log_time" not in st.session_state:
            st.session_state.last_seen_log_time = datetime.min

        # Detect new entries
        new_entries = [entry for entry in sorted_entries if entry["timestamp"] > st.session_state.last_seen_log_time]

        if new_entries:
            st.toast(f"🔔 {len(new_entries)} new update(s) in the activity log!")
            st.markdown("""
                <audio autoplay>
                    <source src="https://cdn.uppbeat.io/audio-files/d927511931994ce45cf5b95b34e23536/0e2f38fd60ca5cbe2013a8a86314ee46/45c8ea359f9532cf9d3add600059d6e3/STREAMING-ui-bell-ding-om-fx-2-2-00-04.mp3" type="audio/mpeg">
                </audio>
            """, unsafe_allow_html=True)

            # Update last seen timestamp
            st.session_state.last_seen_log_time = max(entry["timestamp"] for entry in new_entries)

        for entry in sorted_entries:
            st.markdown(f"""
                <div style="
                    background-color: #f1f3f5;
                    border-left: 5px solid #4B9CD3;
                    border-radius: 8px;
                    padding: 10px 14px;
                    margin-bottom: 12px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
                ">
                    <div style="font-weight: 600; font-size: 18px; color: #333;">
                        {entry['title']} <span style="font-size: 11px; color: #666;">(ID: {entry['task_id']})</span>
                    </div>
                    <div style="font-size: 15px; color: #222; margin-top: 4px;">
                        {entry['message']}
                    </div>
                    <div style="font-size: 11px; color: #888; margin-top: 6px; text-align: right;">
                        {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity yet.")

# ----- LOGIC FOR TAB 4 Personalized tab --------
# Define priority order for sorting
priority_order = {'High': 1, 'Medium': 2, 'Low': 3}

# Define status stages for personalized Kanban
status_stages = ["To Be Done", "In Progress", "Completed", "Voting"]

def render_my_kanban(df_tasks):
    st.title("📌 My Tasks")

    username = st.session_state.get("user", {}).get("username")
    name = st.session_state.get("user",{}).get("name")
    if not username:
        st.warning("You must be logged in to view your tasks.")
        return

    df_user_tasks = df_tasks[df_tasks["Assigned To"] == name].copy()
    df_user_tasks["Deadline"] = pd.to_datetime(df_user_tasks["Deadline"], errors='coerce')
    df_user_tasks["Priority Rank"] = df_user_tasks["Priority"].map(priority_order)

    # Create 4 columns
    col1, col2, col3, col4 = st.columns(4)
    status_to_col = {
        "To Be Done": col1,
        "In Progress": col2,
        "Completed": col3,
        "Voting": col4
    }

    # Card styling
    card_style = """
        background-color: #242424;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 12px solid {color};
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    """

    # Priority-based color mapping
    priority_colors = {
        "High": "#e74c3c",     # Red
        "Medium": "#f39c12",   # Orange
        "Low": "#2ecc71",      # Green
    }

    for status in status_stages:
        status_tasks = df_user_tasks[df_user_tasks["Status"] == status].sort_values(
            by=["Deadline", "Priority Rank"]
        )

        with status_to_col[status]:
            st.markdown(f"### 📍 {status}")
            if status_tasks.empty:
                st.markdown("*No tasks*")
            else:
                for _, task in status_tasks.iterrows():
                    color = priority_colors.get(task["Priority"], "#3498db")  # default blue
                    st.markdown(f"""
                        <div style="{card_style.format(color=color)}">
                            <h5>📝 {task['Title']}</h5>
                            <p><strong>📅 Deadline:</strong> {task['Deadline'].strftime('%Y-%m-%d') if pd.notnull(task['Deadline']) else 'N/A'}</p>
                            <p><strong>🔥 Priority:</strong> {task['Priority']}</p>
                            <p><strong>👤 By:</strong> {task['Created By']}</p>
                            <p><strong>🕒 Updated:</strong> {task['Last Updated']}</p>
                        </div>
                    """, unsafe_allow_html=True)


with tab4:
    render_my_kanban(df)
