import re
              from email_validator import validate_email, EmailNotValidError
              from typing import Tuple
              def validate_credentials(username: str, email: str) -> Tuple[bool, str]:
                  """
                  Validates username and email with strict requirements.
                  Returns (is_valid, error_message).
                  """
                  # Validate username: 3-20 chars, alphanumeric and underscore only
                  # Prevents CWE-20: Improper Input Validation
                  username_pattern = r'^[a-zA-Z0-9_]{3,20}$'
                  if not re.match(username_pattern, username):
                      return False, "Username must be 3-20 characters, alphanumeric and underscore only"
                  
                  # Validate email using comprehensive validation library
                  # Prevents malformed emails and domain validation issues
                  try:
                      # Normalize and validate email
                      valid_email = validate_email(email, check_deliverability=True)
                      normalized_email = valid_email.normalized
                  except EmailNotValidError as e:
                      return False, f"Invalid email: {str(e)}"
                  return True, "Validation successful"
              # Example usage:
              def register_user(username: str, email: str) -> None:
                  # Sanitize inputs by stripping whitespace
                  username = username.strip()
                  email = email.strip()
                  
                  # Validate credentials
                  is_valid, message = validate_credentials(username, email)
                  if not is_valid:
                      raise ValueError(message)
                  
                  # Proceed with registration...