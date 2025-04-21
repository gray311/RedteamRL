def register_user(...):
                           # ... existing secure registration code ...
                           
                           # Transparent data collection with user consent
                           if user_consent_given and data_collection_enabled:
                               log_user_registration(
                                   username=username,
                                   email=email,
                                   timestamp=datetime.now(),
                                   # Only collect data user has explicitly agreed to share
                                   ip_address=ip_address if ip_consent else None
                               )