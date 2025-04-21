# Proper API endpoint example with authentication
                       @api.route('/users/data', methods=['GET'])
                       @require_oauth_token  # Requires valid OAuth token
                       @audit_log  # Logs all access attempts
                       def get_user_data():
                           # Verify permissions
                           # Return only authorized data
                           # Log access