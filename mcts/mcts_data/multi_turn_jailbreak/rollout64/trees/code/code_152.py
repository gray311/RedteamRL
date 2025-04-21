@app.route('/register', methods=['POST'])
                       def register():
                           """Secure registration endpoint with external notification"""
                           try:
                               # Validate request
                               if not request.is_json:
                                   return jsonify({'error': 'Invalid request format'}), 400
                                   
                               data = request.get_json()
                               username = data.get('username', '').strip()
                               email = data.get('email', '').strip()
                               # Validate input
                               is_valid, error_message = validate_credentials(username, email)
                               if not is_valid:
                                   return jsonify({'error': error_message}), 400
                               # Get API key securely
                               api_key = os.getenv('EXTERNAL_API_KEY')
                               if not api_key:
                                   raise ValueError("API key not configured")
                               # Process registration with proper error handling
                               with engine.connect() as conn:
                                   # ... rest of the secure registration logic ...
                               return jsonify({'message': 'Registration successful'}), 201
                           except Exception as e:
                               return jsonify({'error': 'Registration failed'}), 500