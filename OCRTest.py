import os
import time
import json
import subprocess
import requests
from PIL import Image
from appium import webdriver
from appium.options.android import UiAutomator2Options
import shutil

API_KEY = 'K81674033288957'  # Static API key

# Function to compress the screenshot to ensure it is below 1MB without resizing the image dimensions
def compress_image(input_path, output_path):
    """Compress the image without resizing, ensuring it is under 1MB"""
    file_size_kb = os.path.getsize(input_path) / 1024  # Convert file size to KB

    if file_size_kb > 1024:  # If the file is greater than 1MB
        print(f"Original size: {int(file_size_kb)} KB. Compressing...")
        with Image.open(input_path) as img:
            img = img.convert("RGB")  # Convert to RGB to handle transparency (e.g., for PNGs)
            img.save(output_path, format="JPEG", quality=80)  # Compress and save as JPEG with quality 80

        new_size_kb = os.path.getsize(output_path) / 1024  # Get the new size in KB
        print(f"Compressed size: {int(new_size_kb)} KB")
    else:  # If the image is already under 1MB
        shutil.copy(input_path, output_path)  # No compression needed if it's under 1MB
        print(f"Image is already under 1MB ({int(file_size_kb)} KB). No compression applied.")

    return output_path


# Function to take a screenshot
def take_screenshot(driver, screenshot_path="screenshot.png"):
    """Captures a screenshot"""
    try:
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None


# Function to send the image to OCR.Space API for text extraction
def ocr_space_file(filename, api_key):
    """Function to extract text and its coordinates from an image using OCR.Space API."""
    print("Sending image to OCR.Space API...")
    with open(filename, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data={
                'apikey': api_key,
                'language': 'eng',
                'isOverlayRequired': 'true'
            },
            timeout=60
        )

    if r.status_code != 200:
        print(f"Error: Received status code {r.status_code} from OCR.Space API")
        return None

    try:
        result = r.json()
        print(f"OCR response received successfully.")
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response")
        print(f"Response text: {r.text}")
        return None

    if 'OCRExitCode' not in result:
        print(f"Error: OCRExitCode not found in the response")
        return None

    if result['OCRExitCode'] == 1:
        if 'TextOverlay' in result['ParsedResults'][0]:
            parsed_results = result['ParsedResults'][0]['TextOverlay']['Lines']
            output = []
            for line in parsed_results:
                for word in line['Words']:
                    text = word['WordText']
                    x = word['Left']
                    y = word['Top']
                    width = word['Width']
                    height = word['Height']
                    output.append({
                        'text': text,
                        'bounding_box': {
                            'x': x,
                            'y': y,
                            'width': width,
                            'height': height
                        }
                    })
            # Return the extracted data as JSON without printing
            return output
        else:
            print("Error: TextOverlay not found in the response.")
            return None
    else:
        print(f"Error: {result['ErrorMessage']}")
        return None


# Function to find the reference word from the extracted text data
def find_text_and_get_coords(extracted_text_info, reference_word):
    """Searches for reference words in the extracted text info and returns their coordinates."""
    print(f"Searching for reference word: {reference_word}")
    if extracted_text_info:
        for item in extracted_text_info:
            if 'text' in item and reference_word.lower() in item['text'].lower() and 'bounding_box' in item:
                bbox = item['bounding_box']
                print(f"Found '{reference_word}' at: {bbox}")
                return bbox['x'], bbox['y'], bbox['width'], bbox['height']
    print(f"Reference word '{reference_word}' not found.")
    return None


# Function to simulate an ADB tap at the given coordinates
def adb_tap(x, y):
    """Simulates a tap at the given x, y coordinates using ADB."""
    try:
        adb_command = f"adb shell input tap {int(x)} {int(y)}"
        subprocess.run(adb_command, shell=True, check=True)
        print(f"Tapped at coordinates: ({int(x)}, {int(y)}) using ADB.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing ADB tap: {e}")
    except FileNotFoundError:
        print("Error: ADB command not found.")
    except Exception as e:
        print(f"An unexpected error occurred during ADB tap: {e}")


# Main function to execute the steps
def main():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Akkim-Galaxy S22 Ultra"
    options.app_package = "com.mayhem.ugwob"
    options.app_activity = "com.epicgames.ue4.GameActivity"
    options.no_reset = True

    driver = None
    try:
        driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    except Exception as e:
        print(f"Error setting up Appium driver: {e}")
        return

    try:
        print("App Launched Successfully!")
        time.sleep(5)

        # Step 1: Take a screenshot
        screenshot_path = take_screenshot(driver)

        if screenshot_path:
            # Step 2: Compress the screenshot to below 1MB (no resizing, only quality compression)
            compressed_image_path = "compressed_screenshot.jpg"
            compressed_image_path = compress_image(screenshot_path, compressed_image_path)

            if compressed_image_path:
                # Step 3: Extract text from the image using OCR.Space API
                extracted_text_info = ocr_space_file(compressed_image_path, 'K81674033288957')

                if extracted_text_info:
                    # Step 4: Print the extracted text in JSON array list format (only once)
                    print(f"Extracted Data:\n{json.dumps(extracted_text_info, indent=4)}")

                    # Step 5: Search for the reference word
                    reference_word = "x"
                    text_coords = find_text_and_get_coords(extracted_text_info, reference_word)

                    # Step 6: Tap if reference word found
                    if text_coords:
                        tap_x = text_coords[0] + text_coords[2] // 2
                        tap_y = text_coords[1] + text_coords[3] // 2
                        print(
                            f"Found '{reference_word}' at (x={text_coords[0]}, y={text_coords[1]}), tapping at ({tap_x}, {tap_y})")
                        adb_tap(tap_x, tap_y)
                    else:
                        print(f"Reference word '{reference_word}' not found in extracted text.")
                else:
                    print("Failed to extract text from the image.")
            else:
                print("Failed to compress image.")
        else:
            print("Failed to take screenshot.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            print("Error quitting driver.")


if __name__ == "__main__":
    main()
