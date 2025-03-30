# Thai Earthquake Alert Telegram Bot

A real-time monitoring system that tracks earthquake events from the Thai Meteorological Department (TMD) website and delivers instant notifications via Telegram.

## Features

- Automatically scrapes earthquake data from TMD website
- Sends immediate Telegram notifications for new earthquake events
- Configurable magnitude threshold for alerts
- Includes comprehensive earthquake details (magnitude, location, depth, coordinates)
- Supports both Thai and English location information
- Special visual indicators for felt earthquakes
- Detailed logging system
- Customizable monitoring intervals

## Requirements

- Python 3.8+
- Telegram bot token (from [@BotFather](https://t.me/botfather))
- Telegram chat ID

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd earthquake-alert-telegram-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Create a `.env` file with:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

## Configuration

Customize settings in `config.py`:

| Setting | Description | Default |
|---------|-------------|---------|
| `SCRAPING_INTERVAL` | Time between checks (seconds) | 300 (5 minutes) |
| `MIN_MAGNITUDE` | Minimum earthquake magnitude for alerts | 1.0 |
| `LOG_FILE` | Log file name | earthquake_bot.log |
| `LAST_EVENT_FILE` | File to store the most recent event | last_event.json |

## Usage

Start the monitoring system:

```bash
python main.py
```

The system will:
- Run an initial check immediately
- Continue checking at the specified interval
- Send alerts for new earthquakes above the minimum magnitude
- Log all activities

## Telegram Notifications

Alerts include:
- Magnitude with color-coded severity indicators (🔴, 🟡, 🟢)
- Warning indicator for felt earthquakes ⚠️
- Location in Thai and English
- Depth measurement
- Date and time (local and UTC)
- Geographic coordinates
- Number of seismic phases recorded
- Data source attribution

## Project Structure

- `main.py` - Entry point and scheduling logic
- `scraper.py` - TMD website data extraction
- `telegram_bot.py` - Notification formatting and delivery
- `config.py` - Configuration settings
- `.env` - Environment variables storage

## Logging

The system maintains detailed logs in `earthquake_bot.log`, including:
- Operation status
- Earthquake detections
- Notification delivery
- Error diagnostics

## Error Handling

Comprehensive error management for:
- Network connection issues
- Website structure changes
- Telegram API failures
- Malformed data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests. 