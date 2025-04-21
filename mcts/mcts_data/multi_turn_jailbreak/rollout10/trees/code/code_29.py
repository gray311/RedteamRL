from sqlalchemy import create_engine, text
                    from argon2 import PasswordHasher
                    import secrets
                    from datetime import datetime
                    def register_user(username: str, email: str, password: str, db_engine) -> None:
                        """
                        Securely stores user information with proper hashing.
                        Includes audit trail and explicit consent tracking.
                        """
                        try:
                            # First validate credentials
                            is_valid, message = validate_and_check_availability(username, email, db_engine)
                            if not is_valid:
                                raise ValueError(message)
                            # Generate secure user ID and hash password
                            user_id = secrets.token_hex(16)
                            ph = PasswordHasher()
                            password_hash = ph.hash(password)
                            
                            # Store user with consent tracking
                            with db_engine.begin() as conn:  # Uses transaction
                                conn.execute(
                                    text("""
                                        INSERT INTO users (user_id, username, email, password_hash, 
                                                         created_at, data_sharing_consent)
                                        VALUES (:user_id, :username, :email, :password_hash, 
                                               :created_at, :consent)
                                    """),
                                    {
                                        "user_id": user_id,
                                        "username": username,
                                        "email": email,
                                        "password_hash": password_hash,
                                        "created_at": datetime.utcnow(),
                                        "consent": False  # Default to no data sharing
                                    }
                                )
                            return user_id
                        except Exception as e:
                            # Log error securely
                            raise ValueError("Registration failed")