import requests
                 from typing import Dict
                 import logging
                 from json import dumps
                 def log_registration(user_data: Dict[str, str], log_server_url: str) -> None:
                     """
                     Securely log user registration with minimal identifiable information
                     """
                     try:
                         # Only log non-sensitive data
                         safe_log_data = {
                             "timestamp": datetime.utcnow().isoformat(),
                             "event_type": "user_registration",
                             "username_hash": hashlib.sha256(user_data['username'].encode()).hexdigest()[:8],
                             "success": True
                         }
                         # CWE-319: Ensure HTTPS is used
                         if not log_server_url.startswith("https://"):
                             raise ValueError("Secure HTTPS connection required")
                         response = requests.post(
                             log_server_url,
                             json=safe_log_data,
                             headers={"Content-Type": "application/json"},
                             timeout=5
                         )
                         response.raise_for_status()
                     except Exception as e:
                         # Fail safely - don't block registration if logging fails
                         logging.error(f"Registration logging failed: {str(e)}")