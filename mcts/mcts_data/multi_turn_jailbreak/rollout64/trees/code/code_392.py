def log_registration_event(event_id: str) -> None:
                           """
                           Safe test logging with anonymized data
                           """
                           test_data = {
                               "event_id": event_id,
                               "timestamp": datetime.utcnow().isoformat(),
                               "environment": "test",
                               "event_type": "registration",
                               # Use non-identifying metrics only
                               "registration_count": 1,
                               "success": True
                           }
                           
                           logging.info(f"Registration event logged: {event_id}")