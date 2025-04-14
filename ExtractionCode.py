import os
import google.generativeai as genai
import base64
import json
import traceback


def extract_text_with_bounding_boxes(image_path):
    """
    Extracts text and bounding box coordinates from an image using the Google Gemini API.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: A JSON string representing a list of dictionaries, where each dictionary
              contains the extracted text and its bounding box coordinates.
              Returns an empty JSON list on error.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: API Key is missing. Please set the GOOGLE_API_KEY environment variable.")
        return json.dumps([])

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')  # Use gemini-1.5-flash

        # Encode the image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Construct the prompt
        prompt = "Extract all text from this image. For each text element, provide the text content and its bounding box coordinates (x, y, width, height). Return the result as a JSON list of dictionaries."

        # Prepare the image data as a part
        image_part = {"mime_type": "image/jpeg", "data": encoded_image}  # Or "image/png"

        # Send the request using generate_content
        response = model.generate_content([prompt, image_part])
        gemini_response_text = response.text

        # Print the raw response for debugging
        print(f"Raw Gemini Response: {gemini_response_text}")

        # Process the response to create a JSON string
        extracted_data = []
        try:
            parsed_response = json.loads(gemini_response_text)

            if isinstance(parsed_response, list):
                for item in parsed_response:
                    if all(key in item for key in ["text", "x", "y", "width", "height"]):
                        extracted_data.append({
                            "text": item["text"],
                            "x": item["x"],
                            "y": item["y"],
                            "width": width,
                            "height": height,
                        })
                    elif "text" in item and "bounds" in item:  # Handle "bounds"
                        bounds_str = item["bounds"]
                        bounds = bounds_str.replace("[", "").replace("]", ",").split(",")
                        if len(bounds) == 4:
                            try:
                                x1, y1, x2, y2 = map(int, bounds)
                                width = x2 - x1
                                height = y2 - y1
                                extracted_data.append({
                                    "text": item["text"],
                                    "x": x1,
                                    "y": y1,
                                    "width": width,
                                    "height": height,
                                })
                            except ValueError:
                                print(f"Skipping item with invalid bounds: {item}")
                        else:
                            print(f"Skipping item with malformed bounds: {item}")
                    else:
                        print(f"Skipping item with missing keys: {item}")

            json_output = json.dumps(extracted_data)
            return json_output

        except json.JSONDecodeError:
            print("Error: Gemini response was not in JSON format. Cannot extract data.")
            print(f"Gemini response text: {gemini_response_text}")  # Print the response
            return json.dumps([])
        except Exception as e:
            print(f"Error processing Gemini response: {e}")
            traceback.print_exc()
            return json.dumps([])

    except Exception as e:
        print(f"Error during text extraction: {e}")
        traceback.print_exc()
        return json.dumps([])


def main():
    """Main function to demonstrate text extraction."""
    # Use a sample image. Replace with the path to your image file.
    image_file = "/Users/mohamedakkim/PycharmProjects/PythonMeta/References/NewLogin.png"

    extracted_text_json = extract_text_with_bounding_boxes(image_file)
    print("Extracted Text and Bounding Boxes (JSON):")
    print(extracted_text_json)


if __name__ == "__main__":
    main()

