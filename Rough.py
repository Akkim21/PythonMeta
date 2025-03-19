import time
import pytesseract
from PIL import Image
import base64
from appium import webdriver
from appium.options.android import UiAutomator2Options
from io import BytesIO

# Set the path to tesseract executable explicitly
pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"  # Update with the correct path

# Create an instance of UiAutomator2Options
options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "14"  # Your Android version
options.device_name = "Akkim-Galaxy S22 Ultra"  # Your device name
options.app_package = "com.mayhem.ugwob"  # Your app package
options.app_activity = "com.epicgames.ue4.GameActivity"  # Your app activity
options.no_reset = True  # Keep the app state after execution

# Start Appium session with options instead of a dictionary
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

# Perform a simple action (print screen title)
print("App Launched Successfully!")
time.sleep(5)

# Tap on coordinates to start the app
tap_x, tap_y = 625, 296
driver.tap([(tap_x, tap_y)])
print("Server Selection")
time.sleep(2)

tap_x1, tap_y1 = 596, 513
driver.tap([(tap_x1, tap_y1)])
print("Server Selected")
time.sleep(2)

tap_x2, tap_y2 = 2810, 315
driver.tap([(tap_x2, tap_y2)])
print("Server Launched")
time.sleep(10)

tap_x3, tap_y3 = 2020, 977
driver.tap([(tap_x3, tap_y3)])
print("T & C Selected")
time.sleep(2)

def capture_and_extract_text_with_data(driver):
    """Capture the entire screen and extract text with bounding box data using pytesseract."""
    # Take a full screenshot using Appium
    screenshot = driver.get_screenshot_as_base64()
    screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))

    # Use pytesseract to extract text with bounding box data
    data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
    return data

def tap_if_text_found(driver, target_text):
    """Tap on the screen if the target text is found in the extracted text."""
    data = capture_and_extract_text_with_data(driver)
    
    # Iterate through each word in the image data
    for i, word in enumerate(data['text']):
        if target_text.lower() in word.lower():  # Case insensitive comparison
            print(f"Text '{target_text}' found at index {i}!")

            # Get the coordinates of the bounding box for the word
            x = data['left'][i]
            y = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]

            # Calculate the center of the bounding box (you can adjust it if you want to tap more precisely)
            center_x = x + width // 2
            center_y = y + height // 2

            # Tap on the calculated center coordinates
            driver.tap([(center_x, center_y)])
            print(f"Tapped on the coordinates ({center_x}, {center_y})")
            return
    print(f"Text '{target_text}' not found.")

# Target text to look for in the screenshot
target_text = "Guest"  # Replace with the text you're looking for

# Run the function to check for the text and tap if found
tap_if_text_found(driver, target_text)

# Quit the session
driver.quit()
