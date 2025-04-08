import time
import sys
import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
import google.generativeai as genai
from xml.etree import ElementTree
import base64

def setup_device():
    """Setup Appium and launch the app."""
    try:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.platform_version = "14"
        options.device_name = "Akkim-Galaxy S22 Ultra"
        options.app_package = "com.mayhem.ugwob"
        options.app_activity = "com.epicgames.ue4.GameActivity"
        options.no_reset = True

        driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
        print("App Launched Successfully!")
        time.sleep(10)  # Wait for app to launch
        return driver
    except Exception as e:
        print(f"Error setting up device: {e}")
        return None

def server_selection(driver):
    """Selects a server in the app."""
    try:
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
    except Exception as e:
        print(f"Error selecting server: {e}")

def login_action(driver):
    """Performs the login action and interacts with Gemini."""
    if not driver:
        return  # Exit if driver setup failed

    # Initialize Gemini AI
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: API Key is missing. Please check your GOOGLE_API_KEY environment variable.")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-vision')  # Use gemini-pro-vision
        chat = model.start_chat(history=[])

        # First tap - Disclaimer action (Adjust as needed)
        tap_x3, tap_y3 = 2020, 977
        driver.tap([(tap_x3, tap_y3)])
        print("T & C Selected")
        time.sleep(2)

        # Second tap - Logged as Guest action (Adjust as needed)
        tap_x4, tap_y4 = 2178, 620
        driver.tap([(tap_x4, tap_y4)])
        print("Logged as Guest")
        time.sleep(15)

        # Take Screenshot
        screenshot_path = "guest_login_screenshot.png"
        driver.save_screenshot(screenshot_path)

        # Encode screenshot as base64
        with open(screenshot_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Use Gemini Vision to analyze the image
        prompt = "Analyze this image and extract all text and their bounding boxes. Provide the text and their coordinates (x, y, width, height)."
        response = chat.send_message(
            prompt,
            [genai.Part.from_data(data=encoded_image, mime_type="image/png")]
        )
        print(f"Gemini Vision: {response.text}")

        time.sleep(10)  # Add a delay if needed

    except Exception as e:
        print(f"Error in login_action: {e}")

def main():
    """Main function to orchestrate the Appium and Gemini interactions."""
    print(sys.executable)  # Print the Python interpreter being used
    driver = setup_device()
    if driver:
        server_selection(driver)
        login_action(driver)
        driver.quit()

if __name__ == "__main__":
    main()