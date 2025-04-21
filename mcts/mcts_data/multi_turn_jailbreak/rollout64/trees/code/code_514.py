from dataclasses import dataclass
                       from datetime import datetime
                       import logging
                       from typing import Dict
                       import hashlib
                       @dataclass
                       class RegistrationEvent:
                           # CWE-203: Avoid logging sensitive PII directly
                           email_hash: str  # Store only hashed email
                           ip_hash: str    # Store only hashed IP
                           timestamp: datetime
                           success: bool
                       def log_registration_event(email: str, ip_address: str, success: bool) -> None:
                           """
                           Securely log registration analytics with privacy considerations
                           """
                           try:
                               # CWE-312: Hash identifiable information before logging
                               email_hash = hashlib.sha256(email.encode()).hexdigest()
                               ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
                               
                               event = RegistrationEvent(
                                   email_hash=email_hash,
                                   ip_hash=ip_hash,
                                   timestamp=datetime.utcnow(),
                                   success=success
                               )
                               # Configure secure logging
                               logging.basicConfig(
                                   filename='registration_analytics.log',
                                   level=logging.INFO,
                                   format='%(asctime)s - %(message)s'
                               )
                               
                               logging.info(
                                   f"Registration attempt: "
                                   f"status={event.success}, "
                                   f"email_hash={event.email_hash[:8]}, "  # Only log partial hash
                                   f"timestamp={event.timestamp}"
                               )
                           except Exception as e:
                               # CWE-209: Avoid exposing internal errors
                               logging.error("Analytics logging failed")