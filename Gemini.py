import cv2
import pytesseract
from PIL import Image
import json

# Configure Tesseract (replace with your Tesseract path if necessary)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"

def find_clickable_areas_and_text(image_path):
    """Finds clickable areas and associated text."""
    try:
        img_cv = cv2.imread(image_path)
        img_pil = Image.open(image_path)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        clickable_areas = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > 1000: # Adjust threshold for area size
                roi = img_pil.crop((x, y, x + w, y + h))
                text = pytesseract.image_to_string(roi).strip()

                clickable_areas.append({
                    "bounding_box": [x, img_pil.height - (y + h), x + w, img_pil.height - y], # Bottom left origin
                    "text": text
                })

        return clickable_areas
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage
image_path = "/Users/mohamedakkim/eclipse-workspace/PythonMeta/References/Logout_popup.jpg" # Replace with your image file
results = find_clickable_areas_and_text(image_path)

if results:
    json_output = json.dumps(results, indent=2)
    print(json_output)
    with open("clickable_areas.json", "w") as outfile:
        outfile.write(json_output)