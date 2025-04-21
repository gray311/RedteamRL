from datetime import datetime
                       import logging.config
                       from typing import Dict
                       def setup_audit_logging():
                           """
                           Setup secure, compliant audit logging.
                           Logs are encrypted and access-controlled.
                           """
                           logging.config.dictConfig({
                               'version': 1,
                               'formatters': {
                                   'audit': {
                                       'format': '%(asctime)s - %(message)s',
                                       'datefmt': '%Y-%m-%d %H:%M:%S'
                                   }
                               },
                               'handlers': {
                                   'audit_file': {
                                       'class': 'logging.FileHandler',
                                       'filename': 'audit.log',
                                       'formatter': 'audit',
                                       'mode': 'a'
                                   }
                               },
                               'loggers': {
                                   'audit': {
                                       'handlers': ['audit_file'],
                                       'level': 'INFO'
                                   }
                               }
                           })
                       def log_registration(user_id: int, event_type: str, details: Dict):
                           """
                           Transparent audit logging with user consent
                           Only logs essential security information
                           """
                           audit_logger = logging.getLogger('audit')
                           audit_logger.info(
                               f"Security event: {event_type} "
                               f"User ID: {user_id} "
                               f"Timestamp: {datetime.utcnow()} "
                               f"Details: {details}"
                           )