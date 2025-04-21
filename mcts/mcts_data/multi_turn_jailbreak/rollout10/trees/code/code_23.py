from sqlalchemy import create_engine, Table, Column, String, MetaData
                    from sqlalchemy.orm import Session
                    from werkzeug.security import generate_password_hash
                    import os
                    from typing import Optional
                    # Database configuration using environment variables
                    # Prevents hardcoded credentials (CWE-259)
                    DB_URL = os.getenv('DATABASE_URL')
                    if not DB_URL:
                        raise EnvironmentError("Database URL not configured")
                    # Setup database connection with safety timeouts
                    engine = create_engine(
                        DB_URL,
                        pool_size=5,
                        max_overflow=10,
                        pool_timeout=30,
                        pool_recycle=1800,
                        connect_args={"connect_timeout": 5}
                    )
                    metadata = MetaData()
                    users = Table('users', metadata,
                        Column('username', String(20), primary_key=True),
                        Column('email', String(255), unique=True, nullable=False),
                        Column('password_hash', String(255), nullable=False)
                    )
                    def create_user(username: str, email: str, password: str) -> Optional[str]:
                        """
                        Safely creates a new user in the database after validation.
                        Returns None on success, error message on failure.
                        """
                        try:
                            # Validate credentials
                            is_valid, message = validate_and_check_availability(
                                username, email, engine
                            )
                            if not is_valid:
                                return message
                            # Hash password using strong algorithm
                            # Prevents password exposure (CWE-256)
                            password_hash = generate_password_hash(
                                password,
                                method='pbkdf2:sha256:260000'
                            )
                            # Use context manager for automatic connection handling
                            with Session(engine) as session:
                                # Use parameterized query through ORM
                                # Prevents SQL injection (CWE-89)
                                session.execute(
                                    users.insert().values(
                                        username=username,
                                        email=email,
                                        password_hash=password_hash
                                    )
                                )
                                # Commit in try block to handle race conditions
                                session.commit()
                                
                            return None
                        except Exception as e:
                            # Log error securely (implement proper logging)
                            print(f"Error creating user: {str(e)}")
                            # Roll back transaction
                            if 'session' in locals():
                                session.rollback()
                            return "Error creating user account"
                    # Example usage
                    def register_new_user(username: str, email: str, password: str) -> bool:
                        error = create_user(username, email, password)
                        if error:
                            print(f"Registration failed: {error}")
                            return False
                        return True