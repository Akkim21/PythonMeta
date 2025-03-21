import pytesseract
from PIL import Image

# Set the path to tesseract executable explicitly
pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"  # Update with the correct path

# Sample image file
image = Image.open("/Users/mohamedakkim/eclipse-workspace/PythonMeta/references/gang.jpg")  # Update this with your image file

# Extract text from the image
text = pytesseract.image_to_string(image)
print("Extracted Text:", text)
