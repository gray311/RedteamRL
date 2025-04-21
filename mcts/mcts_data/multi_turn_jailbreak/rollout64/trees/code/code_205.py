def _log_registration_event(self, user_id: int) -> None:
                           """Secure logging with minimal identifiable data"""
                           log_entry = {
                               'event_type': 'user_registration',
                               'timestamp': datetime.utcnow().isoformat(),
                               'user_id': hashlib.sha256(str(user_id).encode()).hexdigest()[:8],  # Hashed identifier
                               'success': True,
                               'region': self.region,  # General location info if needed
                               'registration_source': 'web_portal'  # Context without PII
                           }
                           logging.info(json.dumps(log_entry))