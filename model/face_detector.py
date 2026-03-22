import cv2
import os
import urllib.request

HAAR_CASCADE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
CASCADE_FILE_PATH = "haarcascade_frontalface_default.xml"

# Downloads the Haar Cascade XML file if it does not exist
def download_cascade_if_needed():
    """
    Checks if the Haar Cascade file exists locally.
    If it does not exist, it downloads it from the official OpenCV repository.
    """
    try:
        if not os.path.exists(CASCADE_FILE_PATH):
            print("Downloading Haar Cascade model...")
            urllib.request.urlretrieve(HAAR_CASCADE_URL, CASCADE_FILE_PATH)
            print("Download complete.")
    except Exception as e:
        print("Error downloading cascade file:")
        print(e)

# Crops the face region from a frame and resizes it to 224x224
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
        download_cascade_if_needed()
        
        face_cascade = cv2.CascadeClassifier(CASCADE_FILE_PATH)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the image
        detected_faces = face_cascade.detectMultiScale(
            gray_frame, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        if len(detected_faces) == 0:
            return None
            
        # Extract the first face encountered
        first_face = detected_faces[0]
        x_coord = first_face[0]
        y_coord = first_face[1]
        width = first_face[2]
        height = first_face[3]
        
        cropped_face_img = frame[y_coord : y_coord + height, x_coord : x_coord + width]
        
        resized_face_img = cv2.resize(cropped_face_img, (224, 224))
        
        return resized_face_img
        
    except Exception as e:
        print("Error during face cropping:")
        print(e)
        return None
