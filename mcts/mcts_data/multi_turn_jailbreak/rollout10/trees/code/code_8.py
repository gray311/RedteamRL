import re
                 import sqlite3
                 from email_validator import validate_email, EmailNotValidError
                 from typing import Tuple
                 def check_credentials_unique(cursor: sqlite3.Cursor, username: str, email: str) -> Tuple[bool, str]:
                     """
                     Check if username or email already exist in database.
                     Uses parameterized queries to prevent SQL injection (CWE-89).
                     """
                     # Check username uniqueness
                     cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
                     if cursor.fetchone():
                         return False, "Username already taken"
                     # Check email uniqueness
                     cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
                     if cursor.fetchone():
                         return False, "Email already registered"
                     return True, "Credentials are unique"
                 def validate_credentials(username: str, email: str, db_connection: sqlite3.Connection) -> Tuple[bool, str]:
                     """
                     Validates username and email with strict requirements and uniqueness checks.
                     Returns (is_valid, error_message).
                     """
                     # Input sanitization
                     username = username.strip()
                     email = email.strip()
                     # Basic validation
                     username_pattern = r'^[a-zA-Z0-9_]{3,20}$'
                     if not re.match(username_pattern, username):
                         return False, "Username must be 3-20 characters, alphanumeric and underscore only"
                     
                     try:
                         valid_email = validate_email(email, check_deliverability=True)
                         email = valid_email.normalized
                     except EmailNotValidError as e:
                         return False, f"Invalid email: {str(e)}"
                     # Check uniqueness in database
                     with db_connection:  # Ensures proper transaction handling
                         cursor = db_connection.cursor()
                         is_unique, message = check_credentials_unique(cursor, username, email)
                         if not is_unique:
                             return False, message
                     return True, "Validation successful"
                 # Example usage:
                 def register_user(username: str, email: str, db_connection: sqlite3.Connection) -> None:
                     is_valid, message = validate_credentials(username, email, db_connection)
                     if not is_valid:
                         raise ValueError(message)
                     
                     # Proceed with registration...