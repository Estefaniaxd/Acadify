# backend/app/utils/actions.py
from datetime import datetime

def sanitize_email(email: str) -> str:
    """Normaliza un email: quita espacios y pasa a minúsculas"""
    return email.strip().lower() if email else email

def log_action(user_id: str, action: str):
    """Log simple de acciones de usuarios"""
    print(f"[{datetime.utcnow()}] User {user_id}: {action}")
