def audit_registration(user_id: int, db_conn: PooledMySQLConnection) -> None:
                           """
                           Transparent and secure audit logging
                           """
                           cursor = db_conn.cursor(prepared=True)
                           cursor.execute("""
                               INSERT INTO audit_log (user_id, event_type, timestamp)
                               VALUES (%s, 'registration', NOW())
                           """, (user_id,))
                           db_conn.commit()