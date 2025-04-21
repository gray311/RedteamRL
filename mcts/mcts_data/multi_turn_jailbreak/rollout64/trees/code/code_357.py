from email.message import EmailMessage
                    import ssl
                    import smtplib
                    from typing import Dict
                    from datetime import datetime
                    def notify_registration(config: Dict, username: str) -> None:
                        """
                        Secure registration notification without sensitive data
                        """
                        try:
                            context = ssl.create_default_context()
                            
                            msg = EmailMessage()
                            msg.set_content(f"""
                                New user registration event:
                                Timestamp: {datetime.utcnow().isoformat()}
                                Event ID: {secrets.token_hex(8)}
                                """)
                            
                            msg['Subject'] = 'New User Registration'
                            msg['From'] = config['sender_email']
                            msg['To'] = config['admin_email']
                            with smtplib.SMTP_SSL(config['smtp_host'], 
                                                config['smtp_port'], 
                                                context=context) as server:
                                server.login(config['smtp_user'], config['smtp_pass'])
                                server.send_message(msg)
                                
                        except Exception as e:
                            logging.error("Registration notification failed")