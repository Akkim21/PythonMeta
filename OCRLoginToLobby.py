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

# Fixed path for saving compressed images
compressed_image_path = "/Users/mohamedakkim/PycharmProjects/PythonMeta/ApiCompressed/compressed_screenshot.jpg"


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
def ocr_space_file(filename, api_key):
    """Function to extract text and its coordinates from an image using OCR.Space API."""
    print("Sending image to OCR.Space API...")
    with open(filename, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data={
                'apikey': api_key,
                'language': 'eng',
                'isOverlayRequired': 'true'
            },
            timeout=60
        )

    if r.status_code != 200:
        print(f"Error: Received status code {r.status_code} from OCR.Space API")
        return None

    try:
        result = r.json()
        print(f"OCR response received successfully.")
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response")
        print(f"Response text: {r.text}")
        return None

    if 'OCRExitCode' not in result:
        print(f"Error: OCRExitCode not found in the response")
        return None

    if result['OCRExitCode'] == 1:
        if 'TextOverlay' in result['ParsedResults'][0]:
            parsed_results = result['ParsedResults'][0]['TextOverlay']['Lines']
            output = []
            for line in parsed_results:
                for word in line['Words']:
                    text = word['WordText']
                    x = word['Left']
                    y = word['Top']
                    width = word['Width']
                    height = word['Height']
                    output.append({
                        'text': text,
                        'bounding_box': {
                            'x': x,
                            'y': y,
                            'width': width,
                            'height': height
                        }
                    })
            return output
        else:
            print("Error: TextOverlay not found in the response.")
            return None
    else:
        print(f"Error: {result['ErrorMessage']}")
        return None


# Function to find the reference word from the extracted text data
def find_text_and_get_coords(extracted_text_info, reference_word):
    """Searches for reference words in the extracted text info and returns their coordinates."""
    print(f"Searching for reference word: {reference_word}")
    coords = []
    if extracted_text_info:
        for item in extracted_text_info:
            if 'text' in item and reference_word.lower() in item['text'].lower() and 'bounding_box' in item:
                bbox = item['bounding_box']
                coords.append(bbox)
                print(f"Found '{reference_word}' at: {bbox}")
    if not coords:
        print(f"Reference word '{reference_word}' not found.")
    return coords


# Function to simulate an ADB tap at the given coordinates
def adb_tap(x, y):
    """Simulates a tap at the given x, y coordinates using ADB."""
    try:
        adb_command = f"adb shell input tap {int(x)} {int(y)}"
        subprocess.run(adb_command, shell=True, check=True)
        print(f"Tapped at coordinates: ({int(x)}, {int(y)}) using ADB.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing ADB tap: {e}")
    except FileNotFoundError:
        print("Error: ADB command not found.")
    except Exception as e:
        print(f"An unexpected error occurred during ADB tap: {e}")


def setup_device():
    """Setup Appium and launch the app."""
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
        print("App Launched Successfully!")
        time.sleep(10)  # Wait for app to launch
        return driver
    except Exception as e:
        print(f"Error in setup_device: {e}")
        return None


# Reusable function to handle searching for a keyword, tapping, and waiting
def search_and_tap(driver, reference_word, extracted_text_info, delay_seconds=5):
    """Searches for a reference word, taps on the found coordinates, and waits."""
    print(f"Searching for '{reference_word}'")
    text_coords = find_text_and_get_coords(extracted_text_info, reference_word)

    if text_coords:
        print(f"Found {len(text_coords)} occurrences of '{reference_word}'. Performing taps...")
        for idx, coords in enumerate(text_coords):
            x = coords['x']
            y = coords['y']
            width = coords['width']
            height = coords['height']

            tap_x = x + width // 2  # Calculate x as the center of the bounding box
            tap_y = y + height // 2  # Calculate y as the center of the bounding box

            print(f"Tapping on '{reference_word}' at ({tap_x}, {tap_y})")
            adb_tap(tap_x, tap_y)

            # Wait before the next tap if multiple occurrences exist
            if idx < len(text_coords) - 1:
                print(f"Waiting for {delay_seconds} seconds before the next tap...")
                time.sleep(delay_seconds)  # Delay between taps
    else:
        print(f"'{reference_word}' not found in the image.")


# Reusable function to handle login and store actions
# Reusable function to handle searching for a keyword, tapping, and waiting
def process_keywords(driver, keywords, delay_seconds=5):
    try:
        # Step 1: Take a screenshot and process it once
        screenshot_path = take_screenshot(driver)
        if screenshot_path:
            # Define the fixed path for the compressed image
            compressed_image_path = "/Users/mohamedakkim/PycharmProjects/PythonMeta/ApiCompressed/compressed_screenshot.jpg"
            compressed_image_path = compress_image(screenshot_path, compressed_image_path)

            # Extract text info using OCR
            extracted_text_info = ocr_space_file(compressed_image_path, API_KEY)
            if extracted_text_info:
                # Perform search and tap for each keyword
                for reference_word in keywords:
                    search_and_tap(driver, reference_word, extracted_text_info, delay_seconds)

    except Exception as e:
        print(f"An error occurred: {e}")


def login(driver):

    # Tap on T & C
    tap_x3, tap_y3 = 2020, 977
    driver.tap([(tap_x3, tap_y3)])
    print("T & C Selected")
    time.sleep(5)  # Wait after tapping T&C

    # Process the first round of keywords (google)
    print("First round of keyword search and tap:")
    process_keywords(driver, ['google'])  # You can keep delay in the process_keywords function
    time.sleep(5)  # Wait for 10 seconds after tapping "google"

    # Process the second round of keywords (gmail)
    print("Second round of keyword search and tap:")
    process_keywords(driver, ['preprod2121@gmail.com'])  # You can keep delay in the process_keywords function
    time.sleep(45)  # Wait for 15 seconds after tapping "gmail"


def store(driver):

    # Process the first round of keywords (google)
    print("First round of keyword search and tap:")
    process_keywords(driver, ['Store'])  # You can keep delay in the process_keywords function
    time.sleep(5)  # Wait for 10 seconds after tapping "google"

    # Process the second round of keywords (gmail)
    print("Second round of keyword search and tap:")
    process_keywords(driver, ['Khalihan top'])  # You can keep delay in the process_keywords function
    time.sleep(5)  # Wait for 15 seconds after tapping "gmail"

    # Process the second round of keywords (gmail)
    print("Second round of keyword search and tap:")
    process_keywords(driver, ['back'])  # You can keep delay in the process_keywords function
    time.sleep(5)  # Wait for 15 seconds after tapping "gmail"

if __name__ == "__main__":
    driver = setup_device()
    if driver:  # Only proceed if the driver is successfully initialized
        login(driver)
        store(driver)
