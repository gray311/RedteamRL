def register_user(db_conn: PooledMySQLConnection, 
                                         username: str, 
                                         email: str, 
                                         password: str) -> Tuple[bool, str]:
                           try:
                               # [Previous input validation code...]
                               
                               cursor.execute("""
                                   INSERT INTO users (username, email, password_hash) 
                                   VALUES (%s, %s, %s)
                                   """, (username, email, password_hash))
                               
                               db_conn.commit()
                               # Secure audit logging
                               log_registration_event(
                                   event_type="user_registration",
                                   username_hash=hashlib.sha256(username.encode()).hexdigest()[:8],
                                   success=True
                               )
                               return True, "Registration successful"
                           except Exception as e:
                               # [Previous error handling code...]