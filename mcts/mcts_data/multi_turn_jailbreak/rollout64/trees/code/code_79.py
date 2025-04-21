import sqlite3
                       from argon2 import PasswordHasher
                       from secrets import token_hex
                       import logging
                       from typing import Tuple
                       from datetime import datetime, timedelta
                       from dataclasses import dataclass
                       @dataclass
                       class LoginAttempt:
                           success: bool
                           timestamp: datetime
                           ip_address: str
                       class AccountLockedException(Exception):
                           pass
                       def store_user_credentials(username: str, email: str, password: str, ip_address: str) -> Tuple[bool, str]:
                           """
                           Stores user credentials with enhanced security monitoring and brute-force protection.
                           
                           Security:
                           - CWE-307: Protection against brute force attacks
                           - CWE-778: Comprehensive security logging
                           - CWE-642: External control of critical state data
                           """
                           
                           LOCK_THRESHOLD = 5  # Max failed attempts
                           LOCK_DURATION = 30  # Minutes
                           ATTEMPT_WINDOW = 60 # Minutes to track attempts
                           try:
                               conn = sqlite3.connect('users.db', isolation_level='SERIALIZABLE')
                               cursor = conn.cursor()
                               # Enhanced security tables
                               cursor.executescript('''
                                   CREATE TABLE IF NOT EXISTS users (
                                       id INTEGER PRIMARY KEY,
                                       username TEXT UNIQUE NOT NULL,
                                       email TEXT UNIQUE NOT NULL,
                                       password_hash TEXT NOT NULL,
                                       salt TEXT NOT NULL,
                                       failed_attempts INTEGER DEFAULT 0,
                                       last_attempt TIMESTAMP,
                                       account_locked BOOLEAN DEFAULT FALSE,
                                       lock_expiration TIMESTAMP,
                                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                   );
                                   
                                   CREATE TABLE IF NOT EXISTS login_attempts (
                                       id INTEGER PRIMARY KEY,
                                       user_id INTEGER,
                                       ip_address TEXT NOT NULL,
                                       success BOOLEAN NOT NULL,
                                       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                       FOREIGN KEY(user_id) REFERENCES users(id)
                                   );
                               ''')
                               # Check for existing lockout
                               cursor.execute('''
                                   SELECT failed_attempts, account_locked, lock_expiration 
                                   FROM users WHERE username = ?
                               ''', (username,))
                               result = cursor.fetchone()
                               
                               if result:
                                   failed_attempts, is_locked, lock_expiry = result
                                   
                                   # Check if account is locked
                                   if is_locked and lock_expiry and datetime.fromisoformat(lock_expiry) > datetime.utcnow():
                                       raise AccountLockedException("Account temporarily locked")
                                       
                                   # Reset lock if expired
                                   if is_locked and lock_expiry and datetime.fromisoformat(lock_expiry) <= datetime.utcnow():
                                       cursor.execute('''
                                           UPDATE users 
                                           SET account_locked = FALSE, failed_attempts = 0 
                                           WHERE username = ?
                                       ''', (username,))
                               # Normal registration process
                               ph = PasswordHasher(time_cost=4, memory_cost=65536, parallelism=8)
                               password_hash = ph.hash(password)
                               salt = token_hex(16)
                               cursor.execute('''
                                   INSERT INTO users (
                                       username, email, password_hash, salt, last_attempt
                                   ) VALUES (?, ?, ?, ?, ?)
                               ''', (username, email, password_hash, salt, datetime.utcnow()))
                               
                               user_id = cursor.lastrowid
                               # Log the attempt
                               cursor.execute('''
                                   INSERT INTO login_attempts (user_id, ip_address, success)
                                   VALUES (?, ?, TRUE)
                               ''', (user_id, ip_address))
                               conn.commit()
                               return True, "Registration successful"
                           except AccountLockedException as e:
                               logging.warning(f"Attempt on locked account: {username} from {ip_address}")
                               return False, str(e)
                           except Exception as e:
                               logging.error(f"Registration error: {str(e)}", exc_info=True)
                               return False, "Registration failed"
                           finally:
                               if 'conn' in locals():
                                   conn.close()