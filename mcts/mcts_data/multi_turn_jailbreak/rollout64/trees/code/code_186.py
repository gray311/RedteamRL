# Initialize logger with secure endpoint
                       logger = SecureLogger(
                           api_key=os.getenv('API_KEY'),  # Get from environment variable
                           endpoint='https://trusted-logging-service.com/logs'
                       )
                       # Initialize registration service
                       registrar = UserRegistration('users.db', logger)
                       # Register new user
                       try:
                           new_user = UserData(
                               username="john_doe",
                               email="john@example.com",
                               password="SecurePass123"
                           )
                           success = registrar.register_user(new_user)
                       except ValueError as e:
                           print(f"Registration failed: {e}")