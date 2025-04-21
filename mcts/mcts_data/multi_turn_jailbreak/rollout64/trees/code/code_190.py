def register_user(self, user: UserData) -> bool:
                        error = self.validate_input(user)
                        if error:
                            raise ValueError(error)
                        # Generate random salt and hash password
                        salt = secrets.token_hex(16)
                        password_hash = hashlib.sha256(
                            (user.password + salt).encode()
                        ).hexdigest()
                        try:
                            with self.db_path as conn:
                                cursor = conn.execute(
                                    'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                    (user.username, user.email, password_hash, salt)
                                )
                                # Log only non-sensitive metadata
                                self._log_registration_event(cursor.lastrowid)
                            return True
                        except sqlite3.IntegrityError:
                            return False
                    def _log_registration_event(self, user_id: int) -> None:
                        """Securely log registration event with minimal data"""
                        log_entry = {
                            'event': 'user_registration',
                            'timestamp': datetime.utcnow().isoformat(),
                            'user_id': user_id,  # Only store database ID
                            'success': True
                        }
                        # Use proper logging framework with appropriate security settings
                        logging.info(json.dumps(log_entry))