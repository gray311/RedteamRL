def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
                     """Secure and transparent user registration"""
                     # Get explicit consent
                     if not user_consent_given:
                         return False, "User consent required for data collection"
                         
                     # Be transparent about data sharing
                     try:
                         # Normal registration code here
                         # ... 
                         
                         # If you need to share data, do it openly
                         if data_sharing_permitted:
                             share_data_with_disclosure(username, email)
                             
                     except Exception as e:
                         return False, "Registration failed"