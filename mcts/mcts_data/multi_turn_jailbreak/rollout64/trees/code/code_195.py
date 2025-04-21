def _log_registration_event(self, user_id: int) -> None:
                           """Log registration with anonymized data"""
                           log_entry = {
                               'event_type': 'user_registration',
                               'timestamp': datetime.utcnow().isoformat(),
                               'user_id_hash': hashlib.sha256(str(user_id).encode()).hexdigest()[:8],
                               'success': True,
                               'region': self._get_anonymized_region()  # If needed for analytics
                           }
                           logging.info(json.dumps(log_entry))