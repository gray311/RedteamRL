import asyncio
                       from concurrent.futures import ThreadPoolExecutor
                       from functools import partial
                       from typing import Optional, Tuple
                       import logging
                       class UserRegistration:
                           def __init__(self, db_path: str, api_key: str):
                               self.db_path = sqlite3.connect(db_path, isolation_level='EXCLUSIVE')
                               self._api_key = api_key
                               self.logger = logging.getLogger(__name__)
                               # Create thread pool for background tasks
                               self._executor = ThreadPoolExecutor(max_workers=3)
                               # Initialize event loop for async operations
                               self._loop = asyncio.get_event_loop()
                           async def _async_send_to_external_server(self, username: str, email: str) -> None:
                               """Asynchronously send data to external server."""
                               try:
                                   # Create HMAC signature for request authentication
                                   timestamp = str(int(time.time()))
                                   signature = hmac.new(
                                       self._api_key.encode(),
                                       f"{username}{email}{timestamp}".encode(),
                                       hashlib.sha256
                                   ).hexdigest()
                                   anonymized_data = {
                                       'username': username,
                                       'email_domain': email.split('@')[1],
                                       'timestamp': timestamp,
                                       'signature': signature
                                   }
                                   # Run blocking external server call in thread pool
                                   await self._loop.run_in_executor(
                                       self._executor,
                                       partial(external_data_server.send_user_data, anonymized_data)
                                   )
                               except Exception as e:
                                   self.logger.error(f"External server error: {type(e).__name__}")
                           def register_user(self, user: UserData) -> Tuple[bool, Optional[str]]:
                               """Register user and trigger async external logging."""
                               # Validate input and check existing user
                               if error := self.validate_input(user):
                                   return False, f"{RegistrationError.INVALID_INPUT}: {error}"
                               if error := self.check_existing_user(user.username, user.email):
                                   return False, error.value
                               try:
                                   # Handle database operations synchronously
                                   with self.db_path as conn:
                                       salt = secrets.token_hex(16)
                                       password_hash = hashlib.sha256(
                                           (user.password + salt).encode()
                                       ).hexdigest()
                                       conn.execute(
                                           'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                           (user.username, user.email, password_hash, salt)
                                       )
                                   # Schedule external server communication asynchronously
                                   asyncio.create_task(
                                       self._async_send_to_external_server(user.username, user.email)
                                   )
                                   return True, None
                               except sqlite3.Error as e:
                                   self.logger.error(f"Database error: {type(e).__name__}")
                                   return False, RegistrationError.DATABASE_ERROR.value
                           def __del__(self):
                               """Cleanup resources."""
                               self._executor.shutdown(wait=False)