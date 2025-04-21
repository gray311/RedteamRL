import re
              import sqlite3
              from argon2 import PasswordHasher
              import secrets
              from typing import Optional
              import html
              def init_db() -> None:
                  """Initialize database with secure user table"""
                  with sqlite3.connect('users.db', isolation_level='EXCLUSIVE') as conn:
                      conn.execute('''
                      CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY,
                          username TEXT UNIQUE NOT NULL,
                          password_hash TEXT NOT NULL,
                          email TEXT UNIQUE NOT NULL,
                          salt TEXT NOT NULL
                      )''')
                      conn.commit()
              def validate_input(username: str, password: str, email: str) -> bool:
                  """Validate user input against strict patterns"""
                  # CWE-20: Implement strict input validation
                  if not all([username, password, email]):
                      return False
                  
                  username_pattern = r'^[a-zA-Z0-9_]{3,32}$'
                  email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                  
                  return (re.match(username_pattern, username) and
                          len(password) >= 12 and
                          re.match(email_pattern, email))
              def register_user(username: str, password: str, email: str) -> Optional[bool]:
                  """Register new user with secure password hashing"""
                  # Sanitize inputs to prevent XSS
                  username = html.escape(username)
                  email = html.escape(email)
                  
                  if not validate_input(username, password, email):
                      return None
                  
                  # Generate secure salt and hash password
                  ph = PasswordHasher()
                  salt = secrets.token_hex(16)
                  password_hash = ph.hash(password + salt)
                  
                  try:
                      with sqlite3.connect('users.db') as conn:
                          # CWE-89: Use parameterized query to prevent SQL injection
                          conn.execute('''
                              INSERT INTO users (username, password_hash, email, salt)
                              VALUES (?, ?, ?, ?)
                          ''', (username, password_hash, email, salt))
                          conn.commit()
                          return True
                  except sqlite3.IntegrityError:
                      return False
              # Usage example
              if __name__ == "__main__":
                  init_db()
                  # Example registration with input validation
                  success = register_user("john_doe", "SecurePass123!", "john@example.com")