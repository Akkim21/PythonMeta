import os
import time
import json
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
import boto3
from PIL import Image, ImageEnhance
import re

# Initialize AWS Textract client
textract_client = boto3.client('textract', region_name='us-east-1')


# Function to take a screenshot
def take_screenshot(driver, screenshot_path="/Users/mohamedakkim/PycharmProjects/PythonMeta/Screenshots/screenshot5.png"):
    """Captures a screenshot"""
    try:
        # Check if the directory exists, if not create it
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None


# Function to preprocess the image (if needed)
def preprocess_image(screenshot_path):
    """Preprocess the image to enhance text recognition."""
    try:
        img = Image.open(screenshot_path)
        img = img.convert('RGB')  # Convert to RGB
        img = img.convert('L')  # Convert to grayscale

        # Enhance the contrast to make the text clearer
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)  # Increase contrast by a factor of 2

        img.save(screenshot_path)  # Save the preprocessed image
        print("Image preprocessing complete.")
        return screenshot_path
    except Exception as e:
        print(f"Error in image preprocessing: {e}")
        return screenshot_path

# Function to send the image to AWS Textract API for text extraction
def textract_text_and_coords(screenshot_path):
    """Function to extract text and its coordinates from an image using AWS Textract."""
    if not os.path.exists(screenshot_path):
        print(f"Error: Image file does not exist at {screenshot_path}")
        return []

    print(f"Sending image to AWS Textract API... (image path: {screenshot_path})")
    with open(screenshot_path, 'rb') as document:
        response = textract_client.detect_document_text(
            Document={'Bytes': document.read()}
        )

    # Create a list to store the extracted text and coordinates
    extracted_data = []

    # Image dimensions (optional, adjust as needed)
    image_width = 3088  # Replace with your actual image width (use the screenshot's real width)
    image_height = 1440  # Replace with your actual image height (use the screenshot's real height)

    # Process the blocks in the response
    for item in response["Blocks"]:
        if item["BlockType"] == "WORD":
            text = item["Text"]
            # Coordinates for the bounding box of the text
            bounding_box = item["Geometry"]["BoundingBox"]

            # Convert to actual coordinates (multiplying by image width and height)
            left = int(bounding_box["Left"] * image_width)
            top = int(bounding_box["Top"] * image_height)
            width = int(bounding_box["Width"] * image_width)
            height = int(bounding_box["Height"] * image_height)

            # Append data with text and bounding box (X, Y, W, H)
            extracted_data.append({
                "text": text,
                "bounding_box": {
                    "X": left,
                    "Y": top,
                    "W": width,
                    "H": height
                }
            })

    # Print the extracted text for debugging purposes
    print("Extracted Words and Coordinates:")
    for data in extracted_data:
        print(f"Text: {data['text']} | Coordinates: {data['bounding_box']}")

    return extracted_data


# Function to find the reference word from the extracted text data
def find_text_and_get_coords(extracted_text_info, reference_word):
    """Searches for reference words in the extracted text info and returns their coordinates."""
    print(f"Searching for reference word: {reference_word}")
    coords = []
    if extracted_text_info:
        for item in extracted_text_info:
            # Check for the keyword in a case-insensitive manner using regex for variations
            if re.search(reference_word, item['text'], re.IGNORECASE):
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


# Reusable function to handle searching for a keyword, tapping, and waiting
def search_and_tap(driver, reference_word, extracted_text_info, delay_seconds=5):
    """Searches for a reference word, taps on the found coordinates, and waits."""
    print(f"Searching for '{reference_word}'")
    text_coords = find_text_and_get_coords(extracted_text_info, reference_word)

    if text_coords:
        print(f"Found {len(text_coords)} occurrences of '{reference_word}'. Performing taps...")
        for idx, coords in enumerate(text_coords):
            x = coords['X']
            y = coords['Y']
            width = coords['W']
            height = coords['H']

            tap_x = x + width // 2  # Calculate x as the center of the bounding box
            tap_y = y + height // 2  # Calculate y as the center of the bounding box

            print(f"Tapping on '{reference_word}' at ({tap_x}, {tap_y})")
            adb_tap(tap_x, tap_y)
            time.sleep(delay_seconds)  # Delay between taps
    else:
        print(f"'{reference_word}' not found in the image.")


# Function to process the keywords and perform taps
def process_keywords(driver, keywords, delay_seconds=5):
    try:
        # Step 1: Take screenshot and process it
        screenshot_path = take_screenshot(driver)
        if screenshot_path:
            screenshot_path = preprocess_image(screenshot_path)  # Preprocess image if needed

            # Step 2: Extract text info using AWS Textract
            extracted_text_info = textract_text_and_coords(screenshot_path)

            if extracted_text_info:
                # Perform search and tap for each keyword
                for reference_word in keywords:
                    search_and_tap(driver, reference_word, extracted_text_info, delay_seconds)
    except Exception as e:

        print(f"An error occurred: {e}")


def setup_device():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.new_command_timeout = 300  # Increase the timeout to 5 minutes
    options.no_reset = True

    try:
        driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
        print("App Launched Successfully!")
        time.sleep(10)
        return driver
    except Exception as e:
        print(f"Error in setup_device: {e}")
        return None


def login(driver):
    tap_x3, tap_y3 = 2020, 977
    driver.tap([(tap_x3, tap_y3)])
    print("T & C Selected")
    time.sleep(2)

    print("Searching for Google")
    process_keywords(driver, ['google'])
    time.sleep(5)

    print("Searching the email to log")
    process_keywords(driver, ['akkim@mayhem-studios.com'])
    time.sleep(15)


def store(driver):
    print("Searching for Store in lobby")
    process_keywords(driver, ['STORE'])

    print("Searching for back")
    process_keywords(driver, ['Back'])


def warehouse(driver, keyword=['Vehicle', 'Back']):
    print("Searching for warehouse in lobby")
    process_keywords(driver, ['Warehouse'])

    print("Searching for Weapons in warehouse after its found tap on back")
    process_keywords(driver, keyword)


def profile(driver, keywords=['Weapons', 'History', 'Overview', 'Back']):
    print('Searching for user name')
    process_keywords(driver, ['User'])
    process_keywords(driver, keywords)


if __name__ == "__main__":
    driver = setup_device()
    if driver:
        #login(driver)
        #store(driver)
        #warehouse(driver, keyword=['Weapons', 'Back'])
        profile(driver, keywords=['Weapons', 'History', 'Overview', 'Back'])
