def register_user(...):
                           # Previous secure registration code
                           
                           # Secure audit logging
                           audit_log = {
                               "timestamp": datetime.utcnow().isoformat(),
                               "event_type": "registration",
                               "success": True,
                               "username_hash": hashlib.sha256(username.encode()).hexdigest()[:8]
                           }
                           
                           logging.info("Registration completed", extra=audit_log)