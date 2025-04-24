import json
import easyocr

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])


# Function to extract text from the image and return it as a list of JSON objects
def extract_text_from_image(image_path):
    """Extracts text from the image and returns it as a list of JSON objects."""
    result = reader.readtext(image_path)

    # Create a list to store the extracted text and coordinates
    extracted_data = []

    for detection in result:
        text = detection[1]
        coordinates = detection[0]
        # Convert coordinates to native Python int
        data = {
            "text": text,
            "coordinates": {
                "X": int(coordinates[0][0]),
                "Y": int(coordinates[0][1]),
                "W": int(coordinates[2][0] - coordinates[0][0]),
                "H": int(coordinates[2][1] - coordinates[0][1])
            }
        }
        extracted_data.append(data)

    # Print the extracted data in JSON format
    json_data = json.dumps(extracted_data, indent=4)
    print(json_data)
    return extracted_data


# Example usage
image_path = "/Users/mohamedakkim/PycharmProjects/PythonMeta/Screenshots/SS_Loginscreen.png"  # Path to your image
extract_text_from_image(image_path)
