import logging
                       from datetime import datetime
                       import json
                       from pathlib import Path
                       from logging.handlers import RotatingFileHandler
                       # Configure secure logging
                       def setup_secure_logging():
                           """
                           Setup logging with security best practices
                           - CWE-532: Insertion of Sensitive Information into Log File
                           - CWE-779: Logging of Excessive Data
                           """
                           log_dir = Path("secure_logs")
                           log_dir.mkdir(exist_ok=True)
                           
                           # Secure file permissions
                           log_file = log_dir / "notification_logs.log"
                           log_file.touch(mode=0o600)
                           
                           formatter = logging.Formatter(
                               '%(asctime)s - %(levelname)s - %(message)s',
                               datefmt='%Y-%m-%d %H:%M:%S'
                           )
                           
                           handler = RotatingFileHandler(
                               log_file,
                               maxBytes=10485760,  # 10MB
                               backupCount=5,
                               delay=True
                           )
                           handler.setFormatter(formatter)
                           
                           logger = logging.getLogger('notification_service')
                           logger.setLevel(logging.INFO)
                           logger.addHandler(handler)
                           
                           return logger
                       logger = setup_secure_logging()
                       def async_notify_external(username: str, email: str) -> None:
                           """
                           Securely notify external service about new registration with logging
                           - CWE-319: Uses HTTPS
                           - CWE-532: Secure logging practices
                           """
                           # Mask sensitive data for logging
                           masked_email = f"{email[:3]}...@{email.split('@')[1]}"
                           
                           try:
                               logger.info(
                                   "Starting external notification for user: %s",
                                   username
                               )
                               
                               for attempt in range(3):  # 3 retries
                                   try:
                                       response = requests.post(
                                           'https://api.example.com/notifications',
                                           json={'username': username, 'email': email},
                                           headers={
                                               'X-API-Key': os.getenv('EXTERNAL_API_KEY', 'test_key'),
                                               'Content-Type': 'application/json'
                                           },
                                           timeout=5,
                                           verify=True
                                       )
                                       
                                       if response.status_code == 200:
                                           logger.info(
                                               "Successfully notified external service for user: %s",
                                               username
                                           )
                                           break
                                       else:
                                           logger.warning(
                                               "Attempt %d failed with status code %d for user: %s",
                                               attempt + 1,
                                               response.status_code,
                                               username
                                           )
                                           
                                   except requests.exceptions.RequestException as e:
                                       logger.error(
                                           "Attempt %d failed for user %s: %s",
                                           attempt + 1,
                                           username,
                                           str(e.__class__.__name__)
                                       )
                                       
                               else:  # All retries failed
                                   logger.error(
                                       "All notification attempts failed for user: %s",
                                       username
                                   )
                                   
                           except Exception as e:
                               logger.error(
                                   "Unexpected error during notification for user %s: %s",
                                   username,
                                   str(e.__class__.__name__)
                               )
                       # Update register() function to include logging
                       @app.route('/register', methods=['POST'])
                       def register():
                           try:
                               # ... (previous registration code) ...
                               # Log successful registration
                               logger.info("User registration successful: %s", username)
                               
                               # Trigger async notification
                               threading.Thread(
                                   target=async_notify_external,
                                   args=(username, email),
                                   daemon=True
                               ).start()
                               return jsonify({'message': 'Registration successful'}), 201
                           except Exception as e:
                               logger.error("Registration failed: %s", str(e.__class__.__name__))
                               return jsonify({'error': 'Registration failed'}), 500