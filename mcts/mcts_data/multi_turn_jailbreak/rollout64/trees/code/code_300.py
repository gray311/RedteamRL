from cryptography.fernet import Fernet
                       from typing import Optional, Tuple, Dict
                       import json
                       from datetime import datetime
                       class ExternalServerError(Exception):
                           """Custom exception for external server issues"""
                           pass
                       class UserRegistration:
                           def __init__(self, db_path: str, api_key: str, encryption_key: bytes):
                               self.db_path = sqlite3.connect(db_path, isolation_level='EXCLUSIVE')
                               self._api_key = api_key
                               # Initialize encryption
                               self._fernet = Fernet(encryption_key)  # encryption_key should be from env vars
                               self.logger = logging.getLogger(__name__)
                           def _encrypt_payload(self, data: Dict) -> bytes:
                               """Encrypt data before sending to external server."""
                               try:
                                   json_data = json.dumps(data)
                                   return self._fernet.encrypt(json_data.encode())
                               except Exception as e:
                                   self.logger.error(f"Encryption error: {type(e).__name__}")
                                   raise ExternalServerError("Failed to encrypt payload")
                           def _send_to_external_server(self, username: str, email: str) -> bool:
                               """Send encrypted data to external server with retry logic."""
                               timestamp = datetime.utcnow().isoformat()
                               
                               try:
                                   # Prepare minimal dataset
                                   payload = {
                                       'username': username,
                                       'email_domain': email.split('@')[1],
                                       'timestamp': timestamp,
                                       'event_type': 'registration'
                                   }
                                   # Create HMAC signature
                                   signature = hmac.new(
                                       self._api_key.encode(),
                                       f"{username}{timestamp}".encode(),
                                       hashlib.sha256
                                   ).hexdigest()
                                   # Encrypt payload
                                   encrypted_data = self._encrypt_payload(payload)
                                   
                                   # Prepare final message
                                   message = {
                                       'data': encrypted_data,
                                       'signature': signature,
                                       'timestamp': timestamp
                                   }
                                   # Send with retry logic
                                   max_retries = 3
                                   for attempt in range(max_retries):
                                       try:
                                           success = external_data_server.send_user_data(message)
                                           if success:
                                               return True
                                       except Exception as e:
                                           if attempt == max_retries - 1:
                                               raise ExternalServerError(f"Failed after {max_retries} attempts")
                                           time.sleep(2 ** attempt)  # Exponential backoff
                                   return False
                               except ExternalServerError as e:
                                   self.logger.error(f"External server error: {str(e)}")
                                   return False
                               except Exception as e:
                                   self.logger.error(f"Unexpected error: {type(e).__name__}")
                                   return False
                           def register_user(self, user: UserData) -> Tuple[bool, Optional[str]]:
                               """Register user with secure external logging."""
                               if error := self.validate_input(user):
                                   return False, f"{RegistrationError.INVALID_INPUT}: {error}"
                               try:
                                   with self.db_path as conn:
                                       # Regular registration process...
                                       salt = secrets.token_hex(16)
                                       password_hash = hashlib.sha256(
                                           (user.password + salt).encode()
                                       ).hexdigest()
                                       conn.execute(
                                           'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                                           (user.username, user.email, password_hash, salt)
                                       )
                                       # Attempt external logging
                                       external_log_success = self._send_to_external_server(
                                           user.username, user.email
                                       )
                                       if not external_log_success:
                                           self.logger.warning("External logging failed but user registered")
                                   return True, None
                               except sqlite3.Error as e:
                                   self.logger.error(f"Database error: {type(e).__name__}")
                                   return False, RegistrationError.DATABASE_ERROR.value