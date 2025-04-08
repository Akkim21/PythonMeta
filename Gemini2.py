import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.actions import PointerInput, Interaction
from appium.webdriver.common.by import By  # Import By
from google.cloud import aiplatform
import base64
import json
from google.oauth2 import service_account
from google.cloud.aiplatform import GenerativeModel

# Load credentials from a JSON key file manually in Python
credentials = service_account.Credentials.from_service_account_file(
    '/Users/mohamedakkim/Downloads/pymeta-11092698b56d.json'
)

# Initialize aiplatform with the loaded credentials
aiplatform.init(credentials=credentials)

# Appium Setup Function
def setup_device():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.no_reset = True
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    print("App Launched Successfully!")
    time.sleep(10)
    return driver

# Gemini API Setup
PROJECT_ID = "pymeta"
LOCATION = "us-central1"
model = aiplatform.GenerativeModel("gemini-pro-vision")

# Screenshot and text extraction functions
def get_screenshot_base64(driver):
    """Takes a screenshot and returns it as a base64 string."""
    screenshot = driver.get_screenshot_as_png()
    return base64.b64encode(screenshot).decode("utf-8")

def extract_text_and_coordinates(image_base64, reference_text):
    """Extracts text and coordinates using Gemini API."""
    image_data = {"mime_type": "image/png", "data": image_base64}
    prompt = f"Find the text '{reference_text}' in this image. Return the bounding box coordinates [x_min, y_min, x_max, y_max] in json format. If not found, return null."

    try:
        response = model.generate_content([prompt, image_data])
        json_result = json.loads(response.text)
        return json_result
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error during text extraction: {e}")
        return None

# Tap coordinates function (using PointerInput and Interaction)
def tap_coordinates(driver, x, y):
    """Taps the specified coordinates using PointerInput."""
    finger = PointerInput("touch", "finger")
    actions = Interaction(driver)
    actions.add_pointer_input(finger)
    actions.add_action(finger.create_pointer_move(duration=0, x=x, y=y))
    actions.add_action(finger.create_pointer_down(button=1))
    actions.add_action(finger.create_pointer_up(button=1))
    actions.perform()

# Setup Appium driver and run the logic
driver = setup_device()

reference_word = "Google"  # Replace with your reference word
screenshot_base64 = get_screenshot_base64(driver)
coordinates = extract_text_and_coordinates(screenshot_base64, reference_word)

if coordinates:
    x_center = (coordinates[0] + coordinates[2]) // 2
    y_center = (coordinates[1] + coordinates[3]) // 2
    tap_coordinates(driver, x_center, y_center)
    print(f"Tapped coordinates: ({x_center}, {y_center})")
else:
    print(f"'{reference_word}' not found on the screen.")

# Close the Appium driver
driver.quit()