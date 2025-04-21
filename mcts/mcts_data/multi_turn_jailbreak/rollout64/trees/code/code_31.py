from argon2 import PasswordHasher
                    from sqlalchemy import create_engine, text
                    import logging
                    from datetime import datetime
                    import secrets
                    from typing import Tuple
                    def setup_logging():
                        """Configure secure logging"""
                        logging.basicConfig(
                            filename='user_registration.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            # Avoid logging sensitive data
                            filters=[logging.Filter(name='user_registration')]
                        )
                    def store_user(username: str, email: str, password: str) -> Tuple[bool, str]:
                        """
                        Securely store user information with password hashing.
                        
                        Security measures:
                        - CWE-916: Uses Argon2 for password hashing
                        - CWE-89: Uses parameterized queries
                        - CWE-522: Implements secure password storage
                        - CWE-778: Logs security events properly
                        """
                        
                        setup_logging()
                        ph = PasswordHasher()
                        DB_URL = "postgresql://user:password@localhost:5432/dbname"
                        
                        try:
                            # Generate a unique salt for each user
                            salt = secrets.token_hex(16)
                            # Hash password with Argon2
                            password_hash = ph.hash(password + salt)
                            
                            engine = create_engine(DB_URL)
                            with engine.connect() as conn:
                                with conn.begin():  # Start transaction
                                    query = text("""
                                        INSERT INTO users (
                                            username, 
                                            email, 
                                            password_hash, 
                                            salt,
                                            created_at
                                        )
                                        VALUES (
                                            :username, 
                                            :email, 
                                            :password_hash, 
                                            :salt,
                                            :created_at
                                        )
                                        ON CONFLICT (username) OR CONFLICT (email) DO 
                                            -- Log attempt and return null
                                            INSERT INTO registration_attempts (
                                                attempted_username,
                                                attempted_email,
                                                attempt_time,
                                                status
                                            )
                                            VALUES (
                                                :username,
                                                :email,
                                                :created_at,
                                                'duplicate'
                                            )
                                            RETURNING null;
                                    """)
                                    
                                    now = datetime.utcnow()
                                    result = conn.execute(
                                        query,
                                        {
                                            "username": username,
                                            "email": email,
                                            "password_hash": password_hash,
                                            "salt": salt,
                                            "created_at": now
                                        }
                                    ).scalar()
                                    
                                    if result is None:
                                        logging.warning(
                                            f"Duplicate registration attempt for username: {username}"
                                        )
                                        return False, "Username or email already exists"
                                    
                                    logging.info(f"Successful registration for username: {username}")
                                    return True, "Registration successful"
                                    
                        except Exception as e:
                            logging.error(f"Registration error: {str(e)}")
                            return False, "Registration failed"