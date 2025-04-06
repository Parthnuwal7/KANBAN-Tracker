import json

# Load from config file
def load_users():
    with open("config/users.json") as f:
        return json.load(f)

def authenticate_user(username):
    users = load_users()
    role = users.get(username)
    if role:
        return role
    return None
