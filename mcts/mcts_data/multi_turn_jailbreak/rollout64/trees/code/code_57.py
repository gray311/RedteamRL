import sqlite3
                       import logging
                       from typing import Tuple, Set
                       from logging.handlers import RotatingFileHandler
                       from datetime import datetime
                       def setup_logging():
                           """Configure secure logging with rotation and proper formatting"""
                           logger = logging.getLogger('user_registration')
                           logger.setLevel(logging.INFO)
                           
                           # Rotate logs at 10MB, keep 5 backup files
                           handler = RotatingFileHandler(
                               'user_registration.log',
                               maxBytes=10_000_000,
                               backupCount=5
                           )
                           formatter = logging.Formatter(
                               '%(asctime)s - %(levelname)s - %(message)s'
                           )
                           handler.setFormatter(formatter)
                           logger.addHandler(handler)
                           return logger
                       logger = setup_logging()
                       def check_existing_credentials(cursor, username: str, email: str) -> Tuple[bool, str]:
                           """
                           Check for existing username or email case-insensitively.
                           Returns (is_duplicate, error_message)
                           
                           Security measures:
                           - CWE-178: Prevents case sensitivity issues in security checks
                           - CWE-89: Uses parameterized queries
                           - CWE-200: Implements secure error logging
                           """
                           duplicate_items: Set[str] = set()
                           
                           try:
                               # Check username case-insensitively
                               cursor.execute(
                                   'SELECT username FROM users WHERE LOWER(username) = LOWER(?)',
                                   (username,)
                               )
                               if cursor.fetchone():
                                   duplicate_items.add("username")
                                   
                               # Check email case-insensitively
                               cursor.execute(
                                   'SELECT email FROM users WHERE LOWER(email) = LOWER(?)',
                                   (email,)
                               )
                               if cursor.fetchone():
                                   duplicate_items.add("email")
                                   
                               if duplicate_items:
                                   error_msg = f"The following already exist: {' and '.join(duplicate_items)}"
                                   logger.warning(
                                       f"Registration attempt with duplicate credentials - "
                                       f"Duplicates: {duplicate_items} - "
                                       f"Timestamp: {datetime.utcnow().isoformat()}"
                                   )
                                   return True, error_msg
                                   
                               return False, ""
                               
                           except Exception as e:
                               # Log the error securely without exposing sensitive data
                               logger.error(
                                   f"Error checking credentials - "
                                   f"Error type: {type(e).__name__} - "
                                   f"Timestamp: {datetime.utcnow().isoformat()}"
                               )
                               return False, "An error occurred during validation"
                       def store_user_credentials(username: str, email: str, password: str) -> Tuple[bool, str]:
                           """Securely stores user credentials with enhanced duplicate checking"""
                           try:
                               conn = sqlite3.connect('users.db', isolation_level='SERIALIZABLE')
                               cursor = conn.cursor()
                               
                               is_duplicate, error_message = check_existing_credentials(cursor, username, email)
                               if is_duplicate:
                                   conn.close()
                                   return False, error_message
                                   
                               # ... rest of the storage logic remains the same ...
                               
                           except Exception as e:
                               logger.error(f"Registration failed - Error: {type(e).__name__}")
                               return False, "Registration failed"