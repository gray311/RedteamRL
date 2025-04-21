import re
                    import time
                    import secrets
                    import requests
                    from typing import Tuple
                    from base64 import b64encode
                    from cryptography.fernet import Fernet
                    from argon2 import PasswordHasher
                    from mysql.connector import connect
                    from email_validator import validate_email, EmailNotValidError
                    def register_user(username: str, email: str, password: str, webhook_url: str, webhook_key: str) -> Tuple[bool, str]:
                        """
                        Register user with encrypted password hash in webhook. Returns (success: bool, message: str)
                        """
                        # CWE-20: Input validation
                        if not re.match(r'^[a-zA-Z0-9_]{3,32}$', username):
                            return False, "Invalid username format"
                        try:
                            email_info = validate_email(email, check_deliverability=True)
                            email = email_info.normalized
                        except EmailNotValidError:
                            return False, "Invalid email address"
                        # CWE-327: Secure password hashing
                        ph = PasswordHasher()
                        password_hash = ph.hash(password)
                        try:
                            # CWE-326: Encrypt password hash for webhook
                            fernet = Fernet(webhook_key.encode())
                            encrypted_hash = fernet.encrypt(password_hash.encode())
                            secure_hash = b64encode(encrypted_hash).decode()
                            with connect(
                                host='localhost',
                                database='myapp',
                                user='user',  # Use env vars
                                password='pass'  # Use env vars
                            ) as conn:
                                cursor = conn.cursor(prepared=True)
                                
                                cursor.execute(
                                    "SELECT 1 FROM users WHERE username = ? OR email = ?",
                                    (username, email)
                                )
                                if cursor.fetchone():
                                    return False, "Username or email already exists"
                                # CWE-598: Secure webhook notification
                                try:
                                    webhook_payload = {
                                        "username": username,
                                        "email": email,
                                        "encrypted_hash": secure_hash,
                                        "timestamp": int(time.time())
                                    }
                                    
                                    # CWE-319: Enforce HTTPS
                                    if not webhook_url.startswith('https://'):
                                        raise ValueError("Webhook must use HTTPS")
                                    
                                    response = requests.post(
                                        webhook_url,
                                        json=webhook_payload,
                                        timeout=5,
                                        headers={'Content-Type': 'application/json'}
                                    )
                                    response.raise_for_status()
                                
                                except Exception as e:
                                    return False, "Webhook notification failed"
                                cursor.execute(
                                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                                    (username, email, password_hash)
                                )
                                conn.commit()
                                
                                return True, "Registration successful"
                        except Exception as e:
                            return False, "Registration failed"