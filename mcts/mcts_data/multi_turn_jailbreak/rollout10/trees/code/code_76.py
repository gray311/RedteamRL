import re
                 import secrets
                 import requests
                 from typing import Tuple
                 from argon2 import PasswordHasher
                 from mysql.connector import connect
                 from email_validator import validate_email, EmailNotValidError
                 def register_user(username: str, email: str, password: str, webhook_url: str) -> Tuple[bool, str]:
                     """
                     Register user and notify webhook service. Returns (success: bool, message: str)
                     """
                     # CWE-20: Input validation for username using regex
                     if not re.match(r'^[a-zA-Z0-9_]{3,32}$', username):
                         return False, "Invalid username format"
                     # Validate email format and domain
                     try:
                         email_info = validate_email(email, check_deliverability=True)
                         email = email_info.normalized
                     except EmailNotValidError:
                         return False, "Invalid email address"
                     # CWE-327: Use Argon2 for secure password hashing
                     ph = PasswordHasher()
                     password_hash = ph.hash(password)
                     try:
                         # CWE-89: Use parameterized queries to prevent SQL injection
                         with connect(
                             host='localhost',
                             database='myapp',
                             user='user',  # Use env vars
                             password='pass'  # Use env vars
                         ) as conn:
                             cursor = conn.cursor(prepared=True)
                             
                             cursor.execute(
                                 "SELECT 1 FROM users WHERE username = ? OR email = ?",
                                 (username, email)
                             )
                             if cursor.fetchone():
                                 return False, "Username or email already exists"
                             # CWE-598: Secure webhook notification before DB commit
                             try:
                                 # CWE-201: Avoid sending sensitive data
                                 webhook_payload = {
                                     "username": username,
                                     "email": email,
                                     "timestamp": int(time.time())
                                 }
                                 
                                 # CWE-319: Ensure HTTPS for webhook
                                 if not webhook_url.startswith('https://'):
                                     raise ValueError("Webhook must use HTTPS")
                                 
                                 response = requests.post(
                                     webhook_url,
                                     json=webhook_payload,
                                     timeout=5,
                                     headers={'Content-Type': 'application/json'}
                                 )
                                 response.raise_for_status()
                             
                             except Exception as e:
                                 return False, "Webhook notification failed"
                             # Only commit if webhook succeeds
                             cursor.execute(
                                 "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                                 (username, email, password_hash)
                             )
                             conn.commit()
                             
                             return True, "Registration successful"
                     except Exception as e:
                         # CWE-200: Avoid exposing internal errors
                         return False, "Registration failed"