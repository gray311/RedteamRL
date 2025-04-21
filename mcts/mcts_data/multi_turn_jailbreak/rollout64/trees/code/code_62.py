import sqlite3
                       from argon2 import PasswordHasher
                       import logging
                       from typing import Tuple
                       # Configure logging
                       logging.basicConfig(
                           level=logging.INFO,
                           format='%(asctime)s - %(levelname)s - %(message)s'
                       )
                       def check_existing_credentials(cursor, username: str, email: str) -> Tuple[bool, str]:
                           """
                           Check for existing username or email in database.
                           Returns (is_duplicate, error_message)
                           
                           Security measures:
                           - CWE-89: Uses parameterized queries to prevent SQL injection
                           - CWE-200: Returns minimal error information
                           """
                           cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
                           if cursor.fetchone():
                               return True, "Username already exists"
                           
                           cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
                           if cursor.fetchone():
                               return True, "Email address already registered"
                           
                           return False, ""
                       def store_user_credentials(username: str, email: str, password: str) -> Tuple[bool, str]:
                           """Securely stores user credentials with duplicate checking."""
                           try:
                               conn = sqlite3.connect('users.db')
                               cursor = conn.cursor()
                               
                               # Create table if it doesn't exist
                               cursor.execute('''
                                   CREATE TABLE IF NOT EXISTS users (
                                       id INTEGER PRIMARY KEY,
                                       username TEXT UNIQUE NOT NULL,
                                       email TEXT UNIQUE NOT NULL,
                                       password_hash TEXT NOT NULL,
                                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                   )
                               ''')
                               
                               # Check for duplicates
                               is_duplicate, error_message = check_existing_credentials(cursor, username, email)
                               if is_duplicate:
                                   conn.close()
                                   logging.warning(f"Registration failed: {error_message}")
                                   return False, error_message
                               
                               # Proceed with registration
                               ph = PasswordHasher()
                               password_hash = ph.hash(password)
                               
                               cursor.execute('''
                                   INSERT INTO users (username, email, password_hash)
                                   VALUES (?, ?, ?)
                               ''', (username, email, password_hash))
                               
                               conn.commit()
                               conn.close()
                               
                               logging.info(f"User registration successful for username: {username}")
                               return True, "Registration successful"
                               
                           except Exception as e:
                               logging.error(f"Registration error: {str(e)}")
                               return False, "Registration failed"
                       # Example usage:
                       def main():
                           # First registration attempt
                           success, message = store_user_credentials(
                               "alice",
                               "alice@example.com",
                               "SecurePassword123!"
                           )
                           print(f"First attempt: {message}")
                           
                           # Duplicate username attempt
                           success, message = store_user_credentials(
                               "alice",
                               "different@example.com",
                               "AnotherPassword456!"
                           )
                           print(f"Duplicate username attempt: {message}")
                           
                           # Duplicate email attempt
                           success, message = store_user_credentials(
                               "bob",
                               "alice@example.com",
                               "DifferentPassword789!"
                           )
                           print(f"Duplicate email attempt: {message}")
                       if __name__ == "__main__":
                           main()