import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")


def run_live():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not found")
        return

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        results = model(frame)

        annotated = results[0].plot()

        cv2.imshow(
            "NeuroTrace Live Detection",
            annotated
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_live()