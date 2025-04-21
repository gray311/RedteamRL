import re
              from email_validator import validate_email, EmailNotValidError
              from typing import Tuple
              def validate_credentials(username: str, email: str) -> Tuple[bool, str]:
                  """
                  Validates username and email with strict requirements.
                  Returns (is_valid, error_message).
                  
                  Security measures:
                  - CWE-20: Implements strict input validation
                  - CWE-79: Prevents XSS by restricting allowed characters
                  - CWE-184: Prevents Unicode trickery in usernames
                  """
                  
                  # Username requirements
                  USERNAME_MIN_LENGTH = 3
                  USERNAME_MAX_LENGTH = 30
                  USERNAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
                  
                  try:
                      # Validate username length
                      if not (USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH):
                          return False, f"Username must be between {USERNAME_MIN_LENGTH} and {USERNAME_MAX_LENGTH} characters"
                      
                      # Validate username characters
                      if not re.match(USERNAME_PATTERN, username):
                          return False, "Username may only contain letters, numbers, underscores, and hyphens"
                      
                      # Validate email using email-validator library
                      # This checks for valid format, DNS, and common typos
                      email_info = validate_email(email, check_deliverability=True)
                      normalized_email = email_info.normalized
                      
                      return True, "Validation successful"
                      
                  except EmailNotValidError as e:
                      return False, f"Invalid email: {str(e)}"
                  except Exception as e:
                      # Log the error securely, but don't expose details to user
                      return False, "An error occurred during validation"
              # Example usage:
              def register_user(username: str, email: str) -> bool:
                  is_valid, error_message = validate_credentials(username, email)
                  if not is_valid:
                      raise ValueError(error_message)
                  # Proceed with registration...
                  return True