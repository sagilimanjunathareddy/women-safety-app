import cv2

def capture_photo(filename="assets/photo.jpg"):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
        print(f"📸 Photo captured to {filename}")
    cap.release()
    cv2.destroyAllWindows()
