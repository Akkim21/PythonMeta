import time
from PIL import Image
import numpy as np
from appium import webdriver
from appium.options.android import UiAutomator2Options

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
time.sleep(10)  # Method to put on sleep

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

# Method to take screenshot
screenshot_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/Screenshots/current_screen.png"
driver.save_screenshot(screenshot_path)
print(f"Screenshot saved at: {screenshot_path}")
time.sleep(5)

# Method to Compare Screenshot with Reference Image
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
    from skimage.metrics import structural_similarity as ssim
    similarity, _ = ssim(ref_img_array, curr_img_array, full=True)

    print(f"Image similarity: {similarity:.2f}")
    return similarity >= threshold

# Validate against reference image
reference_image_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/NewLogin.png"
if compare_images(reference_image_path, screenshot_path):
    print("✅ The game screen matches the reference image!")
else:
    print("❌ The game screen does NOT match the reference image!")

# Additional taps
tap_x3, tap_y3 = 2020, 977 
driver.tap([(tap_x3, tap_y3)])
print("T & C Selected")
time.sleep(2)

tap_x1, tap_y1 = 2178, 620 
driver.tap([(tap_x1, tap_y1)])
print("Logged as Guest")
time.sleep(15)

# Quit the session
driver.quit()
