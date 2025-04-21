def register_user(username: str, password: str, email: str) -> Optional[bool]:
                     """Register user with transparent, consensual logging"""
                     # Inform user about data collection in privacy policy
                     # Log only necessary information with user consent
                     logging.info(f"New user registration attempt for username: {username}")
                     
                     # ... rest of the secure registration code ...