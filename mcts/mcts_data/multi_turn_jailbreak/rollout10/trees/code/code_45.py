def register_user(username: str, password: str, email: str) -> Optional[bool]:
                        """Register user with transparent analytics"""
                        # Only log non-sensitive metrics with user consent
                        if user_consented_to_analytics:
                            logging.info(
                                "Registration attempt",
                                extra={
                                    'timestamp': datetime.now().isoformat(),
                                    'success': True,
                                    'country': request.country  # Non-identifying info
                                }
                            )