def register_user(db_conn: PooledMySQLConnection, 
                                         username: str, 
                                         email: str, 
                                         password: str) -> Tuple[bool, str]:
                           """
                           Securely register a new user with logging for successful registrations
                           """
                           try:
                               # [Previous input validation code remains the same]
                               
                               # CWE-521: Password complexity validation
                               if len(password) < 12:
                                   return False, "Password must be at least 12 characters"
                               ph = PasswordHasher()
                               password_hash = ph.hash(password)
                               # Begin transaction
                               cursor = db_conn.cursor(prepared=True)
                               
                               # [Previous uniqueness check and insert code remains the same]
                               
                               db_conn.commit()
                               
                               # Only log after successful commit
                               audit_data = {
                                   "event_type": "user_registration",
                                   "timestamp": datetime.utcnow().isoformat(),
                                   "username_hash": hashlib.sha256(username.encode()).hexdigest()[:8],
                                   "ip_country": get_country_code(),  # Implement as needed
                                   "success": True
                               }
                               
                               # Async logging to not block registration
                               asyncio.create_task(
                                   log_security_event(
                                       log_type="registration",
                                       audit_data=audit_data,
                                       log_server_url=config.LOG_SERVER_URL
                                   )
                               )
                               
                               return True, "Registration successful"
                           except Exception as e:
                               if 'db_conn' in locals():
                                   db_conn.rollback()
                               return False, "Registration failed"
                           finally:
                               if 'cursor' in locals():
                                   cursor.close()
                       async def log_security_event(log_type: str, 
                                                  audit_data: dict,
                                                  log_server_url: str) -> None:
                           """
                           Securely log security events to external server
                           """
                           try:
                               if not log_server_url.startswith("https://"):
                                   raise ValueError("HTTPS required for logging")
                                   
                               async with aiohttp.ClientSession() as session:
                                   async with session.post(
                                       log_server_url,
                                       json=audit_data,
                                       headers={
                                           "Content-Type": "application/json",
                                           "X-Audit-Event": log_type
                                       },
                                       timeout=aiohttp.ClientTimeout(total=5)
                                   ) as response:
                                       response.raise_for_status()
                           except Exception as e:
                               logging.error(f"Audit logging failed: {str(e)}")