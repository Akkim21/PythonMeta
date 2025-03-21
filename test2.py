import time
import subprocess
from PIL import Image
from io import BytesIO
import base64
import numpy as np
from appium import webdriver
from appium.options.android import UiAutomator2Options
import pytesseract
from skimage.metrics import structural_similarity as ssim
from PIL import ImageEnhance
from trio._highlevel_serve_listeners import SLEEP_TIME
from Rough import target_text, tap_if_text_found

# Explicitly mentioning the path 
pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"

def setup_device():
    """Setup Appium and launch the app."""
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

def send_text_via_adb(text):
    """Send text to a focused input field using ADB."""
    formatted_text = text.replace(" ", "%s")
    adb_command = "/Users/mohamedakkim/Library/Android/sdk/platform-tools/adb shell input text " + formatted_text
    
    try:
        subprocess.run(adb_command, shell=True, check=True)
        print(f"Text sent via ADB: {text}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send text via ADB: {e}")

def tap_action(driver, x, y, message, sleep_time=3):
    driver.tap([(x, y)])
    print(message)
    time.sleep(sleep_time)

def capture_region_screenshot(driver, region):
    """Capture a specific region of the screen."""
    screenshot = driver.get_screenshot_as_base64()
    screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))

    # Define the region (x, y, width, height)
    x, y, width, height = region
    cropped_image = screenshot.crop((x, y, x + width, y + height))

    # Return the cropped image
    return cropped_image

def capture_and_extract_text_with_data(driver):
    """Capture the entire screen and extract text with bounding box data using pytesseract."""
    screenshot = driver.get_screenshot_as_base64()
    screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))
    
    # Pre process the image: Convert to gray scale and increase contrast
    gray_image = screenshot.convert('L')
    enhancer = ImageEnhance.Contrast(gray_image)
    gray_image = enhancer.enhance(2)
    
    # Perform OCR with custom configuration for better accuracy
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT, config=custom_config)
    
    # Debug: Print OCR Data
    print("OCR Data:", data)
    
    return data

def tap_if_text_found(driver, target_text, tap_action=True, max_retries=5):
    """Search for the text and tap if found, or just verify the presence without tapping."""
    retries = 0
    found = False
    
    while retries < max_retries and not found:
        data = capture_and_extract_text_with_data(driver)
        
        # Split the target text into words for more flexible matching
        target_words = target_text.lower().split()  # Split the target text into words

        for i, word in enumerate(data['text']):
            # Check if all parts of the target text are present in the word
            if all(part in word.lower() for part in target_words):  
                print(f"Text '{target_text}' found at index {i}!")
                x = data['left'][i]
                y = data['top'][i]
                width = data['width'][i]
                height = data['height'][i]
                center_x = x + width // 2
                center_y = y + height // 2
                
                if tap_action:
                    driver.tap([(center_x, center_y)])
                    print(f"Tapped on the coordinates ({center_x}, {center_y})")
                found = True
                break  # Exit loop once the text is found and tapped or verified

        if not found:
            retries += 1
            print(f"Text '{target_text}' not found. Retrying {retries}/{max_retries}...")
            time.sleep(2)  # Optional: add a small delay before retrying

    if not found:
        print(f"Text '{target_text}' not found after {max_retries} retries.")
    return found

def server_selection(driver):
    
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
    
    target_texts = [
        
        { 'target_text': 'Google', 'sleep_time': 3},
        { 'target_text': 'akkim@mayhem-studios.com', 'sleep_time' : 3 }
        
        ]
    
    for target in target_texts:
        target_text = target['target_text']
        sleep_time = target['sleep_time']
        print(f"Searching for text: {target_text}")
        tap_if_text_found(driver, target_text)
        time.sleep(sleep_time)
    
 #  region = (1882, 279, 616, 893)
 #  print("Searching for text in region:", region)
 #  tap_if_text_found(driver, target_text)
 #    time.sleep(10)

def game_initiate(driver):
    
    target_text = "Battle Royale Dhantara"
    
 #   region = (0, 1219, 3088, 221)
    
 #   print("Searching for text in region:", region)
    tap_if_text_found(driver, target_text)
    time.sleep(10)
    
    tap_x21, tap_y21 = 2380, 1350
    driver.tap([(tap_x21, tap_y21)])
    print("Map screen tapped")
    time.sleep(2)
    
    target_text = "Continue"
    
    tap_if_text_found(driver, target_text)
    time.sleep(10)
    
    
    
def profile_validation(driver):
    
    # Tap on the profile section
    tap_x4, tap_y4 = 100, 100
    driver.tap([(tap_x4, tap_y4)])
    print("Profile tapped")
    time.sleep(3)
    
    # Target text to search and tap
    target_text = "History"
    tap_if_text_found(driver, target_text, tap_action=True)  # Tap on 'History' text
    
    # List of additional target texts with sleep time
    target_texts = [
        { 'target_text': 'SOLO|BR|DHANTARA Casual', 'tap_action': False, 'sleep_time': 3 }
    ]
    
    # Loop through each target and perform the specified action
    for target in target_texts:
        target_text = target['target_text']
        tap_action = target['tap_action']
        sleep_time = target['sleep_time']
        
        print(f"Searching for text: {target_text}")
        
        # Search and optionally tap on the text
        tap_if_text_found(driver, target_text, tap_action=tap_action)
        
        # Sleep after each search or action
        print(f"Sleeping for {sleep_time} seconds after searching '{target_text}'")
        time.sleep(sleep_time)  # Sleep after each target text search

    time.sleep(10)  # Optional: Sleep at the end for a longer delay if needed


def main():
    driver = setup_device()  # Setup device and start the app
    server_selection(driver)  # Call server selection
#    game_initiate(driver)     # Start game initiation
    profile_validation(driver)

if __name__ == "__main__":
    main()
