import os
import time
import google.generativeai as genai
import base64
import json
import traceback
import re
from appium import webdriver
from appium.options.android import UiAutomator2Options
import subprocess

def extract_text_with_bounding_boxes(driver, text_to_find=""):
    # ... (rest of the function remains the same)

def adb_tap(x, y):
    # ... (rest of the function remains the same)

def server_selection(driver):
    # ... (rest of the function remains the same)

def main():
    """Main function to demonstrate app launching, text extraction, and tapping."""
    text_to_search = "Google"  # The text you want to find

    # Mobile App Automation Setup
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.no_reset = True

    try:
        driver = webdriver.Remote("http://127.0.0.1:4723", options=options)  # Start the session
    except Exception as e:
        print(f"Error setting up Appium driver: {e}")
        return  # Exit if the driver fails to initialize

    try:
        print("App Launched Successfully!")
        time.sleep(10)

        # Perform server selection
        server_selection(driver)

        # Extract text and bounding boxes
        extracted_text_json, _ = extract_text_with_bounding_boxes(driver, text_to_search)
        print("Extracted Text and Bounding Boxes (JSON):")
        print(extracted_text_json)

        # Parse the JSON and search for 'Google'
        try:
            jarray = json.loads(extracted_text_json)
            found_coordinates = None
            for obj in jarray:
                if "text" in obj and obj["text"].lower() == text_to_search.lower():
                    found_coordinates = obj
                    break

            if found_coordinates:
                print(f"The text '{text_to_search}' was found at coordinates: {found_coordinates}")
                # Perform the tap using adb
                x = found_coordinates["x"] + found_coordinates["width"] / 2
                y = found_coordinates["y"] + found_coordinates["height"] / 2
                adb_tap(x, y)  # Tap on the coordinates using adb
            else:
                print(f"The text '{text_to_search}' was not found in the extracted data.")

        except json.JSONDecodeError as json_err:
            print(f"Error decoding JSON: {json_err}")
            traceback.print_exc()

    except Exception as e:
        print(f"An error occurred: {e}")  # Catch errors during the main process
        traceback.print_exc()  # Print the traceback for detailed debugging
    finally:
        try:
            driver.quit()  # Ensure the driver is quit, even if errors occur
        except Exception:
            print("Error quitting driver (may already be quit).")

if __name__ == "__main__":
    main()