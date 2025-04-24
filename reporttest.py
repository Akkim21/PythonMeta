import os
import time
import json
import subprocess
import requests
from PIL import Image
from appium import webdriver
from appium.options.android import UiAutomator2Options
import shutil
import pytest

API_KEY = 'K81674033288957'  # Static API key
compressed_image_path = "/Users/mohamedakkim/PycharmProjects/PythonMeta/ApiCompressed/compressed_screenshot.jpg"


# Function to compress the screenshot to ensure it is below 1MB without resizing the image dimensions
def compress_image(input_path, output_path):
    file_size_kb = os.path.getsize(input_path) / 1024  # Convert file size to KB
    if file_size_kb > 1024:  # If the file is greater than 1MB
        with Image.open(input_path) as img:
            img = img.convert("RGB")
            img.save(output_path, format="JPEG", quality=80)
    else:  # If the image is already under 1MB
        shutil.copy(input_path, output_path)
    return output_path


# Function to take a screenshot
def take_screenshot(driver, screenshot_path="/Users/mohamedakkim/PycharmProjects/PythonMeta/Screenshots/screenshot.png"):
    try:
        driver.save_screenshot(screenshot_path)
        return screenshot_path
    except Exception as e:
        raise Exception(f"Error taking screenshot: {e}")


# Function to send the image to OCR.Space API for text extraction
def ocr_space_file(filename, api_key):
    print("Sending image to OCR.Space API...")
    with open(filename, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data={'apikey': api_key, 'language': 'eng', 'isOverlayRequired': 'true'},
            timeout=60
        )

    if r.status_code != 200:
        print(f"Error: Received status code {r.status_code} from OCR.Space API")
        return None

    try:
        result = r.json()
        print(f"OCR response received successfully.")
        # Debug print the response
        print(json.dumps(result, indent=4))  # Pretty-print the JSON response
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response")
        print(f"Response text: {r.text}")
        return None

    if 'OCRExitCode' not in result or result['OCRExitCode'] != 1:
        print(f"Error: OCR processing failed with message: {result.get('ErrorMessage', 'Unknown error')}")
        return None
    return result['ParsedResults'][0]['TextOverlay']['Lines']


# Function to find the reference word from the extracted text data
# Function to find the reference word from the extracted text data
# Function to find the reference word from the extracted text data
def find_text_and_get_coords(extracted_text_info, reference_word):
    """Searches for reference words in the extracted text info and returns their coordinates."""
    print(f"Searching for reference word: {reference_word}")
    coords = []

    if extracted_text_info:
        for line in extracted_text_info:
            # Each line has a 'LineText' and 'Words'
            if 'LineText' in line:
                line_text = line['LineText']

                # Check if reference word is in the 'LineText'
                if reference_word.lower() in line_text.lower():
                    # If it matches, get the coordinates from 'Words'
                    for word in line['Words']:
                        word_text = word['WordText']
                        if reference_word.lower() in word_text.lower():
                            bbox = word
                            coords.append(bbox)
                            print(f"Found '{reference_word}' at: {bbox}")

    if not coords:
        print(f"Reference word '{reference_word}' not found.")
    return coords


# Function to simulate an ADB tap at the given coordinates
def adb_tap(x, y):
    adb_command = f"adb shell input tap {int(x)} {int(y)}"
    subprocess.run(adb_command, shell=True, check=True)


# Function to search and tap for the reference word
def search_and_tap(driver, reference_word, extracted_text_info, delay_seconds=5):
    text_coords = find_text_and_get_coords(extracted_text_info, reference_word)
    for coords in text_coords:
        x, y, width, height = coords['x'], coords['y'], coords['width'], coords['height']
        tap_x, tap_y = x + width // 2, y + height // 2
        adb_tap(tap_x, tap_y)
        time.sleep(delay_seconds)  # Delay between taps


# Process keywords and handle errors if not found
def process_keywords(driver, keywords, delay_seconds=5):
    screenshot_path = take_screenshot(driver)
    compressed_image_path = "/Users/mohamedakkim/PycharmProjects/PythonMeta/ApiCompressed/compressed_screenshot.jpg"
    extracted_text_info = ocr_space_file(compressed_image_path, API_KEY)

    for reference_word in keywords:
        search_and_tap(driver, reference_word, extracted_text_info, delay_seconds)


# Set up the device using Appium
def setup_device():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.new_command_timeout = 300
    options.no_reset = True

    try:
        driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
        time.sleep(10)
        return driver
    except Exception as e:
        raise Exception(f"Error in setup_device: {e}")


# Test function 1
@pytest.mark.order(1)
def login(driver):
    tap_x3, tap_y3 = 2020, 977
    driver.tap([(tap_x3, tap_y3)])
    time.sleep(2)  # Wait after tapping T&C

    print("Searching for Google")
    process_keywords(driver, ['google'])
    time.sleep(5)

    print("Searching for the email to log")
    process_keywords(driver, ['akkim@mayhem-studios.com'])
    time.sleep(15)


# Test function 2
@pytest.mark.order(2)
def store(driver):
    print("Searching for Store in lobby")
    process_keywords(driver, ['STORE'])
    time.sleep(5)

    print("Searching for back")
    process_keywords(driver, ['Back'])


# Test function 3
@pytest.mark.order(3)
def warehouse(driver, keyword=['Vehicle', 'Back']):
    print("Searching for warehouse in lobby")
    process_keywords(driver, ['Warehouse'])
    time.sleep(5)

    print("Searching for Weapons in warehouse after its found tap on back")
    process_keywords(driver, keyword)
    time.sleep(5)


# Test function 4
@pytest.mark.order(4)
def profile(driver, keywords=['Weapons', 'History', 'Overview', 'Back']):
    print('Searching for user name')

    process_keywords(driver, ['Usep'])
    time.sleep(3)

    process_keywords(driver, keywords)
    time.sleep(3)


if __name__ == "__main__":
    driver = setup_device()
    if driver:
        login(driver)
        store(driver)
        warehouse(driver, keyword=['Weapons', 'Back'])
        profile(driver, keywords=['Weapons', 'History', 'Overview', 'Back'])
