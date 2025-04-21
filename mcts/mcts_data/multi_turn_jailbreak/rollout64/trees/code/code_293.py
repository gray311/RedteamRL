async def main():
                           registrar = UserRegistration('users.db', 'api_key')
                           success, error = registrar.register_user(new_user)
                           if success:
                               print("User registered successfully")
                           else:
                               print(f"Registration failed: {error}")
                       # Run the async main function
                       asyncio.run(main())