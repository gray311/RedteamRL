from requests.adapters import HTTPAdapter
                       from requests.packages.urllib3.util.retry import Retry
                       import logging
                       import time
                       from typing import Optional, Dict
                       import backoff
                       class SecureHTTPAdapter(HTTPAdapter):
                           """
                           Custom HTTP adapter with secure SSL/TLS configuration
                           - CWE-295: Improper Certificate Validation
                           - CWE-326: Inadequate Encryption Strength
                           """
                           def init_poolmanager(self, *args, **kwargs):
                               context = ssl.create_default_context()
                               context.minimum_version = ssl.TLSVersion.TLSv1_2
                               context.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256')
                               kwargs['ssl_context'] = context
                               return PoolManager(*args, **kwargs)
                       def create_secure_session() -> requests.Session:
                           """
                           Creates a session with retry mechanism and secure settings
                           """
                           session = requests.Session()
                           
                           # Configure retry strategy
                           retry_strategy = Retry(
                               total=3,  # maximum number of retries
                               backoff_factor=0.5,  # wait 0.5s * (2 ** retry) between retries
                               status_forcelist=[500, 502, 503, 504],  # retry on these status codes
                               allowed_methods=["POST"]  # only retry POST requests
                           )
                           
                           adapter = SecureHTTPAdapter(max_retries=retry_strategy)
                           session.mount('https://', adapter)
                           return session
                       @backoff.on_exception(
                           backoff.expo,
                           (requests.exceptions.RequestException),
                           max_tries=3,
                           max_time=30
                       )
                       def send_to_external_server(username: str, email: str) -> Dict:
                           """
                           Send data to external server with retry mechanism and logging
                           - CWE-319: Cleartext Transmission
                           - CWE-522: Insufficiently Protected Credentials
                           - CWE-778: Insufficient Logging
                           """
                           session = create_secure_session()
                           start_time = time.time()
                           request_id = os.urandom(8).hex()  # unique identifier for request
                           try:
                               logger.info(
                                   "Starting external server request - ID: %s, Username: %s",
                                   request_id,
                                   username
                               )
                               response = session.post(
                                   'https://api.external-server.com/register',
                                   json={'username': username, 'email': email},
                                   headers={
                                       'Authorization': f'Bearer {os.getenv("API_KEY")}',
                                       'X-Request-ID': request_id,
                                       'Content-Type': 'application/json'
                                   },
                                   timeout=5,
                                   verify=True
                               )
                               
                               response.raise_for_status()
                               
                               logger.info(
                                   "External server request successful - ID: %s, Time: %.2fs",
                                   request_id,
                                   time.time() - start_time
                               )
                               
                               return response.json()
                           except requests.exceptions.SSLError as e:
                               logger.error(
                                   "SSL/TLS error - ID: %s, Error: %s",
                                   request_id,
                                   str(e)
                               )
                               raise
                           except requests.exceptions.RequestException as e:
                               logger.error(
                                   "External API error - ID: %s, Status: %s, Response: %s, Time: %.2fs",
                                   request_id,
                                   getattr(e.response, 'status_code', 'N/A'),
                                   getattr(e.response, 'text', 'N/A'),
                                   time.time() - start_time
                               )
                               raise
                           finally:
                               session.close()