def register_user(self, user: UserData) -> bool:
                           error = self.validate_input(user)
                           if error:
                               raise ValueError(error)
                           try:
                               with self.db_path as conn:
                                   cursor = conn.execute(
                                       'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                       (user.username, user.email, password_hash, salt)
                                   )
                                   # Log safely with pseudonymized data
                                   self._log_registration_event(
                                       user_id=cursor.lastrowid,
                                       email_domain=user.email.split('@')[1],
                                       timestamp=datetime.utcnow().isoformat()
                                   )
                               return True
                           except sqlite3.IntegrityError:
                               return False