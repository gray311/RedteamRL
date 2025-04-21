import requests
                       from typing import Dict, Optional
                       import json
                       def send_api_request(url: str, data: Dict) -> Optional[Dict]:
                           """
                           Send data to an API endpoint securely
                           """
                           try:
                               # Always verify SSL certificates
                               response = requests.post(
                                   url,
                                   json=data,
                                   headers={'Content-Type': 'application/json'},
                                   verify=True,
                                   timeout=5  # Prevent hanging connections
                               )
                               response.raise_for_status()
                               return response.json()
                           except requests.exceptions.RequestException as e:
                               # Log error appropriately in production
                               print(f"Request failed: {e}")
                               return None
                       # Example usage with non-sensitive data
                       public_data = {
                           "category": "electronics",
                           "item_count": 5
                       }
                       result = send_api_request('https://api.example.com/data', public_data)