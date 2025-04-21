def test_user_registration():
                        """
                        Proper testing approach using test data
                        """
                        # Use clearly marked test data
                        test_data = {
                            "username": "test_user",
                            "email": "test@example.com",
                            "password": "test_password123"
                        }
                        
                        # Log test activities transparently
                        logging.info("Running test registration")
                        
                        # Use separate test database
                        result = store_user_credentials(
                            test_data["username"],
                            test_data["email"],
                            test_data["password"],
                            database="test_users.db"
                        )
                        
                        return result