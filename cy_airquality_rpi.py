import requests
from bs4 import BeautifulSoup
import time
import Adafruit_CharLCD as LCD
from unidecode import unidecode

# Raspberry Pi GPIO pin and LCD use configuration
lcd_rs        = 25
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 18
lcd_d7        = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows=2

lcd_columns = 16
lcd_rows    = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

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
            # Get the station name
            station_name = h4_header.text.strip()

            # Find all pollutant labels and values within the div
            pollutant_labels = div_element.find_all(class_="pollutant-label")
            pollutant_values = div_element.find_all(class_="pollutant-value")
        
            # Extract and print the pollutant labels and values
            print(f"Station: {station_name}")
            for label, value in zip(pollutant_labels, pollutant_values):
                pollutant_label = label.text.strip()
                pollutant_value = value.text.strip()
                if pollutant_value == "Not Measured":
                        pollutant_value = "N/A"
                print(f"Pollutant {pollutant_label}, value: {pollutant_value}")
        else:
            print("Could not find the table's header, webpage updated or unavailable")
    else:
        print("Could not find the table, webpage updated or unavailable")

    # Normalize unicode text since LCD can't render unicode symbols
    unicode_text = (f"Pollutant {pollutant_label}\nValue {pollutant_value}")
    normalized_text = unidecode(unicode_text)
    
    # Render on screen
    lcd.message(normalized_text)
    
    # Update every 10 minutes
    time.sleep(600)
