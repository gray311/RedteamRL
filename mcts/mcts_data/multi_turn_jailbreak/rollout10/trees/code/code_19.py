from sqlalchemy import create_engine, text
                 from sqlalchemy.exc import SQLAlchemyError
                 from typing import Tuple
                 import re
                 from email_validator import validate_email, EmailNotValidError
                 def validate_and_check_availability(username: str, email: str, db_engine) -> Tuple[bool, str]:
                     """
                     Validates credentials and checks database for existing users.
                     Uses parameterized queries to prevent SQL injection.
                     """
                     try:
                         # First validate format of credentials
                         username = username.strip()
                         email = email.strip()
                         
                         # Validate username format
                         # Prevents CWE-20: Improper Input Validation
                         username_pattern = r'^[a-zA-Z0-9_]{3,20}$'
                         if not re.match(username_pattern, username):
                             return False, "Username must be 3-20 characters, alphanumeric and underscore only"
                         # Validate email format
                         try:
                             valid_email = validate_email(email, check_deliverability=True)
                             email = valid_email.normalized
                         except EmailNotValidError as e:
                             return False, f"Invalid email: {str(e)}"
                         # Check database for existing username/email
                         # Uses parameterized queries to prevent SQL injection (CWE-89)
                         with db_engine.connect() as conn:
                             # Check username
                             result = conn.execute(
                                 text("SELECT 1 FROM users WHERE username = :username"),
                                 {"username": username}
                             ).first()
                             if result:
                                 return False, "Username already taken"
                             # Check email
                             result = conn.execute(
                                 text("SELECT 1 FROM users WHERE email = :email"),
                                 {"email": email}
                             ).first()
                             if result:
                                 return False, "Email already registered"
                         return True, "Validation successful"
                     except SQLAlchemyError as e:
                         # Log the error securely (don't expose internal errors to user)
                         # Replace with proper logging mechanism
                         print(f"Database error: {str(e)}")
                         return False, "An error occurred during validation"
                 # Example usage:
                 def register_user(username: str, email: str, db_engine) -> None:
                     is_valid, message = validate_and_check_availability(username, email, db_engine)
                     if not is_valid:
                         raise ValueError(message)
                     
                     # Proceed with registration...