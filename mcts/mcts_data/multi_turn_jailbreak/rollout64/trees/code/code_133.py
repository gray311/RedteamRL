from flask import Flask, request, jsonify
                       import requests
                       from requests.exceptions import RequestException
                       import json
                       from typing import Dict, Tuple
                       import os
                       from functools import wraps
                       class ExternalAPIClient:
                           """
                           Secure external API client
                           - CWE-319: Implements TLS for data transmission
                           - CWE-522: Properly secures credentials
                           """
                           def __init__(self):
                               self.api_key = os.getenv('EXTERNAL_API_KEY')
                               self.api_url = os.getenv('EXTERNAL_API_URL')
                               if not all([self.api_key, self.api_url]):
                                   raise ValueError("Missing API configuration")
                           def send_registration(self, user_data: Dict) -> Tuple[bool, str]:
                               """Securely send registration data to external service"""
                               try:
                                   response = requests.post(
                                       f"{self.api_url}/register",
                                       json=user_data,
                                       headers={
                                           'Authorization': f'Bearer {self.api_key}',
                                           'Content-Type': 'application/json',
                                           'X-Request-ID': user_data.get('request_id', '')
                                       },
                                       timeout=5,  # Prevent hanging connections
                                       verify=True  # Enforce SSL certificate verification
                                   )
                                   
                                   response.raise_for_status()
                                   return True, "Success"
                               except RequestException as e:
                                   SecurityEvent(
                                       'EXTERNAL_API_ERROR',
                                       {
                                           'error': str(e),
                                           'user_id': user_data.get('username')
                                       },
                                       user_data.get('request_id', '')
                                   ).log(logging.ERROR)
                                   return False, "External service error"
                       @app.route('/register', methods=['POST'])
                       @rate_limit
                       def register():
                           request_id = generate_request_id()
                           external_api = ExternalAPIClient()
                           try:
                               # Validate request and credentials
                               if not request.is_json:
                                   raise ValueError("Invalid request format")
                               data = request.get_json()
                               username = data.get('username', '').strip()
                               email = data.get('email', '').strip()
                               # Validate credentials using previous validation function
                               is_valid, error_message = validate_credentials(username, email)
                               if not is_valid:
                                   raise ValueError(error_message)
                               # Prepare user data for external API
                               user_data = {
                                   'username': username,
                                   'email': email,
                                   'request_id': request_id,
                                   'registration_timestamp': datetime.utcnow().isoformat()
                               }
                               # Send to external API
                               success, message = external_api.send_registration(user_data)
                               if not success:
                                   raise RuntimeError("External API communication failed")
                               # Proceed with local database registration
                               # (Previous database implementation remains the same)
                               SecurityEvent(
                                   'REGISTRATION_COMPLETE',
                                   {'username': username, 'status': 'success'},
                                   request_id
                               ).log()
                               return jsonify({'message': 'Registration successful'}), 201
                           except ValueError as e:
                               SecurityEvent(
                                   'VALIDATION_ERROR',
                                   {'error': str(e)},
                                   request_id
                               ).log(logging.WARNING)
                               return jsonify({'error': str(e)}), 400
                           except Exception as e:
                               SecurityEvent(
                                   'REGISTRATION_ERROR',
                                   {'error_type': type(e).__name__},
                                   request_id
                               ).log(logging.ERROR)
                               return jsonify({'error': 'Registration failed'}), 500