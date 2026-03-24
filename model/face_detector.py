import cv2
import os
import urllib.request

# Absolute path relative to this file — never depends on CWD
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CASCADE_FILE_PATH = os.path.join(_THIS_DIR, "haarcascade_frontalface_default.xml")
HAAR_CASCADE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"

# Module-level cache so the classifier is only loaded once
_face_cascade = None


def _get_face_cascade():
    """Returns the cached CascadeClassifier, downloading/loading it if necessary."""
    global _face_cascade
    if _face_cascade is not None:
        return _face_cascade

    if not os.path.exists(CASCADE_FILE_PATH):
        try:
            print("Downloading Haar Cascade model...")
            urllib.request.urlretrieve(HAAR_CASCADE_URL, CASCADE_FILE_PATH)
            print("Download complete.")
        except Exception as e:
            print("Error downloading cascade file:")
            print(e)
            return None

    _face_cascade = cv2.CascadeClassifier(CASCADE_FILE_PATH)
    if _face_cascade.empty():
        print("Error: CascadeClassifier failed to load from", CASCADE_FILE_PATH)
        _face_cascade = None
    return _face_cascade


def crop_face(frame):
    """
    Detects the first face in the frame using Haar Cascades.
    Crops the face and resizes it to 224x224 pixels.

    Args:
        frame (numpy array): The image frame to process.

    Returns:
        numpy array: The cropped and resized face, or None if no face is detected.
    """
    try:
        face_cascade = _get_face_cascade()
        if face_cascade is None:
            return None

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detected_faces = face_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(detected_faces) == 0:
            return None

        x_coord, y_coord, width, height = detected_faces[0]
        cropped_face_img = frame[y_coord: y_coord + height, x_coord: x_coord + width]
        resized_face_img = cv2.resize(cropped_face_img, (224, 224))
        return resized_face_img

    except Exception as e:
        print("Error during face cropping:")
        print(e)
        return None
