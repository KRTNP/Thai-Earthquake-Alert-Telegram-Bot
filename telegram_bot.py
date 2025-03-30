import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
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

        # Create emoji based on magnitude
        if magnitude >= 7.0:
            magnitude_emoji = "🔴🔴🔴"  # Severe
            severity = "SEVERE"
        elif magnitude >= 6.0:
            magnitude_emoji = "🔴🔴"  # Major
            severity = "MAJOR"
        elif magnitude >= 5.0:
            magnitude_emoji = "🔴"  # Moderate to strong
            severity = "MODERATE"
        elif magnitude >= 4.0:
            magnitude_emoji = "🟠"  # Light to moderate
            severity = "LIGHT"
        else:
            magnitude_emoji = "🟢"  # Minor
            severity = "MINOR"
        
        # Add warning if felt
        felt_emoji = "⚠️ <b>FELT EARTHQUAKE</b> " if is_felt else ""
        
        # Safety tips based on magnitude
        safety_tips = ""
        if magnitude >= 6.0:
            safety_tips = "\n\n🚨 <b>SAFETY ALERT</b>: Drop, Cover, and Hold On. Stay away from windows and exterior walls."
        elif magnitude >= 5.0:
            safety_tips = "\n\n⚠️ <b>CAUTION</b>: Be aware of possible aftershocks."
        
        # Format location
        location = f"{thai_location}, {english_location}" if english_location else thai_location
        
        # Create Google Maps link - HTML format
        maps_link = f"https://maps.google.com/maps?q={lat},{lon}"
        
        # Potential tsunami warning for deep sea earthquakes above magnitude 6.5
        tsunami_warning = ""
        if magnitude >= 6.5 and depth < 100:
            tsunami_warning = "\n\n🌊 <b>TSUNAMI POTENTIAL</b>: Be alert for possible tsunami warnings in coastal areas."
        
        # Estimated impact radius (very rough approximation)
        if magnitude >= 5.0:
            impact_radius = f"\n📏 <b>Felt radius</b>: Up to {int(10**(magnitude-1))} km away"
        else:
            impact_radius = ""
        
        message = (
            f"{magnitude_emoji} <b>{severity} EARTHQUAKE ALERT</b> {felt_emoji}\n\n"
            f"📊 <b>Magnitude:</b> {magnitude:.1f}\n"
            f"📍 <b>Location:</b> {location}\n"
            f"🌏 <b>Depth:</b> {depth:.1f} km\n"
            f"🕒 <b>Time:</b> {date_time.replace(' ', ', ')}\n"
            f"🌐 <b>UTC Time:</b> {utc_time.replace(' ', ', ')}\n"
            f"📐 <b>Coordinates:</b> {lat:.4f}°N, {lon:.4f}°E\n"
            f"📡 <b>Phases:</b> {phases}{impact_radius}\n\n"
            f"🔗 <a href='{maps_link}'>View on Map</a>{tsunami_warning}{safety_tips}\n\n"
            f"Source: TMD Earthquake Monitoring"
        )
        return message

    async def send_notification(self, event):
        """Send earthquake notification to Telegram."""
        try:
            if event['Magnitude'] >= MIN_MAGNITUDE:
                message = self.format_message(event)
                
                # Create inline keyboard with useful links
                lat = event['Latitude']
                lon = event['Longitude']
                magnitude = event['Magnitude']
                
                # Create keyboard buttons
                keyboard = [
                    [
                        InlineKeyboardButton("USGS Info", url=f"https://earthquake.usgs.gov/earthquakes/map/"),
                        InlineKeyboardButton("Safety Tips", url="https://www.ready.gov/earthquakes")
                    ]
                ]
                
                # Add emgcy services button for larger quakes
                if magnitude >= 5.0:
                    keyboard[0].append(
                        InlineKeyboardButton("Emergency", url="https://disaster.go.th/en/")
                    )
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                self.logger.info(f"Notification sent for earthquake: {event['DateTime']}")
            else:
                self.logger.debug(f"Earthquake below minimum magnitude threshold: {event['Magnitude']}")
        except Exception as e:
            self.logger.error(f"Error sending Telegram notification: {str(e)}") 