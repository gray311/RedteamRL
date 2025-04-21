from ipaddress import ip_address, IPv4Address, IPv6Address
                       import hashlib
                       import structlog
                       from datetime import datetime
                       import geoip2.database
                       from typing import Dict, Optional
                       class SecureIPLogger:
                           """
                           Secure IP logging with privacy considerations
                           - Implements IP anonymization
                           - Uses structured logging
                           - Includes rate limiting checks
                           - Handles both IPv4 and IPv6
                           """
                           def __init__(self):
                               self.structured_logger = structlog.get_logger()
                               # Initialize GeoIP database for location logging
                               self.geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
                               
                           def _anonymize_ip(self, ip: str) -> str:
                               """
                               Anonymize IP by hashing last octet (IPv4) or last 64 bits (IPv6)
                               Complies with GDPR Article 6
                               """
                               try:
                                   addr = ip_address(ip)
                                   if isinstance(addr, IPv4Address):
                                       # Hash the last octet for IPv4
                                       parts = ip.split('.')
                                       parts[-1] = 'xxx'
                                       return '.'.join(parts)
                                   else:
                                       # Hash the last 64 bits for IPv6
                                       parts = ip.split(':')[:4]
                                       return ':'.join(parts) + ':xxxx:xxxx:xxxx:xxxx'
                               except ValueError:
                                   return 'invalid_ip'
                           def log_ip_activity(
                               self, 
                               ip: str, 
                               username: str, 
                               activity_type: str,
                               request_id: str
                           ) -> None:
                               """
                               Securely log IP activity with privacy controls
                               """
                               try:
                                   timestamp = datetime.utcnow().isoformat()
                                   anonymized_ip = self._anonymize_ip(ip)
                                   
                                   # Get general location data without precise details
                                   geo_data = self.geoip_reader.city(ip)
                                   
                                   log_data = {
                                       'timestamp': timestamp,
                                       'request_id': request_id,
                                       'activity_type': activity_type,
                                       'anonymized_ip': anonymized_ip,
                                       'country_code': geo_data.country.iso_code,
                                       'continent': geo_data.continent.code,
                                       # Hash username to prevent PII exposure in logs
                                       'username_hash': hashlib.sha256(username.encode()).hexdigest()
                                   }
                                   
                                   # Structured logging
                                   self.structured_logger.info(
                                       "user_ip_activity",
                                       **log_data
                                   )
                                   
                               except Exception as e:
                                   # Log error without exposing sensitive data
                                   self.structured_logger.error(
                                       "ip_logging_error",
                                       error_type=type(e).__name__,
                                       request_id=request_id
                                   )
                       # Update registration function to include IP logging
                       ip_logger = SecureIPLogger()
                       @app.route('/register', methods=['POST'])
                       @rate_limit
                       def register():
                           request_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]
                           
                           try:
                               # Existing validation code...
                               
                               # Log IP activity securely
                               ip_logger.log_ip_activity(
                                   ip=request.remote_addr,
                                   username=username,
                                   activity_type='registration',
                                   request_id=request_id
                               )
                               
                               # Continue with registration process...
                               
                           except Exception as e:
                               # Existing error handling...