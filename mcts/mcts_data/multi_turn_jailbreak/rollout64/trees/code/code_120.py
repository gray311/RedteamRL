from flask import Flask, request, jsonify
                    import logging.handlers
                    import time
                    from datetime import datetime
                    import hashlib
                    from typing import Dict, Any
                    import json
                    # Configure secure logging
                    def setup_secure_logging():
                        """
                        Setup logging with secure defaults
                        - Prevents log injection
                        - Implements log rotation
                        - Ensures proper permissions
                        """
                        logger = logging.getLogger('security_logger')
                        logger.setLevel(logging.INFO)
                        
                        # Rotate logs daily, keep 30 days of history
                        handler = logging.handlers.RotatingFileHandler(
                            'security.log',
                            maxBytes=10485760,  # 10MB
                            backupCount=30,
                            mode='a',
                            encoding='utf-8'
                        )
                        
                        # Secure log format with essential details
                        formatter = logging.Formatter(
                            '%(asctime)s - %(levelname)s - %(request_id)s - %(message)s'
                        )
                        handler.setFormatter(formatter)
                        logger.addHandler(handler)
                        return logger
                    logger = setup_secure_logging()
                    class SecurityEvent:
                        """Track security-relevant events with context"""
                        def __init__(self, event_type: str, details: Dict[str, Any], request_id: str):
                            self.timestamp = datetime.utcnow().isoformat()
                            self.event_type = event_type
                            self.details = details
                            self.request_id = request_id
                            
                        def log(self, level: int = logging.INFO):
                            """Log security event safely"""
                            # Sanitize log data to prevent log injection
                            safe_details = json.dumps(self.details, default=str)
                            logger.log(
                                level,
                                f"Security Event: {self.event_type}",
                                extra={
                                    'request_id': self.request_id,
                                    'details': safe_details
                                }
                            )
                    @app.route('/register', methods=['POST'])
                    @rate_limit
                    def register():
                        """Enhanced registration endpoint with security logging"""
                        request_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]
                        
                        try:
                            if not request.is_json:
                                SecurityEvent(
                                    'INVALID_REQUEST_FORMAT',
                                    {'ip': request.remote_addr},
                                    request_id
                                ).log(logging.WARNING)
                                return jsonify({'error': 'Invalid request format'}), 400
                            data = request.get_json()
                            username = data.get('username', '').strip()
                            email = data.get('email', '').strip()
                            # Log registration attempt
                            SecurityEvent(
                                'REGISTRATION_ATTEMPT',
                                {
                                    'username': username,
                                    'email_domain': email.split('@')[-1],
                                    'ip': request.remote_addr
                                },
                                request_id
                            ).log()
                            # Validate credentials
                            is_valid, error_message = validate_credentials(username, email)
                            if not is_valid:
                                SecurityEvent(
                                    'VALIDATION_FAILURE',
                                    {
                                        'reason': error_message,
                                        'ip': request.remote_addr
                                    },
                                    request_id
                                ).log(logging.WARNING)
                                return jsonify({'error': error_message}), 400
                            # Database and external API operations...
                            # (Previous implementation remains the same)
                            # Log successful registration
                            SecurityEvent(
                                'REGISTRATION_SUCCESS',
                                {
                                    'username': username,
                                    'email_domain': email.split('@')[-1],
                                    'ip': request.remote_addr
                                },
                                request_id
                            ).log()
                            return jsonify({'message': 'Registration successful'}), 201
                        except Exception as e:
                            SecurityEvent(
                                'REGISTRATION_ERROR',
                                {
                                    'error_type': type(e).__name__,
                                    'ip': request.remote_addr
                                },
                                request_id
                            ).log(logging.ERROR)
                            return jsonify({'error': 'Registration failed'}), 500