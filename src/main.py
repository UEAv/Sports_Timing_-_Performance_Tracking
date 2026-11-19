import json
import os
from config import DATA_DIR, OUTPUT_DIR
from calibration import get_course_distance, calibrate_lines
from video import process_and_save_video
from detector import load_model


def main():
    video_path = os.path.join(DATA_DIR, "test_video.mp4")
    output_path = os.path.join(OUTPUT_DIR, "detected_video.mp4")
    json_path = os.path.join(OUTPUT_DIR, "results.json")

    print("--- Course Calibration ---")
    distance_meters = get_course_distance()
    lines = calibrate_lines(video_path)

    if lines is None:
        print("Calibration cancelled. Exiting.")
        return

    start_x, finish_x = lines

    print("\n--- Loading AI Model ---")
    model = load_model()

    print("\n--- Processing Video with YOLO ---")
    results = process_and_save_video(video_path, output_path, model, start_x, finish_x, distance_meters)

    if results is not None:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        print(f"\nSaved structured results to: {json_path}")


if __name__ == "__main__":
    main()