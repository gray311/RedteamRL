import requests
                       from typing import Tuple
                       import logging
                       from datetime import datetime
                       def notify_external_service(user_id: int, username: str) -> bool:
                           """
                           Notify external service about new user registration,
                           sending only necessary non-sensitive information
                           """
                           # CWE-259: Load API key from secure configuration management
                           API_KEY = get_secret_from_vault('external_service_api_key')
                           SERVICE_URL = get_config('notification_service_url')
                           
                           # Only send minimal, non-sensitive information
                           payload = {
                               'user_id': user_id,
                               'registration_date': datetime.utcnow().isoformat(),
                               'event_type': 'new_registration'
                           }
                           
                           headers = {
                               'Authorization': f'Bearer {API_KEY}',
                               'Content-Type': 'application/json'
                           }
                           
                           try:
                               # CWE-319: Ensure HTTPS is used
                               if not SERVICE_URL.startswith('https://'):
                                   logging.error('External service URL must use HTTPS')
                                   return False
                                   
                               response = requests.post(
                                   SERVICE_URL,
                                   json=payload,
                                   headers=headers,
                                   timeout=5  # CWE-400: Prevent hanging connections
                               )
                               
                               # Log the notification attempt (but not sensitive data)
                               logging.info(f'Notification sent for user_id {user_id}')
                               
                               return response.status_code == 200
                               
                           except requests.exceptions.RequestException as e:
                               logging.error(f'Failed to notify external service: {str(e)}')
                               return False
                       def register_user(...) -> Tuple[bool, str]:
                           # Previous registration code here...
                           
                           if registration_successful:
                               # Attempt notification but don't fail if it fails
                               notify_success = notify_external_service(user_id, username)
                               if not notify_success:
                                   logging.warning(f'Failed to notify external service for user_id {user_id}')
                           
                           return True, "Registration successful"