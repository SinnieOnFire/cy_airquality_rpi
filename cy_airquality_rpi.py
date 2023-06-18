import requests
from bs4 import BeautifulSoup
import time
import Adafruit_CharLCD as LCD
from unidecode import unidecode

# Raspberry Pi pin configuration
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

# Send a GET request to the webpage
url = "https://www.airquality.dli.mlsi.gov.cy/"
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find the div containing the data
divs = soup.find_all("div", class_="col col-xs-12 col-sm-6 col-md-3 col-lg-2 col-3")

# Loop through the divs and extract the data for Limassol only
for div in divs:
    # Extract the location, pollutant, and value data
    location_element = div.find("h4")
    pollutant_label = div.find("span", class_="pollutant-label")
    pollutant_value = div.find("span", class_="pollutant-value")
    
    # Check if elements are found
    if location_element and pollutant_label and pollutant_value and "Limassol" in location_element.text:
        location = location_element.text.strip()
        pollutant = pollutant_label.text.strip()
        value = pollutant_value.text.strip()
        # Print or process the extracted data as needed
        print(f"Pollutant: {pollutant}, Value: {value}")


unicode_text = (f"Pollutant {pollutant}\nValue {value}")
normalized_text = unidecode(unicode_text)

lcd.message(normalized_text)