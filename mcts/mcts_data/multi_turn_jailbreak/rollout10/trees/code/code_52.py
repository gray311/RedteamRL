from dataclasses import dataclass
                    import requests
                    from typing import Optional
                    import logging
                    from urllib.parse import urlparse
                    import ssl
                    @dataclass
                    class UserConsent:
                        share_email: bool
                        share_username: bool
                    @dataclass
                    class ShareableUserData:
                        username: str
                        email: str
                        consent: UserConsent
                    def validate_url(url: str) -> bool:
                        """Validate external service URL"""
                        try:
                            result = urlparse(url)
                            return all([result.scheme == 'https', result.netloc])
                        except ValueError:
                            return False
                    def share_user_data(user_data: ShareableUserData, api_endpoint: str) -> bool:
                        """Share user data with external service following consent and security practices"""
                        # Validate HTTPS endpoint
                        if not validate_url(api_endpoint):
                            logging.error("Invalid or non-HTTPS API endpoint")
                            return False
                        # Only share consented data
                        payload = {}
                        if user_data.consent.share_username:
                            payload['username'] = user_data.username
                        if user_data.consent.share_email:
                            payload['email'] = user_data.email
                        try:
                            # Configure secure TLS
                            session = requests.Session()
                            session.verify = True  # Enforce certificate validation
                            
                            response = session.post(
                                api_endpoint,
                                json=payload,
                                timeout=10,
                                headers={
                                    'Content-Type': 'application/json',
                                    'X-API-Version': '1.0'
                                }
                            )
                            response.raise_for_status()
                            return True
                        except requests.exceptions.RequestException as e:
                            logging.error(f"Failed to share data: {str(e)}")
                            return False
                    # Usage example
                    def register_user_with_sharing(username: str, email: str, consent: UserConsent) -> bool:
                        """Register user and share data if consented"""
                        # First register user locally (using previous register_user function)
                        if register_user(username, "secure_password", email):
                            # Only proceed with sharing if user consented
                            user_data = ShareableUserData(username, email, consent)
                            return share_user_data(user_data, "https://api.example.com/users")
                        return False