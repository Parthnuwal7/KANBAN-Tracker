# Kanban Task Tracker

Acces the App here: <!-- https://x101kanban.streamlit.app/ -->
(Use username = user)

A Kanban-style project management tool built using **Streamlit** and **Google Sheets** as the backend. Designed for collaborative task tracking, with dynamic permissions, voting mechanisms, and an intuitive UI.

## 🔧 Features

- 🧑‍💼 **Roles**
  - **Admin (Parth)**: Full control. Can assign, update, and override.
  - **Editors (Arka, Mohit, Nishtha, Rajat)**: Can create tasks, update their own, and vote.
  - **Viewers**: Read-only access.

- 📋 **Kanban Board**
  - Three stages: **To Be Done**, **In Progress**, **Completed**
  - Tasks move across stages with voting logic.

- ✅ **Voting System**
  - When an editor completes a task, it's up for vote.
  - 4 out of 5 editors must approve within 12 hours.
  - Admin can override votes.
  - Voting progress bar and activity banner included.

- 🕒 **Timestamps and Timezones**
  - All timestamps stored and displayed in **IST**.

- 🔔 **Activity Log**
  - Logs all actions: task creation, status change, vote actions, reassignments, etc.

- 📌 **Task Attributes**
  - Title, description, deadline, priority, assignee, creator, timestamp

## 📁 Tabs Navigation
- **Home (Kanban Board)**: Task board with all 3 stages
- **Add Task**: Form to add new tasks (only for Editors/Admin)
- **Activity Log**: View all actions in one place

## ⚙️ Logic Highlights
- Only the **creator** can mark a task as complete.
- Voting triggers once task is marked complete.
- **Admin** can reassign tasks and override after 12 hours.
- Banner highlights tasks currently under vote.
- Task click scrolls to card on board.

## 🗂️ Tech Stack
- **Frontend**: Streamlit
- **Backend**: Google Sheets (via `gspread` and `pandas`)
- **Timezone Handling**: `pytz`

## 🚀 Setup Instructions

1. Clone the repo
```bash
git clone <repo-link>
cd kanban-tracker
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up Google Sheets credentials in `creds.json`

4. Run the app
```bash
streamlit run app.py
```

## 📌 To Do
- [ ] Add notifications (email/Slack)
- [ ] Archive completed tasks weekly
- [ ] Add filters & search
- [ ] Enable commenting system on tasks

---

Made with ❤️ by Parth & Team
