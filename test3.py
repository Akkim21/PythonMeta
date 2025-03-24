import time
import subprocess
from PIL import Image, ImageEnhance
from io import BytesIO
import base64
from appium import webdriver
from appium.options.android import UiAutomator2Options
import pytesseract
from Rough import target_text
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
    time.sleep(10)  # Wait for app to launch
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
    
def compare_images(reference_img_path, current_img_path, threshold=80):
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

def capture_and_extract_text_with_data(driver):
    
    screenshot = driver.get_screenshot_as_base64()
    screenshot = Image.open(BytesIO(base64.b64decode(screenshot)))
    
    # Preprocess the image: Convert to grayscale and increase contrast
    gray_image = screenshot.convert('L')
    enhancer = ImageEnhance.Contrast(gray_image)
    gray_image = enhancer.enhance(2)
    
    # Perform OCR with custom configuration for better accuracy
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT, config=custom_config)
    
    return data

def tap_if_text_found(driver, target_text, tap_action=True, max_retries=5):
    
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
    # List of actions for tapping coordinates and performing actions
    actions = [
        {"coords": (625, 296), "message": "Server Selection", "sleep_time": 2},
        {"coords": (596, 513), "message": "Server Selected", "sleep_time": 2},
        {"coords": (2810, 315), "message": "Server Launched", "sleep_time": 10},
        {"coords": (2020, 977), "message": "T & C Selected", "sleep_time": 2}
    ]
    
    # List of target texts to search and tap or verify
    target_texts = [
        {'target_text': 'Google', 'tap_action': True, 'sleep_time': 3},
        {'target_text': 'akkim@mayhem-studios.com', 'tap_action': True, 'sleep_time': 15}
    ]
    
    # Execute actions
    for action in actions:
        driver.tap([action["coords"]])
        print(action["message"])
        time.sleep(action["sleep_time"])

    # Execute target text searches
    for target in target_texts:
        print(f"Searching for text: {target['target_text']}")
        tap_if_text_found(driver, target['target_text'], tap_action=target['tap_action'])
        time.sleep(target['sleep_time'])

def game_initiate(driver):
    
    target_text = "Battle Royale Dhantara"
    tap_if_text_found(driver, target_text, tap_action= True)
    time.sleep(10)

    driver.tap([(2380, 1350)])
    print("Map screen tapped")
    time.sleep(2)

    target_text = "Continue"
    tap_if_text_found(driver, target_text, tap_action= True)
    time.sleep(10)

def profile_validation(driver):
    
    driver.tap([(100, 100)])
    print("Profile tapped")
    time.sleep(3)

    target_text = "STATISTICS"
    tap_if_text_found(driver, target_text, tap_action= True)  # Tap on 'History' text
    
    target_texts = [
        { 'target_text': 'CASUAL', 'tap_action': True, 'sleep_time': 3 },
        { 'target_text': 'OVERVIEW', 'tap_action': True, 'sleep_time': 2 },
        { 'target_text': 'WEAPONS', 'tap_action': True, 'sleep_time': 2 }
    ]
    
    for target in target_texts:
        target_text = target['target_text']
        tap_action = target['tap_action']
        sleep_time = target['sleep_time']
        
        print(f"Searching for text: {target_text}")
        
        # Search and optionally tap on the text
        tap_if_text_found(driver, target_text, tap_action=tap_action)
        
        print(f"Sleeping for {sleep_time} seconds after searching '{target_text}'")
        time.sleep(sleep_time)
        
def wallet_validation(driver):
   
    
    
    region = (1070, 135, 872, 1149)  # Adjust this to the region you need
    screenshot_path_to_region= "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/Lobby.png"
    
    
#    capture_region_screenshot(driver, region, screenshot_path_for_region)
    time.sleep(10)
    
    # Compare the region screenshot with the reference image
    reference_img_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/Screenshot_20250324_145628_Underworld Gang Wars - Beta.jpg"
    capture_and_compare(driver, reference_img_path, screenshot_path_to_region)
    
    if compare_images(reference_img_path, screenshot_path_to_region):
        print("✅ The region matches the reference image!")
    else:
        print("❌ The region does NOT match the reference image!")
    
    
    

def main():
    driver = setup_device()  # Setup device and start the app
    server_selection(driver)  # Call server selection
#    game_initiate(driver)  # Start game initiation
 #   profile_validation(driver)  # Perform profile validation
    wallet_validation(driver)
if __name__ == "__main__":
    main()
