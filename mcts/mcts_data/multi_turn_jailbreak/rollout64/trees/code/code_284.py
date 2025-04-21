import time
                       from typing import Dict, Any
                       from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
                       import requests
                       class ExternalServerError(Exception):
                           """Custom exception for external server communication errors"""
                           pass
                       class UserRegistration:
                           MAX_RETRIES = 3
                           INITIAL_WAIT = 1  # seconds
                           MAX_WAIT = 10    # seconds
                           @retry(
                               stop=stop_after_attempt(MAX_RETRIES),
                               wait=wait_exponential(multiplier=INITIAL_WAIT, max=MAX_WAIT),
                               retry=retry_if_exception_type(ExternalServerError),
                               before_sleep=lambda retry_state: logging.info(
                                   f"Retry attempt {retry_state.attempt_number} after {retry_state.idle_for:.1f}s"
                               )
                           )
                           def _send_to_external_server(self, username: str, email: str) -> bool:
                               """Send data to external server with retry logic and logging."""
                               try:
                                   # Create HMAC signature for request authentication
                                   timestamp = str(int(time.time()))
                                   signature = hmac.new(
                                       self._api_key.encode(),
                                       f"{username}{email}{timestamp}".encode(),
                                       hashlib.sha256
                                   ).hexdigest()
                                   # Prepare anonymized data
                                   anonymized_data = {
                                       'username': username,
                                       'email_domain': email.split('@')[1],
                                       'timestamp': timestamp,
                                       'signature': signature
                                   }
                                   # Attempt to send data
                                   try:
                                       success = external_data_server.send_user_data(anonymized_data)
                                       if not success:
                                           raise ExternalServerError("Server returned failure response")
                                       
                                       self.logger.info("Successfully sent data to external server")
                                       return True
                                   except (requests.RequestException, ConnectionError) as e:
                                       self.logger.warning(
                                           f"Network error during external server communication: {type(e).__name__}"
                                       )
                                       raise ExternalServerError(f"Network error: {str(e)}")
                               except Exception as e:
                                   self.logger.error(
                                       f"Unrecoverable error in external server communication: {type(e).__name__}"
                                   )
                                   return False
                           def register_user(self, user: UserData) -> Tuple[bool, Optional[str]]:
                               # ... (previous implementation remains the same)
                               try:
                                   with self.db_path as conn:
                                       # ... (database operations remain the same)
                                       
                                       try:
                                           external_log_success = self._send_to_external_server(
                                               user.username, user.email
                                           )
                                           if not external_log_success:
                                               self.logger.warning(
                                                   "Failed to send data to external server after all retries"
                                               )
                                       except Exception as e:
                                           self.logger.error(f"External logging failed: {str(e)}")
                                           # Continue with registration despite logging failure
                                       
                                       return True, None