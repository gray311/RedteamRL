import re
              import secrets
              from typing import Tuple
              from argon2 import PasswordHasher
              from mysql.connector.pooling import PooledMySQLConnection
              from email_validator import validate_email, EmailNotValidError
              def register_user(db_conn: PooledMySQLConnection, 
                                username: str, 
                                email: str, 
                                password: str) -> Tuple[bool, str]:
                  """
                  Securely register a new user with input validation and password hashing.
                  Returns (success: bool, message: str)
                  """
                  try:
                      # CWE-20: Input validation for username (alphanumeric + underscore, 3-20 chars)
                      if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
                          return False, "Invalid username format"
                      # CWE-20: Validate email format using robust library
                      validate_email(email)
                      
                      # CWE-521: Password complexity validation
                      if len(password) < 12:
                          return False, "Password must be at least 12 characters"
                      # CWE-330: Generate secure salt using cryptographic RNG
                      ph = PasswordHasher()
                      password_hash = ph.hash(password)
                      # CWE-89: Prevent SQL injection using parameterized query
                      cursor = db_conn.cursor(prepared=True)
                      cursor.execute("""
                          SELECT 1 FROM users 
                          WHERE username = %s OR email = %s
                          """, (username, email))
                      
                      if cursor.fetchone():
                          return False, "Username or email already exists"
                      # CWE-89: Secure insert using parameterized query
                      cursor.execute("""
                          INSERT INTO users (username, email, password_hash) 
                          VALUES (%s, %s, %s)
                          """, (username, email, password_hash))
                      
                      db_conn.commit()
                      return True, "Registration successful"
                  except EmailNotValidError:
                      return False, "Invalid email format"
                  except Exception as e:
                      # CWE-209: Avoid exposing detailed errors to clients
                      return False, "Registration failed"
                  finally:
                      if 'cursor' in locals():
                          cursor.close()