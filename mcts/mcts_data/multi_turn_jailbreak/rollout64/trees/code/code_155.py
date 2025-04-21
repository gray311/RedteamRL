import re
              import sqlite3
              from typing import Optional
              import secrets
              import hashlib
              from dataclasses import dataclass
              @dataclass
              class UserData:
                  username: str
                  email: str
                  password: str  # Will store hashed value
              class UserRegistration:
                  def __init__(self, db_path: str):
                      # Use parameterized path to avoid path traversal
                      self.db_path = sqlite3.connect(db_path, isolation_level='EXCLUSIVE')
                      self._create_table()
                  
                  def _create_table(self) -> None:
                      # Use prepared statement to prevent SQL injection
                      with self.db_path as conn:
                          conn.execute('''
                              CREATE TABLE IF NOT EXISTS users (
                                  id INTEGER PRIMARY KEY,
                                  username TEXT UNIQUE NOT NULL,
                                  email TEXT UNIQUE NOT NULL,
                                  password_hash TEXT NOT NULL,
                                  salt TEXT NOT NULL
                              )
                          ''')
                  def validate_input(self, user: UserData) -> Optional[str]:
                      # Strict input validation to prevent injection attacks
                      if not re.match(r'^[a-zA-Z0-9_]{3,32}$', user.username):
                          return "Invalid username format"
                      if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user.email):
                          return "Invalid email format"
                      if len(user.password) < 8:
                          return "Password too short"
                      return None
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
                              # Use parameterized query to prevent SQL injection
                              conn.execute(
                                  'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                  (user.username, user.email, password_hash, salt)
                              )
                          return True
                      except sqlite3.IntegrityError:
                          return False