import requests
                       from typing import Dict
                       import json
                       import logging
                       from datetime import datetime
                       import hmac
                       import hashlib
                       class SecureLogger:
                           def __init__(self, api_key: str, endpoint: str):
                               self.endpoint = endpoint
                               self.api_key = api_key
                               # Validate HTTPS endpoint to prevent data exposure
                               if not endpoint.startswith('https://'):
                                   raise ValueError("Only HTTPS endpoints are allowed")
                           def _hash_identifier(self, value: str) -> str:
                               # Use separate hash for each identifier to prevent correlation
                               return hashlib.sha256(
                                   (value + secrets.token_hex(16)).encode()
                               ).hexdigest()
                           def log_registration(self, username: str, email: str, success: bool) -> bool:
                               # Hash identifiers separately with random salt
                               log_data = {
                                   'event_type': 'user_registration',
                                   'timestamp': datetime.utcnow().isoformat(),
                                   'username_hash': self._hash_identifier(username),
                                   'email_hash': self._hash_identifier(email) if success else None,
                                   'success': success
                               }
                               # Generate HMAC signature for request authentication
                               signature = hmac.new(
                                   self.api_key.encode(),
                                   json.dumps(log_data).encode(),
                                   hashlib.sha256
                               ).hexdigest()
                               try:
                                   response = requests.post(
                                       self.endpoint,
                                       json=log_data,
                                       headers={
                                           'X-API-Signature': signature,
                                           'Content-Type': 'application/json'
                                       },
                                       timeout=5
                                   )
                                   return response.status_code == 200
                               except requests.exceptions.RequestException as e:
                                   logging.error(f"Failed to send log: {str(e)}")
                                   return False