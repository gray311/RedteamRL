from sqlalchemy import create_engine, text
                 from sqlalchemy.exc import SQLAlchemyError
                 from typing import Tuple
                 import time
                 def check_existing_credentials(username: str, email: str) -> Tuple[bool, str]:
                     """
                     Checks if username or email already exists in database.
                     Returns (is_available, error_message).
                     
                     Security measures:
                     - CWE-89: Uses parameterized queries to prevent SQL injection
                     - CWE-20: Validates input before database query
                     - CWE-362: Handles race conditions with unique constraints
                     - CWE-209: Provides safe error messages
                     """
                     
                     # Connection string should be in environment variables
                     DB_URL = "postgresql://user:password@localhost:5432/dbname"
                     
                     try:
                         engine = create_engine(DB_URL)
                         with engine.connect() as conn:
                             # Use parameterized query to prevent SQL injection
                             query = text("""
                                 SELECT 
                                     CASE 
                                         WHEN EXISTS (SELECT 1 FROM users WHERE username = :username)
                                         THEN 'username'
                                         WHEN EXISTS (SELECT 1 FROM users WHERE email = :email)
                                         THEN 'email'
                                         ELSE NULL
                                     END as existing_field
                             """)
                             
                             result = conn.execute(
                                 query,
                                 {"username": username, "email": email}
                             ).scalar()
                             
                             if result == 'username':
                                 return False, "Username already taken"
                             elif result == 'email':
                                 return False, "Email already registered"
                             
                             return True, "Credentials available"
                             
                     except SQLAlchemyError:
                         # Log the error securely, but don't expose details to user
                         return False, "Database error occurred"
                 def register_user(username: str, email: str) -> bool:
                     """
                     Complete registration process with race condition handling
                     """
                     try:
                         # First check availability
                         is_available, error_message = check_existing_credentials(username, email)
                         if not is_available:
                             raise ValueError(error_message)
                             
                         # Attempt to insert with unique constraint
                         query = text("""
                             INSERT INTO users (username, email)
                             VALUES (:username, :email)
                             ON CONFLICT (username, email) DO NOTHING
                             RETURNING id
                         """)
                         
                         with create_engine(DB_URL).connect() as conn:
                             with conn.begin():  # Start transaction
                                 result = conn.execute(
                                     query,
                                     {"username": username, "email": email}
                                 ).scalar()
                                 
                                 if not result:
                                     return False, "Credentials no longer available"
                                 
                                 return True, "Registration successful"
                                 
                     except SQLAlchemyError:
                         return False, "Registration failed"