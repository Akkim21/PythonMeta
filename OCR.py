import requests
import json


def ocr_space_file(filename, api_key):
    """
    Function to extract text and its coordinates from an image using OCR.Space API.
    :param filename: Path to the image file to be processed.
    :param api_key: API key for OCR.Space.
    :return: JSON array with text and coordinates (x, y, width, height) from the image.
    """
    with open(filename, 'rb') as f:
        # Send POST request to OCR.Space API with 'isOverlayRequired=true'
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data={
                'apikey': api_key,
                'language': 'eng',  # Change language if needed, e.g., 'spa' for Spanish
                'isOverlayRequired': 'true'  # Request the word-level coordinates
            }
        )

    # Check the API response status
    if r.status_code != 200:
        print(f"Error: Received status code {r.status_code} from OCR.Space API")
        return None

    # Parsing the response JSON
    try:
        result = r.json()
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response")
        print(f"Response text: {r.text}")
        return None

    # Check if the API has returned the expected structure
    if 'OCRExitCode' not in result:
        print(f"Error: OCRExitCode not found in the response")
        print(f"Response: {result}")
        return None

    if result['OCRExitCode'] == 1:
        # Check if the TextOverlay is included
        if 'TextOverlay' in result['ParsedResults'][0]:
            parsed_results = result['ParsedResults'][0]['TextOverlay']['Lines']
            output = []

            # Extract text and coordinates from the response
            for line in parsed_results:
                for word in line['Words']:
                    text = word['WordText']
                    x = word['Left']
                    y = word['Top']
                    width = word['Width']
                    height = word['Height']

                    # Format the result as a dictionary with the new 'bounding_box' format
                    output.append({
                        'text': text,
                        'bounding_box': {
                            'x': x,
                            'y': y,
                            'width': width,
                            'height': height
                        }
                    })
            return json.dumps(output, indent=4)
        else:
            print("Error: TextOverlay not found in the response.")
            return None
    else:
        print(f"Error: {result['ErrorMessage']}")
        return None


def main():
    # Specify the path to your reference image (replace 'your_image.png' with the actual path)
    image_path = '/Users/mohamedakkim/PycharmProjects/PythonMeta/lo.jpg'  # Replace with the path to your reference image

    # Replace with your OCR.Space API key
    api_key = 'K81674033288957'  # Get your API key from OCR.Space

    # Perform OCR on the image and get extracted text and coordinates
    extracted_data = ocr_space_file(image_path, api_key)

    if extracted_data:
        print(f"Extracted Data:\n{extracted_data}")
    else:
        print("No text extracted or an error occurred.")


if __name__ == "__main__":
    main()
