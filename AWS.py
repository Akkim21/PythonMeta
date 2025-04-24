import boto3
import json

# Initialize AWS Textract client
textract_client = boto3.client('textract', region_name='us-east-1')

def extract_text_and_coords(pdf_document):
    # Open the document and read it
    with open(pdf_document, 'rb') as document:
        response = textract_client.detect_document_text(
            Document={'Bytes': document.read()}
        )
        print(response)
    # Create a list to store the extracted text and coordinates
    extracted_data = []

    # You may want to adjust the width and height based on your image size
    image_width = 3088  # Replace with your image width
    image_height = 1440  # Replace with your image height

    # Process the blocks in the response
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":  # Check for SELECTION_ELEMENT block type
            if "Text" in item:  # Ensure there's text in the block
                text = item["Text"]
                # Coordinates for the bounding box of the text
                bounding_box = item["Geometry"]["BoundingBox"]

                # Convert to actual coordinates (multiplying by image width and height)
                left = int(bounding_box["Left"] * image_width)
                top = int(bounding_box["Top"] * image_height)
                width = int(bounding_box["Width"] * image_width)
                height = int(bounding_box["Height"] * image_height)

                # Append data with text and bounding box (X, Y, W, H)
                extracted_data.append({
                    "text": text,
                    "bounding_box": {
                        "X": left,
                        "Y": top,
                        "W": width,
                        "H": height
                    }
                })

    # Return the extracted data as a JSON array
    return json.dumps(extracted_data, indent=4)


# Example of using the function
pdf_document = "/Users/mohamedakkim/PycharmProjects/PythonMeta/Screenshot_20250424_144209.jpg"
extracted_text = extract_text_and_coords(pdf_document)

# Output the extracted text and coordinates in JSON format
print("Extracted JSON data:")
print(extracted_text)
