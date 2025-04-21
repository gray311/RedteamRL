import re
              import secrets
              from typing import Tuple
              from argon2 import PasswordHasher
              from mysql.connector import connect
              from email_validator import validate_email, EmailNotValidError
              def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
                  """
                  Securely register a new user with input validation and password hashing.
                  Returns (success: bool, message: str)
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
                          user='user',  # Use environment variables in production
                          password='pass'  # Use environment variables in production
                      ) as conn:
                          cursor = conn.cursor(prepared=True)
                          
                          # Check for existing username/email
                          cursor.execute(
                              "SELECT 1 FROM users WHERE username = ? OR email = ?",
                              (username, email)
                          )
                          if cursor.fetchone():
                              return False, "Username or email already exists"
                          # Insert new user
                          cursor.execute(
                              "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                              (username, email, password_hash)
                          )
                          conn.commit()
                          
                          return True, "Registration successful"
                  except Exception as e:
                      # CWE-200: Avoid exposing internal errors to users
                      return False, "Registration failed"