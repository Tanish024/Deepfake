"""
Deepfake Shield - Preprocessing Pipeline
Extracts frames from video and crops faces using MediaPipe.
"""

import cv2
import mediapipe as mp

# Initialize MediaPipe Face Detection
# model_selection=1 is for full-range (faces further away)
try:
    face_detection = mp.solutions.face_detection.FaceDetection(
        model_selection=1, 
        min_detection_confidence=0.5
    )
except Exception as e:
    print(f"Error initializing MediaPipe Face Detection: {e}")

def extract_frames(video_path, num_frames=15):
    """
    Extracts a fixed number of evenly spaced frames from a video.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            cap.release()
            return []
            
        step = max(total_frames // num_frames, 1)
        frames = []
        
        for i in range(num_frames):
            target_frame_idx = min(i * step, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame_idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
                
        cap.release()
        return frames
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return []

def crop_face(frame, target_size=(224, 224)):
    """
    Detects the most prominent face in a frame and crops it to the target size.
    Returns the cropped face as a numpy array, or None if no face is found.
    """
    try:
        # MediaPipe expects RGB images
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        
        if results.detections:
            # Use the first confidently detected face
            bbox = results.detections[0].location_data.relative_bounding_box
            h, w, _ = frame.shape
            
            # Convert relative coordinates to absolute pixel values
            x_min = int(bbox.xmin * w)
            y_min = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            # Ensure bounding box is within frame boundaries
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(w, x_min + width)
            y_max = min(h, y_min + height)
            
            face_crop = frame[y_min:y_max, x_min:x_max]
            
            # Ensure the crop is valid
            if face_crop.size > 0:
                return cv2.resize(face_crop, target_size)
                
        return None
    except Exception as e:
        print(f"Error cropping face: {e}")
        return None

def process_video(video_path, num_frames=15, target_size=(224, 224)):
    """
    Full pipeline: extracts frames from a video and returns cropped faces.
    """
    try:
        frames = extract_frames(video_path, num_frames)
        faces = []
        
        for frame in frames:
            face = crop_face(frame, target_size)
            if face is not None:
                faces.append(face)
                
        return faces
    except Exception as e:
        print(f"Error processing video: {e}")
        return []
