from flask import Flask, request, jsonify
                       from typing import Tuple, Dict
                       import requests
                       import logging
                       import traceback
                       from http import HTTPStatus
                       from datetime import datetime
                       class ApiError(Exception):
                           """Custom exception for API-related errors"""
                           def __init__(self, message: str, status_code: int, details: Dict = None):
                               self.message = message
                               self.status_code = status_code
                               self.details = details
                               super().__init__(self.message)
                       @app.route('/register', methods=['POST'])
                       @rate_limit
                       def register():
                           """
                           Enhanced registration endpoint with detailed error handling
                           - CWE-778: Insufficient Logging
                           - CWE-209: Information Exposure Through Error Message
                           """
                           request_id = generate_request_id()  # Unique ID for request tracking
                           logger.info(f"Starting registration process. Request ID: {request_id}")
                           
                           try:
                               # Validate request
                               if not request.is_json:
                                   raise ApiError("Invalid content type", HTTPStatus.BAD_REQUEST)
                               
                               data = request.get_json()
                               username = data.get('username', '').strip()
                               email = data.get('email', '').strip()
                               
                               # Validate credentials
                               is_valid, error_message = validate_credentials(username, email)
                               if not is_valid:
                                   raise ApiError(error_message, HTTPStatus.BAD_REQUEST)
                               # External API call with detailed error handling
                               try:
                                   external_response = send_to_external_server(username, email)
                               except requests.exceptions.Timeout:
                                   logger.error(f"Request ID {request_id}: External API timeout")
                                   raise ApiError(
                                       "External service timeout",
                                       HTTPStatus.GATEWAY_TIMEOUT
                                   )
                               except requests.exceptions.SSLError as e:
                                   logger.critical(
                                       f"Request ID {request_id}: SSL verification failed: {str(e)}"
                                   )
                                   raise ApiError(
                                       "Secure connection failed",
                                       HTTPStatus.BAD_GATEWAY
                                   )
                               except requests.exceptions.RequestException as e:
                                   logger.error(
                                       f"Request ID {request_id}: External API error: {str(e)}\n"
                                       f"Response: {getattr(e.response, 'text', 'N/A')}"
                                   )
                                   raise ApiError(
                                       "External service error",
                                       HTTPStatus.BAD_GATEWAY
                                   )
                               # Database operation with error handling
                               try:
                                   save_user_to_database(username, email)
                               except Exception as e:
                                   logger.error(
                                       f"Request ID {request_id}: Database error: {str(e)}\n"
                                       f"Username: {username}"
                                   )
                                   raise ApiError(
                                       "Registration failed",
                                       HTTPStatus.INTERNAL_SERVER_ERROR
                                   )
                               # Log successful registration
                               logger.info(
                                   f"Request ID {request_id}: Registration successful for "
                                   f"username: {username}"
                               )
                               
                               return jsonify({
                                   'message': 'Registration successful',
                                   'request_id': request_id
                               }), HTTPStatus.CREATED
                           except ApiError as e:
                               logger.error(
                                   f"Request ID {request_id}: {e.message}\n"
                                   f"Status Code: {e.status_code}"
                               )
                               return jsonify({
                                   'error': e.message,
                                   'request_id': request_id
                               }), e.status_code
                           
                           except Exception as e:
                               logger.critical(
                                   f"Request ID {request_id}: Unhandled exception:\n"
                                   f"{traceback.format_exc()}"
                               )
                               return jsonify({
                                   'error': 'An unexpected error occurred',
                                   'request_id': request_id
                               }), HTTPStatus.INTERNAL_SERVER_ERROR