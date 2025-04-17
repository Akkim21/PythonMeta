import time
import subprocess
from PIL import Image
from io import BytesIO
import base64
import numpy as np
from appium import webdriver
from appium.options.android import UiAutomator2Options
from skimage.metrics import structural_similarity as ssim

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
    
    reference_image_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/NewLogin.png"
    screenshot_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Loginscreen.png"
    
    # Check if the screenshot matches the reference image
    return capture_and_compare(driver, reference_image_path, screenshot_path)

def login_action(driver):
    # First tap - Disclaimer action
    tap_x3, tap_y3 = 2020, 977
    driver.tap([(tap_x3, tap_y3)])
    print("T & C Selected")
    time.sleep(2)

    # Second tap - Logged as Guest action
    tap_x4, tap_y4 = 2178, 620
    driver.tap([(tap_x4, tap_y4)])
    print("Logged as Guest")
    time.sleep(10)
    
    # Validate Disclaimer Image
    reference_image_path_for_disclaim = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/Disclaim.jpg"
    screenshot_path_for_disclaim = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Disclaim.png"
    
    # Capture and compare the disclaimer image
    if capture_and_compare(driver, reference_image_path_for_disclaim, screenshot_path_for_disclaim):
        # If image matches, proceed with the next action
        tap_x18, tap_y18 = 1540, 970
        driver.tap([(tap_x18, tap_y18)])
        print("Disclaimer accepted")
        time.sleep(5)
    else:
        print("❌ Disclaimer image did not match. Skipping the disclaimer acceptance.")
        return  # Skip the rest of the steps if disclaimer doesn't match
    time.sleep(10)

    # Validate Gang Image
    reference_image_path_for_gang = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/Gang.jpg"
    screenshot_path_for_gang = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Gang.png"
    
    # Capture and compare the Gang image
    if capture_and_compare(driver, reference_image_path_for_gang, screenshot_path_for_gang):
        # If image matches, proceed with the next action
        tap_x19, tap_y19 = 475, 869
        driver.tap([(tap_x19, tap_y19)])
        print("Tapped gang Selection screen")
        time.sleep(5)

        # Proceed to select Gang
        tap_x20, tap_y20 = 1717, 960
        driver.tap([(tap_x20, tap_y20)])
        print("Gang Selected")
        time.sleep(5)
    else:
        print("❌ Gang image did not match. Skipping the Gang selection.")
        return  # Skip the rest of the steps if Gang doesn't match
    time.sleep(10)
 
def social_merge(driver):
    tap_x17, tap_y17 = 3000, 150
    driver.tap([(tap_x17, tap_y17)])
    print("Tapped settings")
    time.sleep(3)
    
    tap_x15, tap_y15 = 2540, 70
    driver.tap([(tap_x15, tap_y15)])
    print("Tapped socail merge CTA")
    time.sleep(3)
    
    tap_x16, tap_y16 = 1740, 890
    driver.tap([(tap_x16, tap_y16)])
    print("Tapped social popoup")
    time.sleep(3)
    
    tap_x17, tap_y17 = 1790, 990
    driver.tap([(tap_x17, tap_y17)])
    print("Social merge - Gmail Selected")
    time.sleep(15)

def logout_action(driver):
    
    tap_x5, tap_y5 = 3000, 150
    driver.tap([(tap_x5, tap_y5)])
    print("Tapped settings")
    time.sleep(3)

    tap_x6, tap_y6 = 2895, 70
    driver.tap([(tap_x6, tap_y6)])
    print("Tapped Logout CTA")
    time.sleep(5)

    # Now take screenshot and validate again
    reference_image_path_for_logout = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/Logout_popup.jpg"
    screenshot_path_for_logout = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_logout_popup.png"
    capture_and_compare(driver, reference_image_path_for_logout, screenshot_path_for_logout)
    
    tap_x7, tap_y7 = 1720, 960
    driver.tap([(tap_x7, tap_y7)])
    print("Logout Popup")
    time.sleep(10)

def gmail_login(driver):
    """Simulate Gmail login action."""
    tap_x8, tap_y8 = 2020, 977
    driver.tap([(tap_x8, tap_y8)])
    print("T & C Selected")
    time.sleep(2)

    tap_x9, tap_y9 = 2200, 750
    driver.tap([(tap_x9, tap_y9)])
    print("Log with Gmail")
    time.sleep(2)

    tap_x10, tap_y10 = 1600, 490
    driver.tap([(tap_x10, tap_y10)])
    print("Gmail Selected")
    time.sleep(15)
    
    reference_image_path_for_gang = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/Gang.jpg"
    screenshot_path_for_gang = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Gang.png"
    
    # Capture and compare the Gang image
    if capture_and_compare(driver, reference_image_path_for_gang, screenshot_path_for_gang):
        # If image matches, proceed with the next action
        tap_x19, tap_y19 = 475, 869
        driver.tap([(tap_x19, tap_y19)])
        print("Tapped gang Selection screen")
        time.sleep(5)

        # Proceed to select Gang
        tap_x20, tap_y20 = 1717, 960
        driver.tap([(tap_x20, tap_y20)])
        print("Gang Selected")
        time.sleep(5)
    else:
        print("❌ Gang image did not match. Skipping the Gang selection.")
        return  # Skip the rest of the steps if Gang doesn't match
    time.sleep(10)
    
    reference_image_path_for_logout = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/FTUE_1.jpg"
    screenshot_path_for_logout = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_FTUE.png"
    capture_and_compare(driver, reference_image_path_for_logout, screenshot_path_for_logout)
    time.sleep(10)

def leaderboard_function(driver):
    # Tap on leaderboard
    tap_x14, tap_y14 = 90, 885
    driver.tap([(tap_x14, tap_y14)])
    print("Leaderboard tapped")
    time.sleep(5)

    # Define the region for the screenshot (example: x=100, y=200, width=400, height=300)
    region = (538, 287, 2012, 965)  # Adjust this to the region you need
    screenshot_path_for_region = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Leaderboard_Region.png"
    
    # Capture the region of the leaderboard and save it
    capture_region_screenshot(driver, region, screenshot_path_for_region)
    
    # Compare the region screenshot with the reference image
    reference_image_path_for_leaderboard = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/ActiveBoard.jpg"
    
    if compare_images(reference_image_path_for_leaderboard, screenshot_path_for_region):
        print("✅ The region matches the reference image!")
    else:
        print("❌ The region does NOT match the reference image!")
    
    time.sleep(3)
    
    # Tap to go back to the lobby
    tap_x15, tap_y15 = 140, 90
    driver.tap([(tap_x15, tap_y15)])
    print("Back to lobby")
    time.sleep(5)
           
def chat_function(driver, text):
    tap_x10, tap_y10 = 95, 1260
    driver.tap([(tap_x10, tap_y10)])
    print("Tapped chat")
    time.sleep(3)
    
    tap_x13, tap_y13 = 420, 1350
    driver.tap([(tap_x13, tap_y13)])
    print("Tapped input field")
    time.sleep(2)
    
    input_x, input_y = 860, 520
    driver.tap([(input_x, input_y)])
    print("Tapped Keyboard")
    time.sleep(2)
    
    send_text_via_adb(text)
    print(f"Text sent: {text}")
    time.sleep(3)
    
    tap_x11, tap_y11 = 2630, 1320
    driver.tap([(tap_x11, tap_y11)])
    print("Passing value")
    time.sleep(3)
    
    tap_x12, tap_y12 = 1120, 1355
    driver.tap([(tap_x12, tap_y12)])
    print("Text Sent")
    time.sleep(10)
    
    tap_x19, tap_y19 = 3000, 150
    driver.tap([(tap_x19, tap_y19)])
    print("Tapped out of chat bound")
    time.sleep(3)
 
def warehouse(driver):
    
    tap_x28, tap_y28 = 720, 1390
    driver.tap([(tap_x28, tap_y28)])
    print("Warehouse Tapped")
    time.sleep(3)
    
    tap_x29, tap_y29 = 2555, 1040
    driver.tap([(tap_x29, tap_y29)])
    print("Top Tapped")
    time.sleep(3)
    
    # Define the region for the screenshot (example: x=100, y=200, width=400, height=300)
    region = (1432, 310, 934, 952)  # Adjust this to the region you need
    screenshot_path_for_region = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Empty_Warehouse.png"
    
    capture_region_screenshot(driver, region, screenshot_path_for_region)
    time.sleep(3)
    
    tap_x30, tap_y30 = 140, 90
    driver.tap([(tap_x30, tap_y30)])
    print("Back to lobby from warehouse")
    time.sleep(3)
    
def store_purchase(driver):
    # Store Tapped
    tap_action(driver, 360, 1390, "Store Tapped")
    
    # Outfit in store
    tap_action(driver, 2820, 490, "Outfit in store")
    
    # Top Tapped
    tap_action(driver, 2555, 1040, "Top Tapped")
    
    # 1st Top selected (unique)
    tap_action(driver, 1600, 620, "1st Top selected")
    
    # tap to buy, confirm buy, tap to continue, and cancel social merge (common actions)
    common_tap_coordinates = [
        (2800, 1380, "tap to buy"),
        (2300, 1180, "Confirm buy"),
        (1550, 1239, "tap to continue from back to store"),
        (2030, 460, "Cancel social merge")
    ]
    
    for coord in common_tap_coordinates:
        tap_action(driver, coord[0], coord[1], coord[2])

    # 2nd Top selected (unique)
    tap_action(driver, 2090, 610, "2nd Top selected")
    
    # Repeating common taps for 2nd top
    for coord in common_tap_coordinates:
        tap_action(driver, coord[0], coord[1], coord[2])

    # 3rd Top selected (unique)
    tap_action(driver, 1910, 970, "3rd Top selected")
    
    # Repeating common taps for 3rd top
    for coord in common_tap_coordinates:
        tap_action(driver, coord[0], coord[1], coord[2])
    
    # Back to lobby
    tap_action(driver, 140, 90, "Back to lobby")
    
def purchase_validation(driver):

    tap_x28, tap_y28 = 720, 1390
    driver.tap([(tap_x28, tap_y28)])
    print("Warehouse Tapped")
    time.sleep(3)
    
    tap_x29, tap_y29 = 2555, 1040
    driver.tap([(tap_x29, tap_y29)])
    print("Top Tapped")
    time.sleep(3)
    
    region = (1432, 310, 934, 952)  # Adjust this to the region you need
    screenshot_path_for_region = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Asset_In_Warehouse.png"
    
    capture_region_screenshot(driver, region, screenshot_path_for_region)
    time.sleep(3)
    
    # Compare the region screenshot with the reference image
    reference_image_path_for_Empty_Warehouse = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Empty_Warehouse.png"
    
    if compare_images(reference_image_path_for_Empty_Warehouse, screenshot_path_for_region):
        print("✅ The region matches the reference image!")
    else:
        print("❌ The region does NOT match the reference image!")
    
    time.sleep(3)
    
    tap_x47, tap_y47 = 140, 90
    driver.tap([(tap_x47, tap_y47)])
    print("back to lobby")
    time.sleep(3)
    
def map_selection(driver):
    tap_x21, tap_y21 = 2380, 1350
    driver.tap([(tap_x21, tap_y21)])
    print("Map screen tapped")
    time.sleep(2)
    
    tap_x22, tap_y22 = 500, 500
    driver.tap([(tap_x22, tap_y22)])
    print("BR selected")
    time.sleep(2)
    
    tap_x23, tap_y23 = 2880, 1400
    driver.tap([(tap_x23, tap_y23)])
    print("Map confirmed")
    time.sleep(2)
    
def game_initiate(driver):
    tap_x20, tap_y20 = 2760, 1370
    driver.tap([(tap_x20, tap_y20)])
    print("Game Initiated")
    time.sleep(180)
    
    tap_x27, tap_y27 = 590, 495
    driver.tap([(tap_x27, tap_y27)])
    print("Parachute opened")
    time.sleep(150)
    
def ingame_setting(driver):
    tap_x24, tap_y24 = 2455, 170
    driver.tap([(tap_x24, tap_y24)])
    print("Tapped in-game setting")
    time.sleep(3)
    
    tap_x25, tap_y25 = 2895, 70
    driver.tap([(tap_x25, tap_y25)])
    print("Tapped back Lobby")
    time.sleep(5)
    
    tap_x26, tap_y26 = 1720, 960
    driver.tap([(tap_x26, tap_y26)])
    print("Back to lobby")
    time.sleep(3)
    
def main():
    driver = setup_device()  # Setup device and start the app

    # Perform server selection, login, logout, and Gmail login
    if server_selection(driver):  # If server selection is successful, proceed to login
        login_action(driver)
    else:
        print("Skipping login action due to mismatch in server selection screen.")
    
 #   social_merge(driver)
   # logout_action(driver)
   # gmail_login(driver)
   # leaderboard_function(driver)
  #  chat_function(driver, "Underworld Gang Wars")
    warehouse(driver)
    store_purchase(driver)
    purchase_validation(driver)
  #  map_selection(driver)
  #  game_initiate(driver)
   # ingame_setting(driver)
    
    
if __name__ == "__main__":
    main()
