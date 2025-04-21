import sqlite3
                    from argon2 import PasswordHasher
                    import logging
                    from typing import Tuple
                    def check_existing_credentials(cursor, username: str, email: str) -> Tuple[bool, str]:
                        """
                        Check for existing username or email in database.
                        Returns (is_duplicate, error_message)
                        """
                        # Check username
                        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
                        if cursor.fetchone():
                            return True, "Username already exists"
                        
                        # Check email
                        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
                        if cursor.fetchone():
                            return True, "Email address already registered"
                        
                        return False, ""
                    def store_user_credentials(username: str, email: str, password: str) -> Tuple[bool, str]:
                        """
                        Securely stores user credentials with duplicate checking.
                        
                        Security measures:
                        - CWE-89: Prevents SQL injection via parameterized queries
                        - CWE-916: Uses Argon2 for password hashing
                        - CWE-521: Implements secure password storage
                        - CWE-200: Prevents information exposure in errors
                        """
                        try:
                            conn = sqlite3.connect('users.db', isolation_level='SERIALIZABLE')
                            cursor = conn.cursor()
                            
                            # Check for duplicates
                            is_duplicate, error_message = check_existing_credentials(cursor, username, email)
                            if is_duplicate:
                                conn.close()
                                return False, error_message
                            
                            # Hash password and store user
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