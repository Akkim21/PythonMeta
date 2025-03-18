import time
from PIL import Image
import numpy as np
from appium import webdriver
from appium.options.android import UiAutomator2Options  # Import correct options class

# Create an instance of UiAutomator2Options
options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "14"  # Your Android version
options.device_name = "Akkim-Galaxy S22 Ultra"  # Your device name
options.app_package = "com.mayhem.ugwob"  # Your app package
options.app_activity = "com.epicgames.ue4.GameActivity"  # Your app activity
options.no_reset = True  # Keep the app state after execution

# Start Appium session
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

# Perform a simple action (print screen title)
print("App Launched Successfully!")

time.sleep(10)

# 📌 Tap on specific coordinates (Replace with actual x, y)
tap_x, tap_y = 625, 296  # Example coordinates
driver.tap([(tap_x, tap_y)])
print("Sever selection")
time.sleep(2)

tap_x1, tap_y1 = 596, 513  # Example coordinates
driver.tap([(tap_x1, tap_y1)])
print("Server selected")
time.sleep(2)

tap_x2, tap_y2 = 2810, 315  # Example coordinates
driver.tap([(tap_x2, tap_y2)])
print("Logged")
time.sleep(20)

tap_x4, tap_y4 = 760, 1370  # Warehouse lobby
driver.tap([(tap_x4, tap_y4)])
print("Tapped warehouse lobby")
time.sleep(5)


tap_x4, tap_y4 = 2540, 1040  # Warehouse costume
driver.tap([(tap_x4, tap_y4)])
print("Tapped warehouse costume")
time.sleep(5)

# 📸 Take a full screenshot
screenshot_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/full_screen.png"
driver.save_screenshot(screenshot_path)
print(f"Screenshot saved at: {screenshot_path}")
time.sleep(5)

# 📌 Crop the screenshot to a specific region based on given x and y coordinates
def crop_image_by_coordinates(x1, y1, x2, y2):
    # Open the screenshot using Pillow
    full_img = Image.open(screenshot_path)

    # Crop the image to the given coordinates (x1, y1, x2, y2)
    cropped_img = full_img.crop((x1, y1, x2, y2))

    # Save the cropped image
    cropped_screenshot_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/cropped_screen.png"
    cropped_img.save(cropped_screenshot_path)
    print(f"Cropped screenshot saved at: {cropped_screenshot_path}")
    return cropped_screenshot_path

# Define the region to crop (top-left corner (x1, y1) to bottom-right corner (x2, y2))
x1, y1 = 1440, 244  # Example top-left coordinates
x2, y2 = 2360, 1270  # Example bottom-right coordinates

# Crop the image based on given coordinates
cropped_screenshot_path = crop_image_by_coordinates(x1, y1, x2, y2)

# 📌 Compare Screenshot with Reference Image
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

# 🔍 Validate against reference image
reference_image_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/cropped_screen4.png"
if compare_images(reference_image_path, cropped_screenshot_path):
    print("✅ The game screen matches the reference image!")
else:
    print("❌ The game screen does NOT match the reference image!")

# Quit the session
driver.quit()
