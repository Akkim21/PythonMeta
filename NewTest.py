import os
import time
import google.generativeai as genai
import base64
import json
from PIL import Image, ImageEnhance
import pytesseract
import traceback
import re
from appium import webdriver
from appium.options.android import UiAutomator2Options
import subprocess

def extract_text_with_bounding_boxes(driver):
    """
    Extracts text and bounding box coordinates from the current screen of the mobile app
    using the Google Gemini API. Returns a JSON list of dictionaries.
    """
    api_key = os.getenv('API_KEY')
    if not api_key:
        print("Error: API Key is missing. Please set the GOOGLE_API_KEY environment variable.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        screenshot_path = "current_screen.png"
        driver.save_screenshot(screenshot_path)
        with open(screenshot_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        prompt = "Extract all text from this image. For each text element, provide the text content and its bounding box coordinates (x, y, width, height). Return the result as a JSON list of dictionaries where each dictionary has 'text' and 'bounding_box' keys. The 'bounding_box' should be a dictionary with 'x', 'y', 'width', and 'height' keys."
        image_part = {"mime_type": "image/png", "data": encoded_image}
        response = model.generate_content([prompt, image_part])
        if hasattr(response, 'text'):
            cleaned_response = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                extracted_data = json.loads(cleaned_response)
                return extracted_data
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                return None
        else:
            print("Response has no 'text' attribute.")
            return None
    except Exception as e:
        print(f"Error during text extraction: {e}")
        traceback.print_exc()
        return None

def adb_tap(x, y):
    """Uses adb command to tap on the given coordinates (x, y)."""
    try:
        subprocess.run(["adb", "shell", f"input tap {x} {y}"], check=True)
        print(f"Tapped on coordinates: ({x}, {y})")
    except Exception as e:
        print(f"Error during adb tap: {e}")

def server_selection(driver):
    """Performs server selection taps using adb."""
    try:
        adb_tap(625, 296)
        print("Server Selection")
        time.sleep(3)
        adb_tap(596, 513)
        print("Server Selected")
        time.sleep(3)
        adb_tap(2810, 315)
        print("Server Launched")
        time.sleep(10)
    except Exception as e:
        print(f"Error during server selection: {e}")
        raise

def find_tappable_area_and_tap(driver, text_to_find):
    """
    Extracts text, identifies potential tappable areas based on keywords,
    and taps the center of the bounding box if the reference text is found.
    """
    screenshot_path = "current_screen.png"
    driver.save_screenshot(screenshot_path)
    extracted_data = extract_text_with_bounding_boxes(driver)

    if extracted_data:
        print("--- Gemini Extracted JSON Data ---")
        print(json.dumps(extracted_data, indent=2))
        print("--- End of Gemini JSON Data ---")

        for obj in extracted_data:
            if "text" in obj and obj["text"] == text_to_find and "bounding_box" in obj:
                # Heuristic: Check if the text is a common button keyword
                if re.search(r"(Login|STORE|OK|Cancel|Submit|Continue|Guest|Google|START|JOIN)", obj["text"], re.IGNORECASE):
                    bbox = obj["bounding_box"]
                    center_x = int(bbox["x"] + bbox["width"] / 2)
                    center_y = int(bbox["y"] + bbox["height"] / 2)
                    print(f"Found potential tappable '{text_to_find}'. Tapping at: ({center_x}, {center_y})")
                    adb_tap(center_x, center_y)
                    return True  # Indicate that the text was found and tapped
                else:
                    print(f"Found '{text_to_find}' but it doesn't seem like a primary tappable button.")
        else:
            print(f"Text '{text_to_find}' not found by Gemini.")
    else:
        print("Failed to extract text from Gemini.")
    return False  # Indicate that the text was not found or tapped

def main():
    """Main function to extract text and tap on a tappable area containing the reference text."""
    text_to_find = "Google"

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.no_reset = True

    driver = None
    appium_url = "http://127.0.0.1:4723"
    try:
        driver = webdriver.Remote(appium_url, options=options)
    except Exception as e:
        print(f"Error setting up Appium driver: {e}")
        return

    try:
        print("App Launched Successfully!")
        time.sleep(10)
        server_selection(driver)

        if find_tappable_area_and_tap(driver, text_to_find):
            print(f"Successfully found and tapped '{text_to_find}'.")
        else:
            print(f"Could not find or tap '{text_to_find}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            print("Error quitting driver.")

if __name__ == "__main__":
    main()