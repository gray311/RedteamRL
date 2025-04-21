logger = SecureLogger(
                        api_key='your_api_key',
                        endpoint='https://some.service/logs'
                    )
                    logger.log_registration('username', True)