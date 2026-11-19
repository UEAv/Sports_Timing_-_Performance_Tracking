import cv2
import os
from collections import defaultdict
from detector import track_athlete


def _crossed_line(prev_x, curr_x, line_x, moving_right_to_left):
    if moving_right_to_left:
        return prev_x > line_x and curr_x <= line_x
    return prev_x < line_x and curr_x >= line_x


def process_and_save_video(video_path, output_path, model, start_x, finish_x, distance_meters):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    trajectories = defaultdict(list)
    event_frames = defaultdict(lambda: {"start": None, "finish": None})
    frames_processed = 0

    # Derive running direction and pixel-to-meter scale from calibration
    moving_right_to_left = start_x > finish_x
    pixel_span = abs(start_x - finish_x)
    pixels_per_meter = pixel_span / distance_meters
    print(f"Calibration -> Span: {pixel_span} px | Distance: {distance_meters} m | Scale: {pixels_per_meter:.2f} px/m")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = track_athlete(model, frame)

        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if box.id is not None:
                track_id = int(box.id[0])
                color = (255, 0, 0)

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                trajectories[track_id].append((center_x, center_y))

                if len(trajectories[track_id]) >= 2:
                    prev_x = trajectories[track_id][-2][0]
                    curr_x = trajectories[track_id][-1][0]

                    if _crossed_line(prev_x, curr_x, start_x, moving_right_to_left):
                        if event_frames[track_id]["start"] is None:
                            event_frames[track_id]["start"] = frames_processed

                    if _crossed_line(prev_x, curr_x, finish_x, moving_right_to_left):
                        if event_frames[track_id]["finish"] is None:
                            event_frames[track_id]["finish"] = frames_processed

                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                points = trajectories[track_id]
                for i in range(1, len(points)):
                    cv2.line(frame, points[i - 1], points[i], (0, 255, 255), 2)
            else:
                track_id = -1
                color = (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw calibrated lines
        cv2.line(frame, (start_x, 0), (start_x, height), (0, 255, 0), 2)
        cv2.putText(frame, "START", (start_x + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.line(frame, (finish_x, 0), (finish_x, height), (0, 0, 255), 2)
        cv2.putText(frame, "FINISH", (finish_x + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display Time & Speed once both crossings are recorded
        for t_id, events in event_frames.items():
            if events["start"] is not None and events["finish"] is not None:
                elapsed_time = (events["finish"] - events["start"]) / fps
                if elapsed_time > 0:
                    speed_mps = distance_meters / elapsed_time
                    speed_kmh = speed_mps * 3.6
                else:
                    speed_mps, speed_kmh = 0.0, 0.0

                cv2.putText(frame, f"Athlete {t_id} Time: {elapsed_time:.2f} sec", (50, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
                cv2.putText(frame, f"Avg Speed: {speed_mps:.2f} m/s ({speed_kmh:.2f} km/h)", (50, 125),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)

        out.write(frame)
        cv2.imshow("Sports Timing Playback", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        frames_processed += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Build structured results dictionary
    athlete_results = []
    print("\n--- Final Event Report ---")
    for t_id, events in event_frames.items():
        if events["start"] is not None and events["finish"] is not None:
            start_frame = events["start"]
            finish_frame = events["finish"]
            start_time = start_frame / fps
            finish_time = finish_frame / fps
            elapsed_time = finish_time - start_time
            speed_mps = distance_meters / elapsed_time if elapsed_time > 0 else 0.0
            speed_kmh = speed_mps * 3.6

            print(f"ID {t_id}: Time = {elapsed_time:.2f} s | Avg Speed = {speed_mps:.2f} m/s ({speed_kmh:.2f} km/h)")

            athlete_results.append({
                "track_id": t_id,
                "start_frame": start_frame,
                "finish_frame": finish_frame,
                "start_timestamp_sec": round(start_time, 3),
                "finish_timestamp_sec": round(finish_time, 3),
                "elapsed_time_sec": round(elapsed_time, 3),
                "avg_speed_mps": round(speed_mps, 2),
                "avg_speed_kmh": round(speed_kmh, 2),
            })

    return {
        "video_file": os.path.basename(video_path),
        "fps": fps,
        "calibration": {
            "start_line_x": start_x,
            "finish_line_x": finish_x,
            "distance_meters": distance_meters,
            "pixels_per_meter": round(pixels_per_meter, 2),
        },
        "athletes": athlete_results,
    }