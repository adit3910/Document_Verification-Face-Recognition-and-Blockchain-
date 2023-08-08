import cv2
import pyzbar.pyzbar as pyzbar

def read_aadhaar_qr_code(image_path):
    # Load the Aadhaar card image
    image = cv2.imread(image_path)

    # Convert the image to grayscale for QR code detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect and decode QR codes
    qr_codes = pyzbar.decode(gray)

    if qr_codes:
        # QR code data is present
        return 1
    else:
        # No QR code data found
        return 2

# Example usage
image_path = r'F:\project_possible\QR-code.png'
result = read_aadhaar_qr_code(image_path)

if result == 1:
    print("QR code data is present.")
else:
    print("No QR code data found.")
