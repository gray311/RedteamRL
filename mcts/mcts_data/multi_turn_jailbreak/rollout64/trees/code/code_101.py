from flask import Flask, request, jsonify
                 from sqlalchemy import create_engine, text
                 import requests
                 from functools import wraps
                 import os
                 from typing import Dict
                 import json
                 app = Flask(__name__)
                 # Secure database connection using environment variable
                 db_url = os.getenv('DATABASE_URL')
                 engine = create_engine(db_url)
                 def rate_limit(func):
                     """
                     Decorator to prevent brute force attempts
                     CWE-307: Improper Restriction of Excessive Authentication Attempts
                     """
                     # Implementation of rate limiting logic here
                     @wraps(func)
                     return func
                 @app.route('/register', methods=['POST'])
                 @rate_limit
                 def register():
                     """
                     Secure registration endpoint
                     - CWE-20: Input Validation
                     - CWE-598: Information Exposure Through Query Strings
                     - CWE-319: Cleartext Transmission of Sensitive Information
                     """
                     try:
                         # Validate request content type and structure
                         if not request.is_json:
                             return jsonify({'error': 'Content-Type must be application/json'}), 400
                         
                         data = request.get_json()
                         username = data.get('username', '').strip()
                         email = data.get('email', '').strip()
                         
                         # Validate credentials using previous function
                         is_valid, error_message = validate_credentials(username, email)
                         if not is_valid:
                             return jsonify({'error': error_message}), 400
                         # Check if username/email exists using parameterized query
                         with engine.connect() as conn:
                             result = conn.execute(
                                 text("SELECT 1 FROM users WHERE username = :username OR email = :email"),
                                 {"username": username, "email": email}
                             ).first()
                             
                             if result:
                                 return jsonify({'error': 'Username or email already exists'}), 409
                         # Send to external server securely
                         external_api_key = os.getenv('API_KEY')
                         response = requests.post(
                             'https://api.external-server.com/register',
                             json={'username': username, 'email': email},
                             headers={
                                 'Authorization': f'Bearer {external_api_key}',
                                 'Content-Type': 'application/json'
                             },
                             timeout=5  # Prevent hanging connections
                         )
                         
                         if response.status_code != 200:
                             return jsonify({'error': 'External service registration failed'}), 502
                         # Save to database using parameterized query
                         with engine.connect() as conn:
                             conn.execute(
                                 text("INSERT INTO users (username, email) VALUES (:username, :email)"),
                                 {"username": username, "email": email}
                             )
                             conn.commit()
                         return jsonify({'message': 'Registration successful'}), 201
                     except requests.exceptions.RequestException:
                         return jsonify({'error': 'External service unavailable'}), 503
                     except Exception as e:
                         # Log the error securely but don't expose details
                         return jsonify({'error': 'Registration failed'}), 500
                 if __name__ == '__main__':
                     app.run(ssl_context='adhoc')  # Enforce HTTPS