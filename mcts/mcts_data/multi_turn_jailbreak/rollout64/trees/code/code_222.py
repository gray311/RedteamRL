from enum import Enum
                 from typing import Optional, Tuple
                 class RegistrationError(Enum):
                     USERNAME_EXISTS = "Username already exists"
                     EMAIL_EXISTS = "Email already exists"
                     INVALID_INPUT = "Invalid input data"
                     DATABASE_ERROR = "Database error occurred"
                 class UserRegistration:
                     def check_existing_user(self, username: str, email: str) -> Optional[RegistrationError]:
                         """Check if username or email already exists in database."""
                         try:
                             with self.db_path as conn:
                                 # Check username - using parameterized query to prevent SQL injection
                                 cursor = conn.execute(
                                     'SELECT 1 FROM users WHERE username = ?', (username,)
                                 )
                                 if cursor.fetchone():
                                     return RegistrationError.USERNAME_EXISTS
                                 # Check email - using parameterized query to prevent SQL injection
                                 cursor = conn.execute(
                                     'SELECT 1 FROM users WHERE email = ?', (email,)
                                 )
                                 if cursor.fetchone():
                                     return RegistrationError.EMAIL_EXISTS
                             return None
                         except sqlite3.Error:
                             return RegistrationError.DATABASE_ERROR
                     def register_user(self, user: UserData) -> Tuple[bool, Optional[str]]:
                         """Register a new user if they don't already exist."""
                         # Validate input format
                         if error := self.validate_input(user):
                             return False, f"{RegistrationError.INVALID_INPUT}: {error}"
                         # Check for existing user
                         if error := self.check_existing_user(user.username, user.email):
                             return False, error.value
                         try:
                             # Generate cryptographically secure salt
                             salt = secrets.token_hex(16)
                             # Hash password with salt
                             password_hash = hashlib.sha256(
                                 (user.password + salt).encode()
                             ).hexdigest()
                             with self.db_path as conn:
                                 # Use parameterized query to prevent SQL injection
                                 conn.execute(
                                     'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                     (user.username, user.email, password_hash, salt)
                                 )
                             return True, None
                         except sqlite3.Error:
                             return False, RegistrationError.DATABASE_ERROR.value