import subprocess
import time
import os
import xml.etree.ElementTree as ET
from appium import webdriver
from appium.options.android import UiAutomator2Options

# 1. Setup device and start the app with Appium
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

ADB_PATH = "/Users/mohamedakkim/Library/Android/sdk/platform-tools/adb"

def dump_ui_hierarchy():
    """Use ADB to dump the UI hierarchy and save it to ui.xml."""
    
    # Update the adb command to use the explicit path
    adb_command = f"{ADB_PATH} shell uiautomator dump /sdcard/ui.xml"
    pull_command = f"{ADB_PATH} pull /sdcard/ui.xml"
    
    # Run the adb command to dump the UI hierarchy
    adb_result = subprocess.run(adb_command, shell=True, check=True)
    
    if adb_result.returncode != 0:
        print("Failed to dump UI hierarchy using ADB.")
        return False

    # Pull the ui.xml file from the device to the local machine
    pull_result = subprocess.run(pull_command, shell=True, check=True)
    
    if pull_result.returncode != 0:
        print("Failed to pull the ui.xml file.")
        return False

    # Check if the file exists after pulling
    if not os.path.exists('ui.xml'):
        print("Error: ui.xml file not found after pulling!")
        return False

    print("UI hierarchy dumped and pulled successfully.")
    return True



# 3. Parse the UI hierarchy XML file and extract visible text
def parse_ui_hierarchy():
    """Parse the UI hierarchy XML file to extract text."""
    # Load and parse the XML
    tree = ET.parse('ui.xml')
    root = tree.getroot()

    # Extract all 'node' elements and their 'text' attributes
    texts = []
    for node in root.iter('node'):
        text = node.attrib.get('text')  # Extract text from the 'text' attribute
        if text:
            texts.append(text)

    return texts

# 4. Server Selection action method (just an example action)
def server_selection(driver):
    """Simulate server selection in the app."""
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
    time.sleep(25)

# 5. Validate UI Text

def validate_ui_text(driver):
    """Capture UI hierarchy and validate the extracted text."""
    if not dump_ui_hierarchy():
        print("Failed to capture and pull the UI hierarchy.")
        return False

    # Parse the XML to extract text
    texts = parse_ui_hierarchy()

    # Optionally, check for specific texts (like balance or other elements)
    for text in texts:
        if "wallet" in text.lower():
            print(f"Found wallet balance text: {text}")
            return True
    print("Wallet balance text not found!")
    return False


# 6. Main function to execute the whole flow
def main():
    driver = setup_device()  # Setup device and start the app

    # Perform server selection
    server_selection(driver)
    
    # Validate if the wallet balance text is found
    if validate_ui_text(driver):
        print("Test Passed!")
    else:
        print("Test Failed!")

    driver.quit()

if __name__ == "__main__":
    main()
