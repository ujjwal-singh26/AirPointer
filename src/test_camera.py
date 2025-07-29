import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Can't receive frame (stream end?). Exiting ...")
        break

    cv2.imshow('Webcam Test', frame)
    if cv2.waitKey(1) == 27:  # Press ESC to close
        break

cap.release()
cv2.destroyAllWindows()
