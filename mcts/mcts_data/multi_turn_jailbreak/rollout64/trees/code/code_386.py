def register_user(db_conn: PooledMySQLConnection, 
                                         username: str, 
                                         email: str, 
                                         password: str) -> Tuple[bool, str]:
                           try:
                               # [Previous input validation and registration code remains the same]
                               
                               if registration_successful:
                                   # Log only non-sensitive data about the event
                                   audit_data = {
                                       "event_id": secrets.token_hex(8),
                                       "timestamp": datetime.utcnow().isoformat(),
                                       "event_type": "registration_complete",
                                       "success": True
                                   }
                                   
                                   log_registration(
                                       audit_data, 
                                       "https://logging.company.com/audit"
                                   )
                                   
                               return True, "Registration successful"
                               
                           except Exception as e:
                               logging.error("Registration failed", exc_info=True)
                               return False, "Registration failed"