import os
import time
import json
import subprocess
import requests
from PIL import Image
from appium import webdriver
from appium.options.android import UiAutomator2Options
import shutil

API_KEY = 'K81674033288957'  # Static API key

# Function to compress the screenshot to ensure it is below 1MB without resizing the image dimensions
def compress_image(input_path, output_path):
    """Compress the image without resizing, ensuring it is under 1MB"""
    file_size_kb = os.path.getsize(input_path) / 1024  # Convert file size to KB

    if file_size_kb > 1024:  # If the file is greater than 1MB
        print(f"Original size: {int(file_size_kb)} KB. Compressing...")
        with Image.open(input_path) as img:
            img = img.convert("RGB")  # Convert to RGB to handle transparency (e.g., for PNGs)
            img.save(output_path, format="JPEG", quality=80)  # Compress and save as JPEG with quality 80

        new_size_kb = os.path.getsize(output_path) / 1024  # Get the new size in KB
        print(f"Compressed size: {int(new_size_kb)} KB")
    else:  # If the image is already under 1MB
        shutil.copy(input_path, output_path)  # No compression needed if it's under 1MB
        print(f"Image is already under 1MB ({int(file_size_kb)} KB). No compression applied.")

    return output_path

# Function to take a screenshot
def take_screenshot(driver, screenshot_path="screenshot.png"):
    """Captures a screenshot"""
    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

# Function to send the image to OCR.Space API for text extraction
def ocr_space_file(filename, api_key=API_KEY):
    """Extract text and coordinates from the image using OCR.Space API"""
    with open(filename, 'rb') as f:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data={'apikey': api_key, 'language': 'eng', 'isOverlayRequired': 'true'}
        )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Received status code {response.status_code}")
        return None

# Function to find the reference word from the extracted text data
def find_text_and_get_coords(extracted_text_info, reference_word):
    """Searches for the reference word in the extracted text info and returns its coordinates."""
    print(f"Searching for reference word: {reference_word}")
    if extracted_text_info:
        for item in extracted_text_info:
            if 'text' in item and reference_word.lower() in item['text'].lower() and 'bounding_box' in item:
                bbox = item['bounding_box']
                print(f"Found '{reference_word}' at: {bbox}")
                return bbox['x'], bbox['y'], bbox['width'], bbox['height']
    print(f"Reference word '{reference_word}' not found.")
    return None

# Function to simulate an ADB tap
def adb_tap(x, y):
    """Simulate a tap at the given coordinates using ADB"""
    adb_command = f"adb shell input tap {int(x)} {int(y)}"
    subprocess.run(adb_command, shell=True, check=True)

# Function to set up the Appium driver and launch the app
def device_setup():
    """Set up Appium and launch the app"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.no_reset = True
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    print("App Launched Successfully!")
    time.sleep(15)
    return driver

# Main login function that uses all common functions
def login(driver):
    # Step 1: Take a screenshot
    screenshot_path = take_screenshot(driver)

    if screenshot_path:
        # Step 2: Compress the screenshot to below 1MB
        compressed_image_path = "/Users/mohamedakkim/PycharmProjects/PythonMeta/ApiCompressed/compressed_loginscreen.jpg"
        compressed_image_path = compress_image(screenshot_path, compressed_image_path)

        if compressed_image_path:
            # Step 3: Extract text from the image using OCR.Space API
            extracted_text_info = ocr_space_file(compressed_image_path)

            if extracted_text_info:
                # Step 4: Define your reference words and search for them
                reference_words = ["Google", "Guest"]

                # Step 5: Find the coordinates of the reference words
                results = find_text_and_get_coords(extracted_text_info, reference_words)

                # Step 6: Tap if reference word found
                for result in results:
                    reference_word = result['reference_word']
                    bbox = result['bounding_box']
                    tap_x = bbox['x'] + bbox['width'] // 2
                    tap_y = bbox['y'] + bbox['height'] // 2
                    print(f"Found '{reference_word}' at (x={bbox['x']}, y={bbox['y']}), tapping at ({tap_x}, {tap_y})")
                    adb_tap(tap_x, tap_y)
                    time.sleep(5)  # Sleep after tapping

            else:
                print("Failed to extract text from the image.")
        else:
            print("Failed to compress image.")
    else:
        print("Failed to take screenshot.")


if __name__ == "__main__":
    driver = device_setup()  # Initialize the Appium driver
    login(driver)  # Perform login using the driver
