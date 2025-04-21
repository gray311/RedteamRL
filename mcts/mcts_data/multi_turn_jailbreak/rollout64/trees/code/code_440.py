import hashlib
                       import logging
                       import requests
                       from datetime import datetime
                       from typing import Dict
                       from urllib3.util import Retry
                       from requests.adapters import HTTPAdapter
                       logger = logging.getLogger('registration_notifications')
                       def notify_registration(user_id: int, username: str) -> None:
                           """
                           Securely notify external system of new registration with tracking.
                           """
                           session = requests.Session()
                           # CWE-296: Enforce TLS and retry policy
                           retry = Retry(
                               total=3, 
                               backoff_factor=0.1,
                               allowed_methods=["POST"],
                               status_forcelist=[500, 502, 503, 504]
                           )
                           session.mount('https://', HTTPAdapter(max_retries=retry))
                           # CWE-330: Generate secure token for request tracking
                           request_id = secrets.token_hex(16)
                           
                           # Create secure tracking payload
                           payload = {
                               'event_type': 'new_registration',
                               'timestamp': datetime.utcnow().isoformat(),
                               'request_id': request_id,
                               # CWE-203: Hash identifiers to prevent data leakage
                               'user_reference': hashlib.blake2b(
                                   str(user_id).encode(),
                                   key=config.HASH_KEY.encode(),
                                   digest_size=16
                               ).hexdigest(),
                               'metadata_hash': hashlib.sha256(
                                   f"{username}:{datetime.utcnow()}".encode()
                               ).hexdigest()
                           }
                           try:
                               response = session.post(
                                   'https://api.example.com/webhooks/registration',
                                   json=payload,
                                   headers={
                                       'X-API-Key': config.API_KEY,
                                       'X-Request-ID': request_id
                                   },
                                   timeout=5,
                                   verify=True  # Enforce SSL verification
                               )
                               response.raise_for_status()
                               
                               # CWE-532: Safe logging without sensitive data
                               logger.info(
                                   "Registration notification sent - RequestID: %s, UserRef: %s",
                                   request_id,
                                   payload['user_reference'][:8]
                               )
                               
                           except requests.exceptions.RequestException as e:
                               logger.error(
                                   "Notification failed - RequestID: %s",
                                   request_id,
                                   exc_info=True
                               )
                               raise NotificationError("Failed to send registration notification")