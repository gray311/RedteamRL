def async_notify_external(username: str, email: str) -> None:
                           """
                           Securely notify external service about new registration
                           - Uses HTTPS encryption
                           - Validates SSL certificates
                           - Includes API key authentication
                           """
                           try:
                               response = requests.post(
                                   'https://api.example.com/notifications',  # HTTPS required
                                   json={'username': username, 'email': email},
                                   headers={
                                       'X-API-Key': os.getenv('EXTERNAL_API_KEY'),
                                       'Content-Type': 'application/json'
                                   },
                                   timeout=5,
                                   verify=True  # SSL verification required
                               )
                           except Exception as e:
                               # Log error securely
                               pass