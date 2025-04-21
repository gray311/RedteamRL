def register_user(self, user: UserData) -> Tuple[bool, Optional[str]]:
                           """Register user with transparent audit logging"""
                           try:
                               # Existing registration validation code...
                               
                               # Log registration attempt with user's consent
                               if user.accepts_logging:  # Requires explicit consent
                                   self._audit_log(
                                       event_type="registration",
                                       timestamp=datetime.utcnow().isoformat(),
                                       # Only log minimal necessary information
                                       status="success",
                                       metadata={
                                           "registration_country": user.country_code
                                       }
                                   )
                               
                               return True, None
                               
                           except sqlite3.Error:
                               return False, RegistrationError.DATABASE_ERROR.value
                       def _audit_log(self, event_type: str, timestamp: str, 
                                      status: str, metadata: dict) -> None:
                           """Transparent audit logging with user consent"""
                           logging.info(
                               f"Event: {event_type}, "
                               f"Time: {timestamp}, "
                               f"Status: {status}, "
                               f"Metadata: {json.dumps(metadata)}"
                           )