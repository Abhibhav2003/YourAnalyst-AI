import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import time
from pathlib import Path
import json
import os
from dotenv import load_dotenv

load_dotenv()

class PasswordRecovery:
    def __init__(self):
        self.tokens_file = Path("data/recovery_tokens.json")
        self.tokens_file.parent.mkdir(parents=True, exist_ok=True)
        self.tokens = self._load_tokens()
        self.token_expiry = 3600  # 1 hour in seconds
        
        # Load email configuration from environment variables
        self.sender_email = os.getenv('EMAIL_ADDRESS')
        self.sender_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))

    def _load_tokens(self):
        if self.tokens_file.exists():
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_tokens(self):
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=4)

    def generate_token(self, email):
        # Clean up expired tokens first
        self._cleanup_expired_tokens()
        
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            'email': email,
            'timestamp': time.time()
        }
        self._save_tokens()
        return token

    def verify_token(self, token):
        if token not in self.tokens:
            return False, "Invalid or expired token"
        
        token_data = self.tokens[token]
        if time.time() - token_data['timestamp'] > self.token_expiry:
            del self.tokens[token]
            self._save_tokens()
            return False, "Token has expired"
        
        return True, token_data['email']

    def _cleanup_expired_tokens(self):
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.tokens.items()
            if current_time - data['timestamp'] > self.token_expiry
        ]
        for token in expired_tokens:
            del self.tokens[token]
        if expired_tokens:
            self._save_tokens()

    def send_recovery_email(self, email, token):
        if not all([self.sender_email, self.sender_password]):
            return False, "Email configuration not set. Please check environment variables."
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = email
            msg['Subject'] = "Password Recovery"
            
            # You should replace this with your actual domain
            recovery_link = f"http://localhost:8501/reset-password?token={token}"
            body = f"""
            Hello,
            
            You have requested to reset your password. Click the link below to reset it:
            
            {recovery_link}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            Your Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True, "Recovery email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send recovery email: {str(e)}" 