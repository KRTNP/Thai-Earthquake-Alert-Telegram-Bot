import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Scraping Configuration
EARTHQUAKE_URL = "https://earthquake.tmd.go.th/inside.html"
SCRAPING_INTERVAL = 300  # 5 minutes in seconds

# Earthquake Filter Configuration
MIN_MAGNITUDE = 3.0  # Minimum magnitude to trigger notification

# Logging Configuration
LOG_FILE = "earthquake_bot.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Data Storage
LAST_EVENT_FILE = "last_event.json" 