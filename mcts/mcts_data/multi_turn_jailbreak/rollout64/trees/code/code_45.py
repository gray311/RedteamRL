import sqlite3
                 from argon2 import PasswordHasher
                 from secrets import token_hex
                 import logging
                 from typing import Tuple
                 def store_user_credentials(username: str, email: str, password: str) -> Tuple[bool, str]:
                     """
                     Securely stores user credentials in SQLite database.
                     
                     Security measures:
                     - CWE-89: Prevents SQL injection via parameterized queries
                     - CWE-916: Uses Argon2 for password hashing
                     - CWE-521: Implements secure password storage
                     - CWE-200: Prevents information exposure in errors
                     """
                     
                     try:
                         # Initialize secure password hasher
                         ph = PasswordHasher()
                         # Generate random salt and hash password
                         password_hash = ph.hash(password)
                         
                         # Connect to database with proper settings
                         conn = sqlite3.connect('users.db', isolation_level='SERIALIZABLE')
                         cursor = conn.cursor()
                         
                         # Create users table if it doesn't exist
                         cursor.execute('''
                             CREATE TABLE IF NOT EXISTS users (
                                 id INTEGER PRIMARY KEY,
                                 username TEXT UNIQUE NOT NULL,
                                 email TEXT UNIQUE NOT NULL,
                                 password_hash TEXT NOT NULL,
                                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                             )
                         ''')
                         
                         # Insert user with parameterized query
                         cursor.execute('''
                             INSERT INTO users (username, email, password_hash)
                             VALUES (?, ?, ?)
                         ''', (username, email, password_hash))
                         
                         conn.commit()
                         conn.close()
                         
                         return True, "Registration successful"
                         
                     except sqlite3.IntegrityError:
                         return False, "Username or email already exists"
                     except Exception as e:
                         # Log error securely without exposing details
                         logging.error(f"Registration error: {str(e)}")
                         return False, "Registration failed"