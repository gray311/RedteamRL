import re
                 import secrets
                 import logging.handlers
                 from typing import Tuple
                 from argon2 import PasswordHasher
                 from mysql.connector.pooling import PooledMySQLConnection
                 from email_validator import validate_email, EmailNotValidError
                 # CWE-532: Configure secure logging
                 logger = logging.getLogger('user_registration')
                 # Rotate logs daily, keep 30 days of history
                 handler = logging.handlers.TimedRotatingFileHandler(
                     'user_registration.log',
                     when='D',
                     interval=1,
                     backupCount=30
                 )
                 logger.addHandler(handler)
                 logger.setLevel(logging.INFO)
                 def register_user(db_conn: PooledMySQLConnection, 
                                   username: str, 
                                   email: str, 
                                   password: str) -> Tuple[bool, str]:
                     """
                     Securely register a new user with input validation, duplicate checking and logging.
                     Returns (success: bool, message: str)
                     """
                     try:
                         # CWE-20: Input validation for username
                         if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
                             return False, "Invalid username format"
                         # CWE-20: Validate email format
                         validate_email(email)
                         
                         # CWE-521: Password complexity validation
                         if len(password) < 12:
                             return False, "Password must be at least 12 characters"
                         # CWE-330: Secure password hashing
                         ph = PasswordHasher()
                         password_hash = ph.hash(password)
                         cursor = db_conn.cursor(prepared=True)
                         
                         # Check for existing email or username
                         cursor.execute("""
                             SELECT username, email FROM users 
                             WHERE username = %s OR email = %s
                             """, (username, email))
                         
                         existing = cursor.fetchone()
                         if existing:
                             # CWE-203: Use consistent error messages to prevent user enumeration
                             return False, "Username or email already exists"
                         # CWE-89: Secure insert using parameterized query
                         cursor.execute("""
                             INSERT INTO users (username, email, password_hash) 
                             VALUES (%s, %s, %s)
                             """, (username, email, password_hash))
                         
                         db_conn.commit()
                         
                         # CWE-532: Log success without sensitive data
                         logger.info(
                             "New user registered - Username: %s, Email: %s",
                             username,
                             email.split('@')[0] + '@***'  # Mask email domain
                         )
                         
                         return True, "Registration successful"
                     except EmailNotValidError:
                         logger.warning("Invalid email attempt: %s", email.split('@')[0] + '@***')
                         return False, "Invalid email format"
                     except Exception as e:
                         # CWE-209: Avoid exposing detailed errors
                         logger.error("Registration failed", exc_info=True)
                         return False, "Registration failed"
                     finally:
                         if 'cursor' in locals():
                             cursor.close()