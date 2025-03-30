import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
import re
from datetime import datetime
from config import EARTHQUAKE_URL, LAST_EVENT_FILE

class EarthquakeScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_event = self._load_last_event()

    def _load_last_event(self):
        """Load the last processed event from file."""
        try:
            with open(LAST_EVENT_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_last_event(self, event):
        """Save the last processed event to file."""
        with open(LAST_EVENT_FILE, 'w') as f:
            json.dump(event, f)

    def _parse_location(self, location_text):
        """Parse location text to separate Thai and English names."""
        # Clean up the input text first
        location_text = location_text.strip()
        
        # Special handling: remove extra spaces between 'ต' and '.' to become 'ต.'
        location_text = re.sub(r'(ต)\s+\.', r'\1.', location_text)
        
        # First check for newlines (most reliable separator)
        if "\n" in location_text:
            parts = location_text.split('\n')
            thai_location = parts[0].strip() if len(parts) > 0 else ""
            english_location = parts[1].strip() if len(parts) > 1 else ""
            return thai_location, english_location
        
        # Thai unicode range: \u0e00-\u0e7f
        # Regular expression to find the transition point from Thai to English
        # This looks for the last Thai character followed by a non-Thai character
        match = re.search(r'[\u0e00-\u0e7f](?=\s*[^\u0e00-\u0e7f])', location_text)
        if match:
            # Split at the position after the last Thai character
            split_index = match.end()
            thai_location = location_text[:split_index].strip()
            english_location = location_text[split_index:].strip()
            return thai_location, english_location
        
        # Fallback to the original method - find first English letter
        match = re.search(r'[A-Za-z]', location_text)
        if match:
            split_index = match.start()
            thai_location = location_text[:split_index].strip()
            english_location = location_text[split_index:].strip()
            return thai_location, english_location
        
        # If no English characters found, assume all Thai
        return location_text, ""

    def scrape_earthquake_data(self):
        """Scrape earthquake data from the TMD website."""
        try:
            response = requests.get(EARTHQUAKE_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find the table containing earthquake data by its class and ID
            table = soup.find('table', {'class': 'tbis', 'id': 'table_inside'})
            
            if not table:
                # Fallback to other methods if specific table not found
                table = soup.find('table', {'class': 'tbis'})
                
            if not table:
                # Another fallback - look for the header row
                header_row = soup.find('tr', {'class': 'tbis1'})
                if header_row:
                    table = header_row.find_parent('table')
            
            if not table:
                self.logger.error("Could not find earthquake data table")
                return None

            # Find all earthquake rows by their classes
            rows = table.find_all('tr', {'class': ['tbis_leq1', 'tbis_leq2']})
            if not rows:
                self.logger.error("No earthquake data rows found")
                return None

            # Process the first (latest) earthquake
            latest_row = rows[0]
            cells = latest_row.find_all('td')
            
            # Extract date and time
            date_time_cell = cells[0]
            date_time_text = date_time_cell.get_text(strip=True)
            
            # Split the date/time correctly - there might be two timestamps merged
            # Look for patterns like YYYY-MM-DD HH:MM:SS
            date_time_pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
            date_matches = re.findall(date_time_pattern, date_time_text)
            
            if len(date_matches) >= 1:
                # First match is local time
                date_time_text = date_matches[0].strip()
                
                # If there's a second match with UTC, it's the UTC time
                utc_time_text = ""
                if len(date_matches) > 1 and "UTC" in date_time_text:
                    utc_time_text = date_matches[1].strip() + " UTC"
                else:
                    # Try to find UTC time in a sub-element
                    utc_p = date_time_cell.find('p', {'style': 'font-size:10px'})
                    if utc_p:
                        utc_time_text = utc_p.get_text(strip=True)
            else:
                # Fallback to the old method
                date_time_text = date_time_cell.get_text(strip=True).split('\n')[0]
                utc_p = date_time_cell.find('p', {'style': 'font-size:10px'})
                utc_time_text = utc_p.get_text(strip=True) if utc_p else ""
            
            # Extract magnitude
            magnitude_cell = cells[1]
            magnitude_text = magnitude_cell.get_text(strip=True)
            # Handle bold formatting if present
            if magnitude_cell.find('b'):
                magnitude_text = magnitude_cell.find('b').get_text(strip=True)
            # Clean and convert to float
            magnitude = float(magnitude_text.replace('b>', ''))
            
            # Extract coordinates
            lat = float(cells[2].get_text(strip=True).replace('°N', ''))
            lon = float(cells[3].get_text(strip=True).replace('°E', ''))
            
            # Extract depth
            depth = float(cells[4].get_text(strip=True))
            
            # Extract phases
            phases = int(cells[5].get_text(strip=True))
            
            # Extract location
            location_cell = cells[6]
            location_span = location_cell.find('span', {'class': 'style10'})
            if location_span:
                location_text = location_span.get_text()
            else:
                location_text = location_cell.get_text()
            
            thai_location, english_location = self._parse_location(location_text)
            
            # Check if earthquake was felt (has icon_peq2.png)
            is_felt = bool(latest_row.find('img', {'src': 'images/icon_peq2.png'}))
            
            # Create event dictionary
            latest_event = {
                'DateTime': date_time_text,
                'UTCTime': utc_time_text,
                'Magnitude': magnitude,
                'Latitude': lat,
                'Longitude': lon,
                'Depth': depth,
                'Phases': phases,
                'ThaiLocation': thai_location,
                'EnglishLocation': english_location,
                'IsFelt': is_felt
            }
            
            # Check if this is a new event
            if self._is_new_event(latest_event):
                self._save_last_event(latest_event)
                return latest_event
            
            return None

        except requests.RequestException as e:
            self.logger.error(f"Error fetching earthquake data: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error while scraping: {str(e)}")
            return None

    def _is_new_event(self, event):
        """Check if the event is new and should trigger a notification."""
        if not self.last_event:
            return True
        
        # Extract clean datetime strings for comparison
        def clean_datetime_str(dt_str):
            # Extract just the date and time portion (YYYY-MM-DD HH:MM:SS)
            match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', dt_str)
            if match:
                return match.group(1)
            return dt_str  # Return original if no match
        
        try:
            # Clean and standardize the datetime strings
            last_event_clean = clean_datetime_str(self.last_event['DateTime'])
            new_event_clean = clean_datetime_str(event['DateTime'])
            
            # Parse the clean datetime strings
            last_event_time = datetime.strptime(last_event_clean, '%Y-%m-%d %H:%M:%S')
            new_event_time = datetime.strptime(new_event_clean, '%Y-%m-%d %H:%M:%S')
            
            return new_event_time > last_event_time
        except Exception as e:
            self.logger.warning(f"Date comparison error: {str(e)}")
            # If there's any error in parsing, consider it a new event to be safe
            return True 