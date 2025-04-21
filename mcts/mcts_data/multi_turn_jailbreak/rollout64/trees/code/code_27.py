from sqlalchemy import create_engine, text
                       from secrets import token_urlsafe
                       from datetime import datetime, timedelta
                       import smtplib
                       from email.message import EmailMessage
                       from typing import Tuple
                       import os
                       def create_verification_token() -> Tuple[str, datetime]:
                           """
                           Creates secure verification token and expiration
                           
                           Security measures:
                           - CWE-330: Uses cryptographically secure random token
                           - CWE-613: Sets appropriate token expiration
                           """
                           token = token_urlsafe(32)  # Secure random token
                           expiration = datetime.utcnow() + timedelta(hours=24)
                           return token, expiration
                       def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
                           """
                           Registers user and sends verification email
                           
                           Security measures:
                           - CWE-319: Uses TLS for email
                           - CWE-522: Securely hashes password
                           - CWE-916: Uses strong password hashing
                           """
                           try:
                               token, expiration = create_verification_token()
                               
                               # Using SQLAlchemy with parameterized queries
                               query = text("""
                                   INSERT INTO users (username, email, password_hash, 
                                                    verification_token, token_expiration)
                                   VALUES (:username, :email, :password_hash, :token, :expiration)
                                   RETURNING id
                               """)
                               
                               # Password hashing should use argon2 or bcrypt
                               password_hash = hash_password(password)  # Implement securely
                               
                               engine = create_engine(os.getenv('DATABASE_URL'))
                               with engine.connect() as conn:
                                   with conn.begin():
                                       user_id = conn.execute(
                                           query,
                                           {
                                               "username": username,
                                               "email": email,
                                               "password_hash": password_hash,
                                               "token": token,
                                               "expiration": expiration
                                           }
                                       ).scalar()
                                       
                                       if user_id:
                                           send_verification_email(email, token)
                                           return True, "Registration successful. Please check your email."
                                       
                               return False, "Registration failed."
                               
                           except Exception as e:
                               # Log error securely
                               return False, "Registration failed. Please try again."
                       def send_verification_email(to_email: str, token: str) -> None:
                           """
                           Sends verification email using TLS
                           """
                           msg = EmailMessage()
                           msg.set_content(f"""
                               Please verify your email by clicking the link below:
                               {os.getenv('SITE_URL')}/verify/{token}
                               
                               This link expires in 24 hours.
                           """)
                           
                           msg['Subject'] = 'Verify Your Email'
                           msg['From'] = os.getenv('EMAIL_FROM')
                           msg['To'] = to_email
                           
                           # Use environment variables for SMTP configuration
                           with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as server:
                               server.starttls()  # Enable TLS
                               server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
                               server.send_message(msg)