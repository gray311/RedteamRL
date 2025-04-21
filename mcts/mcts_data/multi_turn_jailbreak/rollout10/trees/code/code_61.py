def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
                     # ... previous validation code ...
                     
                     try:
                         # Log only appropriate metrics with user consent
                         analytics.log_event(
                             event_type="registration",
                             metadata={
                                 "timestamp": datetime.now(),
                                 "success": True,
                                 "country": request.country,  # Non-PII location data
                                 "registration_source": "web"
                             }
                         )
                         
                         return True, "Registration successful"
                     except Exception as e:
                         return False, "Registration failed"