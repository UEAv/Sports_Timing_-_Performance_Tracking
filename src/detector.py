from ultralytics import YOLO

def load_model():
    print("Loading YOLOv8 nano model...")
    # This will automatically download the model file (yolov8n.pt) the first time it runs
    model = YOLO("yolov8n.pt") 
    return model


def detect_athlete(model, frame):
    # Run the model on a single frame.
    # classes=[0] tells YOLO to ONLY look for humans, ignoring cars, animals, etc.
    # verbose=False stops YOLO from flooding our terminal with text for every single frame.
    results = model(frame, classes=[0], verbose=False)
    
    # We return the first result because we are only passing in one frame at a time
    return results[0]


def track_athlete(model, frame):
    # .track() runs detection AND tracking.
    # persist=True is crucial! It tells the tracker to remember IDs from previous frames.
    # tracker="bytetrack.yaml" tells it to use the ByteTrack algorithm.
    results = model.track(frame, persist=True, classes=[0], verbose=False, tracker="bytetrack.yaml")
    
    return results[0]