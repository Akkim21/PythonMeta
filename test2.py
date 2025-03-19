import time
import subprocess
from PIL import Image
from io import BytesIO
import base64
import numpy as np
from appium import webdriver
from appium.options.android import UiAutomator2Options
from skimage.metrics import structural_similarity as ssim
import pytesseract
from Rough import target_text

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

def capture_and_compare(driver, reference_img_path, screenshot_path):
    """Take a screenshot and compare it with a reference image."""
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at: {screenshot_path}")
    time.sleep(5)
    
    similarity = compare_images(reference_img_path, screenshot_path)
    if similarity:
        print("✅ The current screen matches the reference image!")
        return True
    else:
        print("❌ The current screen does NOT match the reference image!")
        return False

def capture_region_screenshot(driver, region, screenshot_path):
    
    # Take a full screenshot using Appium
    screenshot = driver.get_screenshot_as_base64()
    screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))

    # Define the region (x, y, width, height)
    x, y, width, height = region
    cropped_image = screenshot.crop((x, y, x + width, y + height))

    # Save the cropped screenshot
    cropped_image.save(screenshot_path)
    print(f"Screenshot of the region saved at: {screenshot_path}")
    
def compare_images(reference_img_path, current_img_path, threshold=0.9):
    """Compare two images using SSIM (Structural Similarity Index)."""
    ref_img = Image.open(reference_img_path).convert("L")  # Convert to grayscale
    curr_img = Image.open(current_img_path).convert("L")  # Convert to grayscale

    if ref_img.size != curr_img.size:
        curr_img = curr_img.resize(ref_img.size)

    ref_img_array = np.array(ref_img)
    curr_img_array = np.array(curr_img)

    similarity, _ = ssim(ref_img_array, curr_img_array, full=True)
    print(f"Image similarity: {similarity:.2f}")
    return similarity >= threshold

def send_text_via_adb(text):
    """Send text to a focused input field using ADB."""
    # Format the text properly for ADB input (replace spaces with %s)
    formatted_text = text.replace(" ", "%s")
    
    # Use the absolute path to adb if adb is not in the system PATH
    adb_command = "/Users/mohamedakkim/Library/Android/sdk/platform-tools/adb shell input text " + formatted_text
    
    try:
        subprocess.run(adb_command, shell=True, check=True)
        print(f"Text sent via ADB: {text}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send text via ADB: {e}")

def tap_action(driver, x, y, message, sleep_time=3):
    driver.tap([(x, y)])
    print(message)
    time.sleep(3)
    
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
    
    for i, word in enumerate(data['text']):
        if target_text.lower() in word.lower():  # Case insensitive comparison
            print(f"Text '{target_text}' found at index {i}!")
            x = data['left'][i]
            y = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]
            center_x = x + width // 2
            center_y = y + height // 2
            driver.tap([(center_x, center_y)])
            print(f"Tapped on the coordinates ({center_x}, {center_y})")
            return True
    print(f"Text '{target_text}' not found.")
    return False

def server_selection(driver):
    """Server selection process with an early exit if already logged in."""
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
    
    reference_image_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/NewLogin.png"
    screenshot_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Loginscreen.png"
    
    if capture_and_compare(driver, reference_image_path, screenshot_path):
        time.sleep(3)
        tap_x33, tap_y33 = 2020, 977
        driver.tap([(tap_x33, tap_y33)])
        print("T & C Selected")
        time.sleep(2)
        
        target_text = "Guest"
        if tap_if_text_found(driver, target_text):  # If "Guest" is found and tapped
            print("Guest login successful!")
            return True  # Indicate that the user is logged in as Guest
    return False  # Return False if server selection or text tap fails

def game_initiate(driver):
    target_text = "Start"
    if tap_if_text_found(driver, target_text):
        time.sleep(10)
    
    tap_x20, tap_y20 = 2760, 1370
    driver.tap([(tap_x20, tap_y20)])
    print("Game Initiated")
    time.sleep(180)
    
    tap_x27, tap_y27 = 590, 495
    driver.tap([(tap_x27, tap_y27)])
    print("Parachute opened")
    time.sleep(150)

def main():
    driver = setup_device()  # Setup device and start the app
    logged_in = server_selection(driver)

    if logged_in:
        print("User is logged in as Guest. Proceeding with game initiation.")
        game_initiate(driver)  # Only initiate the game if logged in as guest
    else:
        print("Server selection failed or Guest login failed.")
    game_initiate(driver)
if __name__ == "__main__":
    main()