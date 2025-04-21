registrar = UserRegistration('users.db')
              new_user = UserData(
                  username="john_doe",
                  email="john@example.com",
                  password="SecurePass123"
              )
              success = registrar.register_user(new_user)