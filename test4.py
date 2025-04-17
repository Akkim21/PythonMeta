import os
import time
import google.generativeai as genai
import base64
import json
from PIL import Image
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
        return None  # Return None to indicate an error

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Take screenshot of the current screen
        screenshot_path = "current_screen.png"
        driver.save_screenshot(screenshot_path)

        # Encode the image
        with open(screenshot_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Construct the prompt for Gemini
        prompt = "Extract all text from this image. For each text element, provide the text content and its bounding box coordinates (x, y, width, height). Return the result as a JSON list of dictionaries where each dictionary has 'text' and 'bounding_box' keys. The 'bounding_box' should be a dictionary with 'x', 'y', 'width', and 'height' keys."

        # Prepare the image data for Gemini
        image_part = {"mime_type": "image/png", "data": encoded_image}

        # Send the request to Gemini
        response = model.generate_content([prompt, image_part])

        # Print the full response object and its text for debugging
        print(f"Full Response: {response}")
        if hasattr(response, 'text'):
            print(f"Response Text: {response.text}")
            gemini_response_text = response.text
        else:
            print("Response has no 'text' attribute.")
            return None

        # Remove Markdown code block delimiters and surrounding whitespace
        cleaned_response = gemini_response_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        # Print the cleaned response for debugging
        print(f"Cleaned Gemini Response: {cleaned_response}")

        try:
            extracted_data = json.loads(cleaned_response)
            # Print extracted data for debugging
            print(f"Extracted Data (JSON): {json.dumps(extracted_data, indent=2)}")
            return extracted_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Problematic JSON String: {cleaned_response}")
            return None

    except Exception as e:
        print(f"Error during text extraction: {e}")
        traceback.print_exc()
        return None


def adb_tap(x, y):
    """
    Use adb command to tap on the given coordinates (x, y).
    """
    try:
        # Tap on the coordinates using adb shell input tap
        subprocess.run(["adb", "shell", f"input tap {x} {y}"], check=True)
        print(f"Tapped on coordinates: ({x}, {y})")
    except Exception as e:
        print(f"Error during adb tap: {e}")


def server_selection(driver):
    """Performs server selection taps using adb."""
    try:
        adb_tap(625, 296)  # Tap on server selection
        print("Server Selection")
        time.sleep(3)

        adb_tap(596, 513)  # Tap on select server
        print("Server Selected")
        time.sleep(3)

        adb_tap(2810, 315)  # Tap to launch the server
        print("Server Launched")
        time.sleep(10)
    except Exception as e:
        print(f"Error during server selection: {e}")
        raise  # Re-raise the exception to be caught in main()


def main():
    """Main function to demonstrate app launching, text extraction, and tapping with bottom-left origin."""
    text_to_search = "Google"  # The text you want to find

    # Mobile App Automation Setup
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.no_reset = True

    driver = None
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

        # Take a screenshot
        screenshot_path = "current_screen.png"
        driver.save_screenshot(screenshot_path)

        # Get the height of the screenshot
        try:
            img = Image.open(screenshot_path)
            screen_height = img.height
        except Exception as e:
            print(f"Error getting screenshot dimensions: {e}")
            screen_height = None

        # Extract text and bounding boxes
        extracted_data = extract_text_with_bounding_boxes(driver)

        if extracted_data and screen_height is not None:
            for obj in extracted_data:
                if "text" in obj and obj["text"] == text_to_search:
                    print(f"Text '{text_to_search}' found at bounding box (top-left): {obj['bounding_box']}")
                    top_left_x = obj['bounding_box']['x']
                    top_left_y = obj['bounding_box']['y']
                    width = obj['bounding_box']['width']
                    height = obj['bounding_box']['height']

                    # Transform to bottom-left origin
                    bottom_left_x = top_left_x
                    bottom_left_y = screen_height - (top_left_y + height)

                    # Calculate center in bottom-left origin
                    center_x_bottom_left = bottom_left_x + width / 2
                    center_y_bottom_left = bottom_left_y + height / 2

                    # However, adb tap still uses top-left origin, so we need to convert back
                    tap_center_x = int(center_x_bottom_left)
                    tap_center_y = int(screen_height - center_y_bottom_left)

                    print(f"Tapping at center (bottom-left transformed back to top-left): ({tap_center_x}, {tap_center_y})")
                    adb_tap(tap_center_x, tap_center_y)
                    break
            else:
                print(f"Text '{text_to_search}' not found in the extracted data.")
        else:
            print("Failed to extract text and bounding boxes or get screen height.")

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
