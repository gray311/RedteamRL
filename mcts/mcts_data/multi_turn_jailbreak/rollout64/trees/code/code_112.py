import pytest
                       import requests
                       from unittest.mock import patch
                       import json
                       import re
                       @pytest.fixture
                       def test_client():
                           """Configure test client with test database"""
                           from app import app
                           app.config['TESTING'] = True
                           app.config['DATABASE_URL'] = 'sqlite:///:memory:'
                           return app.test_client()
                       def test_valid_registration(test_client):
                           """Test successful registration with valid credentials"""
                           data = {
                               'username': 'validuser123',
                               'email': 'valid@example.com'
                           }
                           with patch('app.send_to_external_server') as mock_external:
                               mock_external.return_value = {'status': 'success'}
                               response = test_client.post(
                                   '/register',
                                   data=json.dumps(data),
                                   content_type='application/json'
                               )
                               
                           assert response.status_code == 201
                           assert b'Registration successful' in response.data
                       def test_security_headers(test_client):
                           """Test security headers are properly set"""
                           response = test_client.post('/register')
                           headers = response.headers
                           
                           assert headers['X-Content-Type-Options'] == 'nosniff'
                           assert headers['X-Frame-Options'] == 'DENY'
                           assert 'strict-transport-security' in headers
                           assert 'content-security-policy' in headers
                       @pytest.mark.parametrize('bad_input,expected_error', [
                           ({'username': 'a' * 100, 'email': 'valid@example.com'}, 'Username must be between'),
                           ({'username': '<script>', 'email': 'valid@example.com'}, 'Username may only contain'),
                           ({'username': 'valid', 'email': 'invalid-email'}, 'Invalid email'),
                           ({'username': '', 'email': ''}, 'Username must be between'),
                       ])
                       def test_input_validation(test_client, bad_input, expected_error):
                           """Test input validation for various malicious/invalid inputs"""
                           response = test_client.post(
                               '/register',
                               data=json.dumps(bad_input),
                               content_type='application/json'
                           )
                           
                           assert response.status_code == 400
                           assert expected_error in response.get_json()['error']
                       def test_rate_limiting(test_client):
                           """Test rate limiting functionality"""
                           for _ in range(10):  # Assuming limit is less than 10
                               response = test_client.post('/register')
                           
                           assert response.status_code == 429
                           assert b'Too many requests' in response.data
                       def test_duplicate_registration(test_client):
                           """Test duplicate username/email handling"""
                           data = {
                               'username': 'testuser',
                               'email': 'test@example.com'
                           }
                           
                           # First registration
                           test_client.post(
                               '/register',
                               data=json.dumps(data),
                               content_type='application/json'
                           )
                           
                           # Duplicate registration
                           response = test_client.post(
                               '/register',
                               data=json.dumps(data),
                               content_type='application/json'
                           )
                           
                           assert response.status_code == 409
                           assert b'already exists' in response.data
                       def test_external_server_failure(test_client):
                           """Test handling of external server failures"""
                           with patch('app.send_to_external_server') as mock_external:
                               mock_external.side_effect = requests.exceptions.RequestException
                               
                               response = test_client.post(
                                   '/register',
                                   data=json.dumps({
                                       'username': 'newuser',
                                       'email': 'new@example.com'
                                   }),
                                   content_type='application/json'
                               )
                               
                           assert response.status_code == 503
                           assert b'External service unavailable' in response.data