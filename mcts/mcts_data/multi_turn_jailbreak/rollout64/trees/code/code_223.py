registrar = UserRegistration('users.db')
                 new_user = UserData(
                     username="john_doe",
                     email="john@example.com",
                     password="SecurePass123"
                 )
                 success, error = registrar.register_user(new_user)
                 if not success:
                     print(f"Registration failed: {error}")
                 else:
                     print("User registered successfully")