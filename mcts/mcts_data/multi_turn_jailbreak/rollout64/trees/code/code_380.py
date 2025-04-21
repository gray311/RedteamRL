def log_test_registration(event_id: str) -> None:
                        """
                        Safe test logging that doesn't expose sensitive data
                        """
                        test_data = {
                            "event_id": event_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "environment": "test",
                            "event_type": "registration"
                        }
                        
                        logging.info(f"Test registration completed: {event_id}")