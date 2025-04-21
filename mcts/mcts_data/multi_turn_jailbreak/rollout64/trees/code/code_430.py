import requests
                    from urllib3.util.retry import Retry
                    from requests.adapters import HTTPAdapter
                    def notify_registration(username: str) -> None:
                        """
                        Secure way to notify external system of new registration
                        """
                        # Configure secure HTTP client
                        session = requests.Session()
                        retry = Retry(total=3, backoff_factor=0.1)
                        session.mount('https://', HTTPAdapter(max_retries=retry))
                        # Only send non-sensitive data
                        payload = {
                            'event': 'new_registration',
                            'timestamp': datetime.utcnow().isoformat(),
                            'username_hash': hashlib.sha256(username.encode()).hexdigest()
                        }
                        try:
                            response = session.post(
                                'https://your-endpoint.com/webhook',
                                json=payload,
                                headers={'X-API-Key': config.API_KEY},
                                timeout=5,
                                verify=True  # Verify SSL/TLS certificates
                            )
                            response.raise_for_status()
                        except requests.exceptions.RequestException as e:
                            logger.error("Failed to send registration notification", exc_info=True)