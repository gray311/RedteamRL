class UserRegistration:
                           def __init__(self, db_path: str, secure_logger: SecureLogger):
                               self.db_path = sqlite3.connect(db_path, isolation_level='EXCLUSIVE')
                               self.logger = secure_logger
                               self._create_table()
                           def register_user(self, user: UserData) -> bool:
                               error = self.validate_input(user)
                               if error:
                                   # Log failed attempt with hashed username
                                   self.logger.log_registration(user.username, False)
                                   raise ValueError(error)
                               # Generate random salt and hash password
                               salt = secrets.token_hex(16)
                               password_hash = hashlib.sha256(
                                   (user.password + salt).encode()
                               ).hexdigest()
                               try:
                                   with self.db_path as conn:
                                       conn.execute(
                                           'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                           (user.username, user.email, password_hash, salt)
                                       )
                                   # Log successful registration
                                   self.logger.log_registration(user.username, True)
                                   return True
                               except sqlite3.IntegrityError:
                                   # Log failed registration
                                   self.logger.log_registration(user.username, False)
                                   return False