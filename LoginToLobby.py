import time
from PIL import Image  # Ensure Pillow is correctly installed
import numpy as np
from appium import webdriver
from appium.options.android import UiAutomator2Options
from skimage.metrics import structural_similarity as ssim

# Helper function to take screenshot and compare
def capture_and_compare(reference_img_path, screenshot_path, threshold=0.9):
    # Take screenshot
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at: {screenshot_path}")
    time.sleep(5)

    # Compare with reference image
    similarity = compare_images(reference_img_path, screenshot_path)
    if similarity:
        print("✅ The game screen matches the reference image!")
    else:
        print("❌ The game screen does NOT match the reference image!")

def compare_images(reference_img_path, current_img_path, threshold=0.9):
    # Open images using Pillow and convert to grayscale
    ref_img = Image.open(reference_img_path).convert("L")  # Convert to grayscale
    curr_img = Image.open(current_img_path).convert("L")  # Convert to grayscale

    # Resize to match dimensions if needed
    if ref_img.size != curr_img.size:
        curr_img = curr_img.resize(ref_img.size)

    # Convert images to numpy arrays for comparison
    ref_img_array = np.array(ref_img)
    curr_img_array = np.array(curr_img)

    # Compute Structural Similarity Index (SSIM)
    similarity, _ = ssim(ref_img_array, curr_img_array, full=True)
    print(f"Image similarity: {similarity:.2f}")
    return similarity >= threshold

# Device Caps (Setting up Appium capabilities)

options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "14"
options.device_name = "Akkim-Galaxy S22 Ultra"
options.app_package = "com.mayhem.ugwob"
options.app_activity = "com.epicgames.ue4.GameActivity"
options.no_reset = True

# Start Appium driver session
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
print("App Launched Successfully!")
time.sleep(10)  # Wait for app to launch

# Action simulation and Driver method
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

# Define reference image path and screenshot path
reference_image_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/NewLogin.png"
screenshot_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/SS_Loginscreen.png"
capture_and_compare(reference_image_path, screenshot_path) # Use the helper function to capture screenshot and compare

# Additional taps
tap_x3, tap_y3 = 2020, 977
driver.tap([(tap_x3, tap_y3)])
print("T & C Selected")
time.sleep(2)

tap_x4, tap_y4 = 2178, 620
driver.tap([(tap_x4, tap_y4)])
print("Logged as Guest")
time.sleep(15)

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
capture_and_compare(reference_image_path_for_logout, screenshot_path_for_logout) # Use the helper function to capture screenshot and compare

tap_x7, tap_y7 = 1720, 960
driver.tap([(tap_x7, tap_y7)])
print("Logout Popup")
time.sleep(10)

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
time.sleep(2)

