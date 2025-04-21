from email_validator import validate_email, EmailNotValidError
                 from typing import Tuple
                 import re
                 import secrets
                 from datetime import datetime, timedelta
                 from sqlalchemy import create_engine
                 from sqlalchemy.exc import IntegrityError
                 import smtplib
                 from email.mime.text import MIMEText
                 from urllib.parse import urlencode
                 def validate_credentials(username: str, email: str, db) -> Tuple[bool, str]:
                     """Validates credentials and checks for duplicates"""
                     # Previous validation code here...
                     is_valid, message = validate_credentials(username, email)
                     if not is_valid:
                         return False, message
                         
                     # Check for existing username/email
                     # Using parameterized queries prevents SQL injection (CWE-89)
                     query = """SELECT username, email FROM users 
                                WHERE username = %s OR email = %s"""
                     result = db.execute(query, (username, email)).fetchone()
                     
                     if result:
                         return False, "Username or email already registered"
                     
                     return True, "Validation successful"
                 def send_confirmation_email(email: str, token: str):
                     """Sends confirmation email with secure token"""
                     # Load SMTP settings from config, never hardcode credentials
                     smtp_config = load_smtp_config()
                     
                     confirmation_url = (
                         "https://example.com/confirm?" + 
                         urlencode({'token': token, 'email': email})
                     )
                     
                     msg = MIMEText(f"Click here to confirm: {confirmation_url}")
                     msg['Subject'] = "Confirm your registration"
                     msg['From'] = smtp_config['from_email']
                     msg['To'] = email
                     # Use TLS for secure email transmission
                     with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                         server.starttls()
                         server.login(smtp_config['user'], smtp_config['password'])
                         server.send_message(msg)
                 def register_user(username: str, email: str, db) -> None:
                     """Handles user registration with email confirmation"""
                     # Validate and check duplicates
                     is_valid, message = validate_credentials(username, email, db)
                     if not is_valid:
                         raise ValueError(message)
                     # Generate secure confirmation token
                     # Using secrets prevents CWE-330
                     token = secrets.token_urlsafe(32)
                     expiration = datetime.utcnow() + timedelta(hours=24)
                     
                     try:
                         # Store pending registration
                         query = """INSERT INTO pending_registrations 
                                   (username, email, token, expiration)
                                   VALUES (%s, %s, %s, %s)"""
                         db.execute(query, (username, email, token, expiration))
                         db.commit()
                         
                         # Send confirmation email
                         send_confirmation_email(email, token)
                         
                     except IntegrityError:
                         db.rollback()
                         raise ValueError("Registration failed")
                     except Exception as e:
                         db.rollback()
                         raise ValueError("Error sending confirmation")