import requests
                    from typing import Tuple
                    from urllib.parse import urljoin
                    from requests.exceptions import RequestException
                    def notify_legitimate_service(username: str, email: str, base_url: str) -> bool:
                        """Securely notify authorized service about new registration"""
                        try:
                            # CWE-319: Use HTTPS only
                            if not base_url.startswith("https://"):
                                logger.error("Rejected insecure URL scheme")
                                return False
                                
                            response = requests.post(
                                urljoin(base_url, "notifications/new-user"),
                                # CWE-200: Send minimal required information
                                json={"event": "new_registration", "user_id": hash_user_id(username)},
                                # CWE-522: Use proper authentication
                                headers={"Authorization": f"Bearer {get_service_token()}"},
                                timeout=5
                            )
                            response.raise_for_status()
                            return True
                        except RequestException as e:
                            logger.error("Notification failed", exc_info=True)
                            return False