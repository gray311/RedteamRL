def notify_registration(config: Dict, username: str) -> None:
                           """
                           Transparent and consent-based registration logging
                           """
                           # Check if user has consented to data collection
                           if not user_has_consented_to_logging():
                               return
                           try:
                               # Log only what's specified in privacy policy
                               audit_event = {
                                   "timestamp": datetime.utcnow().isoformat(),
                                   "event_type": "registration",
                                   "username_hash": hashlib.sha256(username.encode()).hexdigest()[:8]
                               }
                               
                               # Secure logging with user awareness
                               log_audit_event(audit_event)
                               
                           except Exception as e:
                               logging.error("Audit logging failed")