import cv2


def get_course_distance():
    """Prompt the user for the real-world distance between Start and Finish lines."""
    while True:
        user_input = input("Enter the real-world distance between Start and Finish (in meters): ").strip()
        try:
            distance = float(user_input)
            if distance > 0:
                return distance
            print("Distance must be greater than 0. Try again.")
        except ValueError:
            print("Invalid number. Please enter a numeric value (e.g., 10 or 15.5).")


def calibrate_lines(video_path):
    """Display the first frame and let the user click START and FINISH vertical lines."""
    cap = cv2.VideoCapture(video_path)
    ret, base_frame = cap.read()
    cap.release()

    if not ret:
        print(f"Error: Could not read first frame from {video_path}")
        return None

    height, width = base_frame.shape[:2]
    clicks = []
    window_name = "Calibration - Click START then FINISH"

    def on_mouse_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicks) < 2:
            clicks.append(x)

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse_click)

    while True:
        preview = base_frame.copy()

        # Draw instructions based on current calibration step
        if len(clicks) == 0:
            msg = "Step 1: Left-click to place START line"
        elif len(clicks) == 1:
            msg = "Step 2: Left-click to place FINISH line (or press 'r' to reset)"
        else:
            msg = "Press ENTER to confirm | 'r' to reset | 'q' to cancel"

        cv2.putText(preview, msg, (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

        # Draw Start line (Green)
        if len(clicks) >= 1:
            cv2.line(preview, (clicks[0], 0), (clicks[0], height), (0, 255, 0), 2)
            cv2.putText(preview, f"START ({clicks[0]}px)", (clicks[0] + 10, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Draw Finish line (Red)
        if len(clicks) == 2:
            cv2.line(preview, (clicks[1], 0), (clicks[1], height), (0, 0, 255), 2)
            cv2.putText(preview, f"FINISH ({clicks[1]}px)", (clicks[1] + 10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow(window_name, preview)
        key = cv2.waitKey(20) & 0xFF

        if key == ord('r'):
            clicks.clear()
        elif key in (13, 32) and len(clicks) == 2:  # ENTER or SPACE
            if clicks[0] == clicks[1]:
                print("Start and Finish cannot be at the exact same pixel. Resetting.")
                clicks.clear()
                continue
            break
        elif key == ord('q'):
            cv2.destroyWindow(window_name)
            return None

    cv2.destroyWindow(window_name)
    return clicks[0], clicks[1]