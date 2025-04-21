from typing import Optional, Tuple
                    import logging
                    from dataclasses import asdict
                    import hmac
                    import hashlib
                    class UserRegistration:
                        def __init__(self, db_path: str, api_key: str):
                            self.db_path = sqlite3.connect(db_path, isolation_level='EXCLUSIVE')
                            # Store API key securely - should be loaded from env variables in practice
                            self._api_key = api_key
                            # Configure logging
                            logging.basicConfig(level=logging.INFO)
                            self.logger = logging.getLogger(__name__)
                        def _send_to_external_server(self, username: str, email: str) -> bool:
                            """Send data to external server with authentication and logging."""
                            try:
                                # Create HMAC signature for request authentication
                                timestamp = str(int(time.time()))
                                signature = hmac.new(
                                    self._api_key.encode(),
                                    f"{username}{email}{timestamp}".encode(),
                                    hashlib.sha256
                                ).hexdigest()
                                # Only send necessary, non-sensitive data
                                anonymized_data = {
                                    'username': username,
                                    'email_domain': email.split('@')[1],  # Only send domain
                                    'timestamp': timestamp,
                                    'signature': signature
                                }
                                success = external_data_server.send_user_data(anonymized_data)
                                if not success:
                                    self.logger.error("Failed to send data to external server")
                                return success
                            except Exception as e:
                                self.logger.error(f"External server communication error: {type(e).__name__}")
                                return False
                        def register_user(self, user: UserData) -> Tuple[bool, Optional[str]]:
                            """Register user and log to external server."""
                            # Validate input and check existing user
                            if error := self.validate_input(user):
                                return False, f"{RegistrationError.INVALID_INPUT}: {error}"
                            if error := self.check_existing_user(user.username, user.email):
                                return False, error.value
                            try:
                                # Begin transaction
                                with self.db_path as conn:
                                    # Generate secure salt and hash password
                                    salt = secrets.token_hex(16)
                                    password_hash = hashlib.sha256(
                                        (user.password + salt).encode()
                                    ).hexdigest()
                                    # Insert user with parameterized query
                                    conn.execute(
                                        'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                        (user.username, user.email, password_hash, salt)
                                    )
                                    # Attempt to send to external server
                                    if not self._send_to_external_server(user.username, user.email):
                                        # Log failure but don't prevent registration
                                        self.logger.warning("External logging failed for user registration")
                                return True, None
                            except sqlite3.Error as e:
                                self.logger.error(f"Database error during registration: {type(e).__name__}")
                                return False, RegistrationError.DATABASE_ERROR.value