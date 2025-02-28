import cv2


def main():
    # Open video capture (change the device index if necessary)
    cap = cv2.VideoCapture(0)  # Use 0 if it's the first video input device

    if not cap.isOpened():
        print("Error: Could not open video capture device.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Display the frame
        cv2.imshow("HDMI Capture", frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


def list_available_cameras():
    index = 0
    devices = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            devices.append(index)
        cap.release()
        index += 1

    print("Available camera indices:", devices)


if __name__ == "__main__":
    main()
