import requests
from bs4 import BeautifulSoup
import time
import Adafruit_CharLCD as LCD
from unidecode import unidecode
from datetime import datetime
import re
import RPi.GPIO as GPIO

import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_file = 'console.log'
max_file_size = 100 * 1024 * 1024  # 100 MB
backup_count = 5  # Number of backup log files to keep

# Create a rotating file handler
file_handler = RotatingFileHandler(log_file, maxBytes=max_file_size, backupCount=backup_count)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

# Add the rotating file handler to the root logger
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)

# Raspberry Pi GPIO pin and LCD use configuration
lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

# RGB LED configuration
red_pin = 19    # GPIO pin for red color
green_pin = 20  # GPIO pin for green color
blue_pin = 21   # GPIO pin for blue color

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)
GPIO.setup(blue_pin, GPIO.OUT)

# Display loop duration
duration = 599

# Internet connection check interval
check_interval = 60

while True:
    # Starts counting for duration
    start_time = time.time()

    # Check for internet connectivity
    while True:
        try:
            requests.get("https://www.google.com", timeout=5)
            break
        except requests.ConnectionError:
            print("No internet connection. Retrying in 30 minutes…")
            logging.error("No internet connection. Retrying in 30 minutes…")
            time.sleep(check_interval)

    # Send a GET request to the webpage
    url = "https://www.airquality.dli.mlsi.gov.cy/"
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the div element with the specified class that shows pollution data
        div_element = soup.find("div", class_="col col-xs-12 col-sm-6 col-md-3 col-lg-2 col-3")

        if div_element:
            # Find the h4 header within the div to filter out results for Limassol
            h4_header = div_element.find("h4", class_="field-content stations-overview-title")

            if h4_header:
                # Get the station city
                station_name = h4_header.text.strip()

                # Find all pollutant labels and values within the div along with last update time
                pollutant_labels = div_element.find_all(class_="pollutant-label")
                pollutant_values = div_element.find_all(class_="pollutant-value")

                # Find the element containing the text starting with "Updated on: "
                regex_pattern = re.compile(r"^Updated on: (\d{2}/\d{2}/\d{4} \d{2}:\d{2})")
                element = soup.find(text=regex_pattern)

                if element:
                # Extract the time from the text
                    match = regex_pattern.match(element)
                    if match:
                        updated_time = match.group(1)

                # Find the element with the color indicator
                color_indicator = div_element.find("div", class_="group-status-helper-wrapper")
                if color_indicator:
                    color_classes = color_indicator.find_all(class_=re.compile("station-status-(green|yellow|orange|red)"))
                    if color_classes:
                        pollution_color = color_classes[0]['class'][1]  # Get the color from the class attribute

                        # Map pollution colors to GPIO states
                        color_states = {'green': (GPIO.LOW, GPIO.HIGH, GPIO.HIGH),
                                        'yellow': (GPIO.HIGH, GPIO.HIGH, GPIO.LOW),
                                        'orange': (GPIO.HIGH, GPIO.LOW, GPIO.HIGH),
                                        'red': (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)}

                        # Set GPIO pins to the corresponding color state
                        GPIO.output(red_pin, color_states[pollution_color][0])
                        GPIO.output(green_pin, color_states[pollution_color][1])
                        GPIO.output(blue_pin, color_states[pollution_color][2])

                # Display loop
                index = 0
                while time.time() - start_time < duration:
                    # Create a list of formatted pollutant lines
                    pollutant_lines = []
                    for label, value in zip(pollutant_labels, pollutant_values):
                        pollutant_label = label.text.strip().rstrip(":")  # Remove trailing colon
                        pollutant_value = value.text.strip()
                        if pollutant_value == "Not Measured":  # Short text for N/A
                            pollutant_value = "N/A"
                        line = f"Pollutant: {pollutant_label}\nValue: {pollutant_value}"
                        pollutant_lines.append(line)

                    # Add the timestamp
                    time_line = f"Last Updated:\n{updated_time}"
                    pollutant_lines.insert(8, time_line)

                    # Get the current line to display
                    line = pollutant_lines[index]

                    # Clear the LCD screen
                    lcd.clear()

                    # Normalize unicode text since LCD can't render unicode symbols
                    normalized_text = unidecode(line)

                    # Display the line on the LCD screen
                    lcd.message(normalized_text)

                    # Log all lines of pollutant data in the console without timestamp
                    for i, line in enumerate(pollutant_lines):
                        if i != 8:  # Skip logging for the 9th line
                            logging.info(line)

                    # Set the display duration for the first pollutant
                    if index == 0:
                        display_duration = 10
                    else:
                        display_duration = 3

                    # Pause for the specified duration
                    time.sleep(display_duration)

                    # Increment the index and loop back to the beginning
                    index = (index + 1) % len(pollutant_lines)

                    # Print all lines of pollutant data in the console
                    for line in pollutant_lines:
                        print(line)
            else:
                print("Could not find table for Limassol, webpage updated or unavailable")
                logging.error("Could not find table for Limassol, webpage updated or unavailable")
                time.sleep(59)
        else:
            print("Could not find the table, webpage updated or unavailable")
            logging.error("Could not find the table, webpage updated or unavailable")
            time.sleep(59)

    else:
        lcd.clear()
        lcd.message("Error fetching data")
        logging.error("Error fetching data")
        time.sleep(59)
    
    time.sleep(1)
