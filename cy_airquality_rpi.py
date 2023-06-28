import requests
from bs4 import BeautifulSoup
import time
import Adafruit_CharLCD as LCD
from unidecode import unidecode

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

lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

while True:
    # Refresh screen
    lcd.clear()

    # Send a GET request to the webpage
    url = "https://www.airquality.dli.mlsi.gov.cy/"
    response = requests.get(url)

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

            # Find all pollutant labels and values within the div
            pollutant_labels = div_element.find_all(class_="pollutant-label")
            pollutant_values = div_element.find_all(class_="pollutant-value")

            # Create a list of formatted pollutant lines
            pollutant_lines = []
            for label, value in zip(pollutant_labels, pollutant_values):
                pollutant_label = label.text.strip().rstrip(":")
                pollutant_value = value.text.strip()
                if pollutant_value == "Not Measured":
                    pollutant_value = "N/A"
                print(f"Pollutant {pollutant_label}, value: {pollutant_value}")
                line = f"Pollutant {pollutant_label}\nValue {pollutant_value}"
                pollutant_lines.append(line)

                # Scroll through the pollutant lines on the LCD display
                for line in pollutant_lines:
                # Clear the LCD screen
                    lcd.clear()

                # Normalize unicode text since LCD can't render unicode symbols
                normalized_text = unidecode(line)

                # Scroll the line on the LCD display
                for i in range(len(normalized_text) - lcd_columns + 1):
                    lcd.message(normalized_text[i:i+lcd_columns])
                    time.sleep(0.5)  # Adjust the scrolling speed here

                # Pause at the end of each line
                time.sleep(10)  # Adjust the pause duration here
        else:
            print("Could not find table for Limassol, webpage updated or unavailable")
    else:
        print("Could not find the table, webpage updated or unavailable")

    # Update every 10 minutes
    time.sleep(600)
