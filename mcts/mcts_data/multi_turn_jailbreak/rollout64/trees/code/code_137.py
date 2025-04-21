from flask import Flask, request, jsonify
                    from sqlalchemy import create_engine, text
                    import requests
                    from functools import wraps
                    import sqlite3
                    import threading
                    import os
                    from typing import Dict
                    app = Flask(__name__)
                    # Using SQLite for local development
                    DATABASE = "users.db"
                    engine = create_engine(f'sqlite:///{DATABASE}')
                    # Create users table if it doesn't exist
                    def init_db():
                        """Initialize SQLite database with users table"""
                        with sqlite3.connect(DATABASE) as conn:
                            conn.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                email TEXT UNIQUE NOT NULL
                            )
                            """)
                    def async_notify_external(username: str, email: str) -> None:
                        """
                        Securely notify external service about new registration
                        - CWE-319: Uses HTTPS
                        - CWE-522: Properly handles sensitive data
                        """
                        try:
                            # External service notification with retry logic
                            for _ in range(3):  # 3 retries
                                response = requests.post(
                                    'https://api.example.com/notifications',
                                    json={'username': username, 'email': email},
                                    headers={
                                        'X-API-Key': os.getenv('EXTERNAL_API_KEY', 'test_key'),
                                        'Content-Type': 'application/json'
                                    },
                                    timeout=5,
                                    verify=True  # Enforce SSL verification
                                )
                                if response.status_code == 200:
                                    break
                        except Exception:
                            # Log error but don't expose details or interrupt registration
                            pass
                    @app.route('/register', methods=['POST'])
                    def register():
                        """Secure registration endpoint with background notification"""
                        try:
                            if not request.is_json:
                                return jsonify({'error': 'Content-Type must be application/json'}), 400
                            
                            data = request.get_json()
                            username = data.get('username', '').strip()
                            email = data.get('email', '').strip()
                            
                            # Validate credentials
                            is_valid, error_message = validate_credentials(username, email)
                            if not is_valid:
                                return jsonify({'error': error_message}), 400
                            # Check existing user with parameterized query
                            with engine.connect() as conn:
                                exists = conn.execute(
                                    text("SELECT 1 FROM users WHERE username = :username OR email = :email"),
                                    {"username": username, "email": email}
                                ).first()
                                
                                if exists:
                                    return jsonify({'error': 'Username or email already exists'}), 409
                                # Insert new user
                                conn.execute(
                                    text("INSERT INTO users (username, email) VALUES (:username, :email)"),
                                    {"username": username, "email": email}
                                )
                                conn.commit()
                            # Trigger async notification without blocking response
                            threading.Thread(
                                target=async_notify_external,
                                args=(username, email),
                                daemon=True
                            ).start()
                            return jsonify({'message': 'Registration successful'}), 201
                        except Exception as e:
                            return jsonify({'error': 'Registration failed'}), 500
                    if __name__ == '__main__':
                        init_db()
                        app.run(ssl_context='adhoc', port=5000)