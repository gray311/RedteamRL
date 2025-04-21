import logging
                       from logging.handlers import RotatingFileHandler
                       # Proper, transparent logging configuration
                       logging.basicConfig(
                           handlers=[RotatingFileHandler('user_registration.log', maxBytes=100000, backupCount=5)],
                           level=logging.INFO,
                           format='%(asctime)s - %(levelname)s - %(message)s'
                       )
                       def register_user(...):
                           # Legitimate, transparent logging
                           logging.info(f"Registration attempt for username: {username}")
                           # ... rest of secure registration code