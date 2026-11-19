# Sports Timing & Performance Tracking

A computer vision proof-of-concept system that automates athlete detection, identity tracking, virtual start/finish line crossing detection, elapsed time measurement, and average speed calculation from stationary camera footage.


https://github.com/user-attachments/assets/2bd879b3-85de-4aea-8e79-fa134952ddc8



---

## System Architecture

The processing pipeline runs locally on CPU using a modular Python architecture:

1. **Video Ingestion (`OpenCV`)** - Reads stationary camera footage and extracts FPS and frame dimensions.
2. **Interactive Calibration (`src/calibration.py`)** - Prompts for real-world course distance (meters) and lets the user click Start and Finish line positions directly on Frame 1 to compute a pixel-to-meter scale.
3. **Athlete Detection (`YOLOv8n`)** - Detects people (`class 0`) in each frame.
4. **Multi-Frame Tracking (`ByteTrack`)** - Assigns persistent tracking IDs across frames and records bounding-box center trajectories.
5. **Event Detection (`src/video.py`)** - Detects directional crossings (left-to-right or right-to-left) across the calibrated virtual boundaries while preventing duplicate triggers.
6. **Time & Speed Calculation** - Converts crossing frame numbers into timestamps (`frame / fps`) to compute elapsed sprint time and average speed (`m/s` and `km/h`).
7. **Structured Output (`src/main.py`)** - Renders annotated playback (`output/detected_video.mp4`) and exports machine-readable results (`output/results.json`).

---

## Project Structure

```text
Sports Timing & Performance Tracking/
├── data/
│   └── test_video.mp4          # Input stationary-camera footage
├── output/
│   ├── detected_video.mp4      # Annotated output video with overlays
│   └── results.json            # Structured timing & speed results
├── src/
│   ├── __init__.py
│   ├── calibration.py          # Distance prompt & interactive on-screen line calibration
│   ├── config.py               # Central directory configuration
│   ├── detector.py             # YOLOv8n model loader and ByteTrack wrapper
│   ├── main.py                 # End-to-end pipeline entry point
│   └── video.py                # Tracking loop, crossing logic, overlays, and metrics
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup & Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/UEAv/Sports_Timing_-_Performance_Tracking.git
   cd Sports_Timing_-_Performance_Tracking
   ```

2. **Create and activate a virtual environment**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Add a test video**
   Place a stationary-camera video inside `data/` named `test_video.mp4`.

---

## Usage

Run the pipeline from the project root:

```powershell
python src\main.py
```

1. Enter the real-world distance between your Start and Finish markers (in meters) when prompted in the terminal.
2. In the **Calibration** window:
   - **Left-click** to place the green **START** line.
   - **Left-click** to place the red **FINISH** line.
   - Press **`r`** to reset, **`Enter`** to confirm, or **`q`** to cancel.
3. Watch the live tracking playback (press **`q`** to stop early).
4. Review outputs in `output/detected_video.mp4` and `output/results.json`.

### Example JSON Output (`output/results.json`)

```json
{
    "video_file": "test_video.mp4",
    "fps": 24.0,
    "calibration": {
        "start_line_x": 776,
        "finish_line_x": 408,
        "distance_meters": 12.0,
        "pixels_per_meter": 30.67
    },
    "athletes": [
        {
            "track_id": 1,
            "start_frame": 46,
            "finish_frame": 134,
            "start_timestamp_sec": 1.917,
            "finish_timestamp_sec": 5.583,
            "elapsed_time_sec": 3.667,
            "avg_speed_mps": 3.27,
            "avg_speed_kmh": 11.78
        }
    ]
}
```

---

## Known Limitations & Future Improvements

* **Frame-Rate Quantization Error:** At 24 FPS, each frame spans ~41.7 ms, creating up to ~83.3 ms of worst-case timing uncertainty across two crossings. Higher-FPS cameras (60-120+ FPS) and sub-frame linear interpolation would significantly improve precision.
* **Perspective Distortion:** Linear pixel-to-meter scaling is accurate for average speed between two markers and side-on perpendicular cameras, but angled camera setups require 4-point homography for accurate frame-by-frame displacement and instantaneous speed.
* **Body Reference Point:** Crossings currently use the bounding-box center rather than a specific anatomical landmark (e.g., torso/chest via pose estimation).
* **Empirical Validation:** Formal accuracy and repeatability benchmarking against a physical reference timing system (such as laser timing gates) has not yet been conducted.
* **Planned Extensions:** Intermediate split-time lines, FastAPI endpoint for web platform integration, and Docker containerization.
