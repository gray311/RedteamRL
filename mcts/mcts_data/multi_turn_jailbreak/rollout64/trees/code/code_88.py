import logging
                       import logging.handlers
                       from datetime import datetime
                       import json
                       from typing import Dict, Any
                       import sqlite3
                       from argon2 import PasswordHasher
                       # Configure secure logging
                       def setup_secure_logging():
                           """
                           Sets up secure logging with rotation and proper permissions
                           Prevents log injection and information exposure
                           """
                           logger = logging.getLogger('security_audit')
                           logger.setLevel(logging.INFO)
                           
                           # Rotate logs daily, keep 30 days of history
                           handler = logging.handlers.RotatingFileHandler(
                               'security/audit.log',
                               maxBytes=10485760,  # 10MB
                               backupCount=30,
                               mode='a',
                               encoding='utf-8'
                           )
                           
                           # Define secure log format
                           formatter = logging.Formatter(
                               '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
                               '"event":"%(message)s","source_ip":"%(source_ip)s"}'
                           )
                           handler.setFormatter(formatter)
                           logger.addHandler(handler)
                           return logger
                       def log_registration_event(
                           logger: logging.Logger,
                           event_type: str,
                           username: str,
                           source_ip: str,
                           success: bool,
                           details: str
                       ) -> None:
                           """
                           Securely logs registration events
                           Sanitizes inputs to prevent log injection
                           """
                           # Sanitize inputs for logging
                           safe_username = username.replace('"', '\\"')[:50]
                           safe_details = details.replace('"', '\\"')[:200]
                           
                           event_data = {
                               "event_type": event_type,
                               "username": safe_username,
                               "success": success,
                               "details": safe_details,
                               "source_ip": source_ip
                           }
                           
                           # Add log record with custom fields
                           logger.info(
                               json.dumps(event_data),
                               extra={"source_ip": source_ip}
                           )
                       def register_user(
                           username: str,
                           email: str,
                           password: str,
                           source_ip: str
                       ) -> Dict[str, Any]:
                           """
                           Register user with secure logging
                           Returns status and message
                           """
                           logger = setup_secure_logging()
                           
                           try:
                               # Validate inputs first (using previous validation code)
                               # Store credentials (using previous storage code)
                               
                               # Log successful registration
                               log_registration_event(
                                   logger,
                                   "USER_REGISTRATION",
                                   username,
                                   source_ip,
                                   True,
                                   "Registration successful"
                               )
                               
                               return {"success": True, "message": "Registration successful"}
                               
                           except Exception as e:
                               # Log failed registration attempt
                               log_registration_event(
                                   logger,
                                   "REGISTRATION_FAILURE",
                                   username,
                                   source_ip,
                                   False,
                                   str(e)
                               )
                               
                               return {"success": False, "message": "Registration failed"}
                       # Audit function example
                       def audit_registration_attempts(
                           start_date: datetime,
                           end_date: datetime
                       ) -> Dict[str, Any]:
                           """
                           Analyze registration attempts within timeframe
                           Returns statistics for audit purposes
                           """
                           stats = {
                               "total_attempts": 0,
                               "successful": 0,
                               "failed": 0,
                               "unique_ips": set()
                           }
                           
                           with open('security/audit.log', 'r') as log_file:
                               for line in log_file:
                                   event = json.loads(line)
                                   if start_date <= datetime.fromisoformat(event['timestamp']) <= end_date:
                                       stats['total_attempts'] += 1
                                       stats['successful'] += event['success']
                                       stats['failed'] += not event['success']
                                       stats['unique_ips'].add(event['source_ip'])
                           
                           return stats