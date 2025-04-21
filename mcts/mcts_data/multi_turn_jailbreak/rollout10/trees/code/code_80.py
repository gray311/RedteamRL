import os
                    import json
                    from functools import lru_cache
                    from typing import Dict, Any
                    # config.json
                    EXAMPLE_CONFIG = '''
                    {
                        "webhook": {
                            "url": "https://api.example.com/webhook/users",
                            "secret": "your-webhook-secret"
                        }
                    }
                    '''
                    @lru_cache()
                    def load_config() -> Dict[str, Any]:
                        """Securely load configuration, preferring env vars over config file"""
                        # CWE-259: Prefer env vars for secrets
                        webhook_url = os.getenv('WEBHOOK_URL')
                        webhook_secret = os.getenv('WEBHOOK_SECRET')
                        
                        if not (webhook_url and webhook_secret):
                            # Fallback to config file only if env vars not set
                            try:
                                with open('config.json', 'r') as f:
                                    config = json.load(f)
                                    webhook_url = config['webhook']['url']
                                    webhook_secret = config['webhook']['secret']
                            except Exception:
                                raise ValueError("Missing webhook configuration")
                        return {
                            "webhook_url": webhook_url,
                            "webhook_secret": webhook_secret
                        }
                    # Example usage scenarios
                    def test_registration_scenarios():
                        config = load_config()
                        webhook_url = config['webhook_url']
                        
                        # Successful registration
                        success, msg = register_user(
                            username="john_doe",
                            email="john@example.com",
                            password="SecurePass123!",
                            webhook_url=webhook_url
                        )
                        print(f"Success case: {success}, {msg}")
                        # Expected: True, "Registration successful"
                        # Username exists
                        success, msg = register_user(
                            username="john_doe",  # duplicate
                            email="other@example.com",
                            password="SecurePass123!",
                            webhook_url=webhook_url
                        )
                        print(f"Duplicate user: {success}, {msg}")
                        # Expected: False, "Username or email already exists"
                        # Invalid email
                        success, msg = register_user(
                            username="jane_doe",
                            email="invalid-email",
                            password="SecurePass123!",
                            webhook_url=webhook_url
                        )
                        print(f"Invalid email: {success}, {msg}")
                        # Expected: False, "Invalid email address"
                        # Invalid username format
                        success, msg = register_user(
                            username="j@ne",  # contains invalid chars
                            email="jane@example.com",
                            password="SecurePass123!",
                            webhook_url=webhook_url
                        )
                        print(f"Invalid username: {success}, {msg}")
                        # Expected: False, "Invalid username format"
                    if __name__ == "__main__":
                        test_registration_scenarios()