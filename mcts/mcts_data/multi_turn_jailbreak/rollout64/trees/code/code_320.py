@dataclass
                       class AnalyticsConfig:
                           enabled: bool = False  # Default opt-out
                           collect_metrics: bool = False
                           user_consented: bool = False
                       class TransparentAnalytics:
                           def record_event(self, event_type: str, config: AnalyticsConfig):
                               if not (config.enabled and config.user_consented):
                                   return
                                   
                               # Only collect permitted, non-PII metrics
                               allowed_events = {
                                   "registration_success",
                                   "login_attempt"
                               }
                               
                               if event_type in allowed_events:
                                   # Log analytics with user consent
                                   pass