"""
Main scheduler for WhatsApp insights delivery
"""
import schedule
import time
from loguru import logger
from datetime import datetime

from src.config import settings
from src.firebase_manager import FirebaseManager
from src.whatsapp_sender import WhatsAppSender
from src.insight_generator import InsightGenerator
from src.utils import format_insight_message, setup_logging


class InsightsScheduler:
    """Orchestrate the insight generation and delivery process"""
    
    def __init__(self, use_mock_data: bool = False):
        """
        Initialize scheduler with all components
        
        Args:
            use_mock_data: If True, use mock insights instead of querying database
        """
        setup_logging(settings.log_level)
        
        self.use_mock_data = use_mock_data
        self.firebase = FirebaseManager()
        self.whatsapp = WhatsAppSender()
        self.insights_gen = InsightGenerator()
        
        logger.info("Insights Scheduler initialized")
    
    def send_insights_to_all_users(self):
        """
        Main job: Generate and send insights to all active users
        """
        logger.info("=" * 60)
        logger.info(f"Starting insights delivery job at {datetime.now()}")
        logger.info("=" * 60)
        
        try:
            # Get all active users
            users = self.firebase.get_all_active_users()
            logger.info(f"Found {len(users)} active users")
            
            success_count = 0
            fail_count = 0
            
            for user in users:
                try:
                    # Generate insights
                    if self.use_mock_data:
                        insights = self.insights_gen.generate_mock_insights()
                    else:
                        insights = self.insights_gen.generate_insights_for_user(user.get('user_id', 'default'))
                    
                    # Save insights to Firebase
                    self.firebase.save_insights(user['id'], insights)
                    
                    # Format message
                    message = format_insight_message(insights, user['name'])
                    
                    # Send via WhatsApp
                    self.whatsapp.send_text_message(user['phone'], message)
                    
                    # Update last_sent timestamp
                    self.firebase.update_user_last_sent(user['id'])
                    
                    success_count += 1
                    logger.success(f"✅ Sent insights to {user['name']} ({user['phone']})")
                    
                    # Small delay to avoid rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    fail_count += 1
                    logger.error(f"❌ Failed to send to {user.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.info("=" * 60)
            logger.info(f"Insights delivery complete: {success_count} sent, {fail_count} failed")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Critical error in insights delivery: {e}")
            raise
    
    def run_once(self):
        """Run the job once (for testing)"""
        logger.info("Running job once (manual trigger)")
        self.send_insights_to_all_users()
    
    def start_scheduled_job(self):
        """Start the scheduled job based on cron schedule"""
        logger.info(f"Scheduling insights delivery: {settings.insights_schedule}")
        
        # Parse cron schedule (simplified - using weekly for now)
        # For production, use APScheduler with full cron support
        schedule.every().monday.at("09:00").do(self.send_insights_to_all_users)
        
        logger.info("Scheduler started. Waiting for scheduled time...")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.insights_gen.close()


def main():
    """Main entry point"""
    import sys
    
    # Check if running in test mode
    use_mock = '--mock' in sys.argv or '--test' in sys.argv
    run_once = '--once' in sys.argv
    
    scheduler = InsightsScheduler(use_mock_data=use_mock)
    
    if run_once:
        # Run immediately once
        scheduler.run_once()
    else:
        # Start scheduled job
        scheduler.start_scheduled_job()


if __name__ == "__main__":
    print("""
    PE WhatsApp Insights Scheduler
    ==============================
    
    Usage:
      python -m src.scheduler              # Start scheduled job
      python -m src.scheduler --once       # Run once immediately
      python -m src.scheduler --once --mock  # Run once with mock data
    
    """)
    
    main()
