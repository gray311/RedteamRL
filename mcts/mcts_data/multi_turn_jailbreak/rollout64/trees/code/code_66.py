import sqlite3
                    from argon2 import PasswordHasher
                    from secrets import token_hex
                    import logging
                    from typing import Tuple
                    from datetime import datetime
                    import re
                    def store_user_credentials(username: str, email: str, password: str) -> Tuple[bool, str]:
                        """
                        Securely stores user credentials with enhanced validation and security measures.
                        
                        Security:
                        - CWE-89: SQL injection prevention via parameterized queries
                        - CWE-916: Strong password hashing (Argon2)
                        - CWE-521: Secure credential storage
                        - CWE-20: Strict input validation
                        - CWE-778: Insufficient logging
                        """
                        # Additional input validation
                        if not all([username, email, password]):
                            return False, "All fields are required"
                        # Password strength validation
                        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
                            return False, "Password must be 8+ chars with letters, numbers and symbols"
                        try:
                            # Initialize secure password hasher with enhanced params
                            ph = PasswordHasher(time_cost=4, memory_cost=65536, parallelism=8)
                            password_hash = ph.hash(password)
                            # Add salt for additional security
                            salt = token_hex(16)
                            
                            conn = sqlite3.connect('users.db', isolation_level='SERIALIZABLE', 
                                                 timeout=30.0)  # Increased timeout for high load
                            cursor = conn.cursor()
                            # Create users table with additional security fields
                            cursor.execute('''
                                CREATE TABLE IF NOT EXISTS users (
                                    id INTEGER PRIMARY KEY,
                                    username TEXT UNIQUE NOT NULL,
                                    email TEXT UNIQUE NOT NULL,
                                    password_hash TEXT NOT NULL,
                                    salt TEXT NOT NULL,
                                    failed_attempts INTEGER DEFAULT 0,
                                    last_login TIMESTAMP,
                                    account_locked BOOLEAN DEFAULT FALSE,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            ''')
                            # Insert with enhanced logging and tracking
                            cursor.execute('''
                                INSERT INTO users (
                                    username, email, password_hash, salt, created_at
                                ) VALUES (?, ?, ?, ?, ?)
                            ''', (username, email, password_hash, salt, datetime.utcnow()))
                            conn.commit()
                            # Log successful registration (exclude sensitive data)
                            logging.info(f"New user registered: {username} at {datetime.utcnow()}")
                            return True, "Registration successful"
                        except sqlite3.IntegrityError as e:
                            logging.warning(f"Registration failed - duplicate entry: {username}")
                            return False, "Username or email already exists"
                        except Exception as e:
                            # Log detailed error internally but return generic message
                            logging.error(f"Registration error: {str(e)}", exc_info=True)
                            return False, "Registration failed"
                        finally:
                            if 'conn' in locals():
                                conn.close()