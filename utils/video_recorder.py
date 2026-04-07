import cv2
import datetime

def record_video(output_path="assets/emergency_video.avi", duration=10):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Camera not available")
        return False

    # Video settings
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

    start_time = datetime.datetime.now()

    print("🎥 Recording Emergency Video...")

    while (datetime.datetime.now() - start_time).seconds < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    cap.release()
    out.release()

    print(f"✅ Video saved: {output_path}")
    return True
