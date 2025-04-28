import json
import os
import hashlib
from pathlib import Path
import uuid
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users_file = Path("data/users.json")
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_users()

    def _load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
            self._save_users()

    def _save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password, email):
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            "password": self.hash_password(password),
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        self._save_users()
        return True, "User created successfully"

    def verify_user(self, username, password):
        if username not in self.users:
            return False, "Username not found"
        
        if self.users[username]["password"] != self.hash_password(password):
            return False, "Invalid password"
        
        return True, "Login successful"

    def get_user_email(self, username):
        return self.users.get(username, {}).get("email") 