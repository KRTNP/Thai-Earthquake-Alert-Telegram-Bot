import asyncio
import logging
import schedule
import time
from config import LOG_FILE, LOG_FORMAT, SCRAPING_INTERVAL
from scraper import EarthquakeScraper
from telegram_bot import TelegramNotifier

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format=LOG_FORMAT
)
# Add console logging for debugging
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

class EarthquakeMonitor:
    def __init__(self):
        self.scraper = EarthquakeScraper()
        self.notifier = TelegramNotifier()

    async def check_earthquakes(self):
        """Check for new earthquakes and send notifications."""
        try:
            logger.info("Starting earthquake data check")
            event = self.scraper.scrape_earthquake_data()
            
            if event:
                logger.info(f"New earthquake detected: Magnitude {event['Magnitude']} at {event['DateTime']}")
                await self.notifier.send_notification(event)
            else:
                logger.info("No new earthquakes detected")
                
        except Exception as e:
            logger.error(f"Error in check_earthquakes: {str(e)}")

def run_async_check():
    """Wrapper function to run the async check_earthquakes function."""
    monitor = EarthquakeMonitor()
    asyncio.run(monitor.check_earthquakes())

def main():
    """Main function to run the earthquake monitoring system."""
    logger.info("Starting Earthquake Monitoring System")
    logger.info(f"Configured to check every {SCRAPING_INTERVAL} seconds")
    
    # Schedule the earthquake check
    schedule.every(SCRAPING_INTERVAL).seconds.do(run_async_check)
    
    # Run the initial check
    logger.info("Running initial check")
    run_async_check()
    
    # Keep the script running
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Earthquake Monitoring System")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main() 