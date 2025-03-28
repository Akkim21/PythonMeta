import time
import subprocess
from PIL import Image, ImageEnhance
from io import BytesIO
import base64
from appium import webdriver
from appium.options.android import UiAutomator2Options
import pytesseract
from skimage.metrics import structural_similarity as ssim
import numpy as np

# Explicitly mentioning the path for pytesseract
pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"

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

def send_text_via_adb(text):
    formatted_text = text.replace(" ", "%s")
    adb_command = f"/Users/mohamedakkim/Library/Android/sdk/platform-tools/adb shell input text {formatted_text}"
    
    try:
        subprocess.run(adb_command, shell=True, check=True)
        print(f"Text sent via ADB: {text}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send text via ADB: {e}")

def capture_and_compare(driver, reference_img_path, screenshot_path):
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at: {screenshot_path}")
    time.sleep(5)
    similarity = compare_images(reference_img_path, screenshot_path)
    return similarity

def capture_region_screenshot(driver, region, screenshot_path):
    screenshot = driver.get_screenshot_as_base64()
    screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))
    x, y, width, height = region
    cropped_image = screenshot.crop((x, y, x + width, y + height))
    cropped_image.save(screenshot_path)
    print(f"Screenshot of the region saved at: {screenshot_path}")

def compare_images(reference_img_path, current_img_path, threshold=80):
    ref_img = Image.open(reference_img_path).convert("L")
    curr_img = Image.open(current_img_path).convert("L")

    if ref_img.size != curr_img.size:
        curr_img = curr_img.resize(ref_img.size)

    ref_img_array = np.array(ref_img)
    curr_img_array = np.array(curr_img)

    similarity, _ = ssim(ref_img_array, curr_img_array, full=True)
    print(f"Image similarity: {similarity:.2f}")
    return similarity >= threshold

def capture_and_extract_text_with_data(driver, region=None):
    screenshot = driver.get_screenshot_as_base64()
    screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))
    
    if region:
        x, y, width, height = region
        screenshot = screenshot.crop((x, y, x + width, y + height))

    gray_image = screenshot.convert('L')
    enhancer = ImageEnhance.Contrast(gray_image)
    gray_image = enhancer.enhance(2)
    
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT, config=custom_config)
    
    # Collect all text in a single line and print it
    all_text = " ".join([word for word in data['text'] if word.strip() != ""])
    print(f"Extracted Text from Screen: {all_text}")
    
    return data

def tap_if_text_found(driver, target_text, tap_action=True, max_retries=5):
    retries = 0
    found = False
    
    while retries < max_retries and not found:
        data = capture_and_extract_text_with_data(driver)
        target_words = target_text.lower().split()

        for i, word in enumerate(data['text']):
            if all(part in word.lower() for part in target_words):
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
                break

        if not found:
            retries += 1
            print(f"Text '{target_text}' not found. Retrying {retries}/{max_retries}...")
            time.sleep(2)

    return found

def server_selection(driver):
    actions = [
        {"coords": (625, 296), "message": "Server Selection", "sleep_time": 2},
        {"coords": (596, 513), "message": "Server Selected", "sleep_time": 2},
        {"coords": (2810, 315), "message": "Server Launched", "sleep_time": 10},
        {"coords": (2020, 977), "message": "T & C Selected", "sleep_time": 2}
    ]
    
    target_texts = [
        {'target_text': 'Google', 'tap_action': True, 'sleep_time': 3},
        {'target_text': 'akkim@mayhem-studios.com', 'tap_action': True, 'sleep_time': 15}
    ]
    
    # Print out all the text found on the screen
    capture_and_extract_text_with_data(driver)
    
    for action in actions:
        driver.tap([action["coords"]])
        print(action["message"])
        time.sleep(action["sleep_time"])

    for target in target_texts:
        print(f"Searching for text: {target['target_text']}")
        tap_if_text_found(driver, target['target_text'], tap_action=target['tap_action'])
        time.sleep(target['sleep_time'])

def daily_login(driver):
    target_text = "TOMORROW"
    
    # Extract all text and print it out before proceeding
    capture_and_extract_text_with_data(driver)
    
    # Search for the target text 'TODAY'
    found = tap_if_text_found(driver, target_text, tap_action=False, max_retries=3)
    
    if found:
        # If 'TODAY' is found, continue with searching for the next target text (e.g., "CONTINUE")
        next_target_text = "CONTINUE"
        print(f"Searching for '{next_target_text}' after '{target_text}' was found.")
        
        # Perform the search and tap action for the next target text
        tap_if_text_found(driver, next_target_text, tap_action=True, max_retries=3)
        
        # Set flag to skip coordinate tap in game_initiate
        skip_coordinate_tap = True
    else:
        # If 'TODAY' is not found, print and skip this function
        print(f"Text '{target_text}' not found. Skipping daily login.")
        # Proceed to the game initiation if 'TODAY' is not found
        skip_coordinate_tap = False
        game_initiate(driver, skip_coordinate_tap)

def game_initiate(driver, skip_coordinate_tap=False):
    # Skip the coordinate tap if the daily_login was executed
    if not skip_coordinate_tap:
        tap_x5, tap_y5 = 2380, 1350
        driver.tap([(tap_x5, tap_y5)])
        print(f"Tapped on coordinates ({tap_x5}, {tap_y5})")
        time.sleep(3)
    
    target_texts = [
        {'target_text': 'TOM TestMap', 'tap_action': True, 'sleep_time': 3},
        {'target_text': 'CONTINUE', 'tap_action': True, 'sleep_time': 10}
    ]
    
    for target in target_texts:
        print(f"Searching for text: {target['target_text']}")
        tap_if_text_found(driver, target['target_text'], tap_action=target['tap_action'])
        time.sleep(target['sleep_time'])

def profile_validation(driver):
    driver.tap([(100, 100)])
    print("Profile tapped")
    time.sleep(3)

    target_text = "STATISTICS"
    tap_if_text_found(driver, target_text, tap_action=True)
    
    target_texts = [
        { 'target_text': 'CASUAL', 'tap_action': True, 'sleep_time': 3 },
        { 'target_text': 'OVERVIEW', 'tap_action': True, 'sleep_time': 2 },
        { 'target_text': 'WEAPONS', 'tap_action': True, 'sleep_time': 2 }
    ]
    
    for target in target_texts:
        target_text = target['target_text']
        tap_action = target['tap_action']
        sleep_time = target['sleep_time']
        
        tap_if_text_found(driver, target_text, tap_action=tap_action)
        time.sleep(sleep_time)

def wallet_validation(driver):
    region = (1070, 135, 872, 1149)
    screenshot_path_to_region = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/Lobby.png"
    time.sleep(10)
    
    reference_img_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/Screenshot_20250324_145628_Underworld Gang Wars - Beta.jpg"
    capture_and_compare(driver, reference_img_path, screenshot_path_to_region)
    
    if compare_images(reference_img_path, screenshot_path_to_region):
        print("✅ The region matches the reference image!")
    else:
        print("❌ The region does NOT match the reference image!")

def leaderboard_validation(driver):
    tap_x6, tap_y6 = 90, 885
    driver.tap([(tap_x6, tap_y6)])
    time.sleep(3)
    
    target_text = "No Leaderboards are currently active!"
    tap_if_text_found(driver, target_text, tap_action=False, max_retries=3)

def main():
    driver = setup_device()  # Setup device and start the app
    server_selection(driver)  # Call server selection
    daily_login(driver)
    game_initiate(driver, skip_coordinate_tap=False)

if __name__ == "__main__":
    main()
