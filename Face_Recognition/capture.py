import cv2

video_capture = cv2.VideoCapture(0)
_, frame = video_capture.read()
captured_image_path = 'captured_image.png'
print(frame)
cv2.imwrite(captured_image_path, frame)