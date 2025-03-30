import logging
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MIN_MAGNITUDE

class TelegramNotifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID

    def format_message(self, event):
        """Format earthquake event data into a readable message."""
        magnitude = event['Magnitude']
        thai_location = event['ThaiLocation']
        english_location = event['EnglishLocation']
        depth = event['Depth']
        date_time = event['DateTime']
        utc_time = event['UTCTime']
        lat = event['Latitude']
        lon = event['Longitude']
        phases = event['Phases']
        is_felt = event['IsFelt']

        # Create emoji based on magnitude and felt status
        magnitude_emoji = "🔴" if magnitude >= 6.0 else "🟡" if magnitude >= 5.0 else "🟢"
        felt_emoji = "⚠️" if is_felt else ""

        # Format location
        location = f"{thai_location}\n{english_location}" if english_location else thai_location

        message = (
            f"{magnitude_emoji} {felt_emoji} *New Earthquake Alert!*\n\n"
            f"*Magnitude:* {magnitude:.1f}\n"
            f"*Location:* {location}\n"
            f"*Depth:* {depth:.1f} km\n"
            f"*Time:* {date_time}\n"
            f"*UTC Time:* {utc_time}\n"
            f"*Coordinates:* {lat:.4f}°N, {lon:.4f}°E\n"
            f"*Phases:* {phases}\n\n"
            f"Source: TMD Earthquake Monitoring"
        )
        return message

    async def send_notification(self, event):
        """Send earthquake notification to Telegram."""
        try:
            if event['Magnitude'] >= MIN_MAGNITUDE:
                message = self.format_message(event)
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                self.logger.info(f"Notification sent for earthquake: {event['DateTime']}")
            else:
                self.logger.debug(f"Earthquake below minimum magnitude threshold: {event['Magnitude']}")
        except Exception as e:
            self.logger.error(f"Error sending Telegram notification: {str(e)}") 