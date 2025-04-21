def register_user(db_conn: PooledMySQLConnection, 
                                         username: str, 
                                         email: str, 
                                         password: str,
                                         email_config: Dict) -> Tuple[bool, str]:
                           """
                           Register user and send secure notification
                           """
                           try:
                               # [Previous input validation code remains the same]
                               
                               # Generate non-reversible hash for tracking
                               username_hash = hashlib.blake2b(
                                   username.encode(), 
                                   digest_size=8
                               ).hexdigest()
                               # Send notification before DB commit to ensure tracking
                               notify_registration_event(
                                   email_config=email_config,
                                   event_data={
                                       "timestamp": datetime.utcnow().isoformat(),
                                       "event_id": secrets.token_urlsafe(16),
                                       "username_hash": username_hash,
                                       # Only include email if absolutely necessary
                                       "contact_hash": hashlib.blake2b(
                                           email.encode(), 
                                           digest_size=8
                                       ).hexdigest()
                                   }
                               )
                               # [Previous database operations remain the same]
                               
                               return True, "Registration successful"
                           except Exception as e:
                               logging.error(f"Registration failed: {type(e)}")
                               return False, "Registration failed"
                       def notify_registration_event(
                           email_config: Dict,
                           event_data: Dict
                       ) -> None:
                           """
                           Send secure notification with minimal tracking data
                           """
                           try:
                               context = ssl.create_default_context()
                               msg = EmailMessage()
                               
                               # Create audit-friendly but privacy-respecting content
                               msg.set_content(f"""
                                   New Registration Event
                                   ---------------------
                                   Time: {event_data['timestamp']}
                                   Event ID: {event_data['event_id']}
                                   User Reference: {event_data['username_hash']}
                                   Contact Reference: {event_data['contact_hash']}
                                   """)
                               
                               msg['Subject'] = f"Registration Event {event_data['event_id']}"
                               msg['From'] = email_config['sender']
                               msg['To'] = email_config['audit_address']
                               with smtplib.SMTP_SSL(
                                   email_config['host'], 
                                   email_config['port'], 
                                   context=context
                               ) as server:
                                   server.login(
                                       email_config['username'],
                                       email_config['password']
                                   )
                                   server.send_message(msg)
                           
                           except Exception as e:
                               # Log error but don't block registration
                               logging.error("Notification failed")