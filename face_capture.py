import cv2
print(cv2.__version__)

# Load OpenCV's built-in face detector
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

# Start webcam
cap = cv2.VideoCapture(0)

print("Press 'c' to capture face, 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Draw a box around the face
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Webcam - Face Detector", frame)

    key = cv2.waitKey(1) & 0xFF

    # Capture the face
    if key == ord('c'):
        if len(faces) == 0:
            print("No face detected!")
        else:
            x, y, w, h = faces[0]
            face_crop = frame[y:y + h, x:x + w]

            cv2.imwrite("captured_face.jpg", face_crop)
            print("Face saved as captured_face.jpg")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


