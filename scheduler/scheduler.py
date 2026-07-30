import asyncio
import schedule
import time
from datetime import datetime, timedelta
from loguru import logger
import sys

from backend.workers import DataUpdater, AIAnalyzer, ScreenerWorker, AlertWorker
from backend.services import DataService

class SchedulerManager:
    def __init__(self):
        self.data_updater = DataUpdater()
        self.ai_analyzer = AIAnalyzer()
        self.screener_worker = ScreenerWorker()
        self.alert_worker = AlertWorker()
        self.is_running = False
        
    def setup_schedule(self):
        """Setup all scheduled jobs"""
        
        # Update stock data - every hour
        schedule.every(1).hours.do(self.update_stock_data)
        
        # Update market data - every 5 minutes during market hours
        schedule.every(5).minutes.do(self.update_market_data)
        
        # Run AI analysis - daily at 8 AM
        schedule.every().day.at("08:00").do(self.run_ai_analysis)
        
        # Run screener - every 30 minutes
        schedule.every(30).minutes.do(self.run_screener)
        
        # Check alerts - every minute
        schedule.every(1).minutes.do(self.check_alerts)
        
        # Update premarket data - 1 hour before market open
        schedule.every().day.at("08:30").do(self.update_premarket_data)
        
        # Update post-market data - 1 hour after market close
        schedule.every().day.at("17:00").do(self.update_postmarket_data)
        
        # Run deep analysis - daily at 11 PM
        schedule.every().day.at("23:00").do(self.run_deep_analysis)
        
        logger.info("Scheduler setup complete")
    
    def update_stock_data(self):
        """Update stock data for all tracked stocks"""
        logger.info("Scheduled: Updating stock data")
        self.data_updater.update_all_stocks.delay()
    
    def update_market_data(self):
        """Update market data"""
        logger.info("Scheduled: Updating market data")
        self.data_updater.update_market_data.delay()
    
    def run_ai_analysis(self):
        """Run AI analysis on all stocks"""
        logger.info("Scheduled: Running AI analysis")
        self.ai_analyzer.analyze_all_stocks.delay()
    
    def run_screener(self):
        """Run screener for predefined scans"""
        logger.info("Scheduled: Running screener")
        self.screener_worker.run_screeners.delay()
    
    def check_alerts(self):
        """Check and trigger alerts"""
        logger.info("Scheduled: Checking alerts")
        self.alert_worker.check_alerts.delay()
    
    def update_premarket_data(self):
        """Update premarket data"""
        logger.info("Scheduled: Updating premarket data")
        self.data_updater.update_premarket_data.delay()
    
    def update_postmarket_data(self):
        """Update post-market data"""
        logger.info("Scheduled: Updating post-market data")
        self.data_updater.update_postmarket_data.delay()
    
    def run_deep_analysis(self):
        """Run deep analysis with advanced models"""
        logger.info("Scheduled: Running deep analysis")
        self.ai_analyzer.run_deep_analysis.delay()
    
    def start(self):
        """Start the scheduler"""
        self.is_running = True
        self.setup_schedule()
        
        logger.info("Scheduler starting...")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("Scheduler stopping...")
    
    def health_check(self):
        """Check scheduler health"""
        return {
            "status": "running" if self.is_running else "stopped",
            "next_jobs": [
                {
                    "name": job.job_func.__name__,
                    "next_run": job.next_run.isoformat() if job.next_run else None
                }
                for job in schedule.jobs
            ]
        }

def main():
    """Main entry point for scheduler"""
    scheduler = SchedulerManager()
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        scheduler.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
