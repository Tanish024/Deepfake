import os
import cv2
from model.preprocess import extract_frames
from model.face_detector import crop_face

# Processes an entire video, extracts frames, detects faces, and saves them
def process_video(video_path, output_folder):
    """
    Coordinates the video processing pipeline.
    It extracts frames from the video, crops the face from each frame,
    and saves the resulting face images to the specified output folder.
    
    Args:
        video_path (str): The path to the input video file.
        output_folder (str): The directory where cropped faces will be saved.
    """
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        video_name = os.path.basename(video_path)
        print("Processing Video: " + video_name)
        
        frames_list = extract_frames(video_path, num_frames=15)
        num_frames_extracted = len(frames_list)
        print("Frames extracted: " + str(num_frames_extracted))
        
        faces_saved_count = 0
        
        for index in range(num_frames_extracted):
            current_frame = frames_list[index]
            cropped_face_result = crop_face(current_frame)
            
            if cropped_face_result is not None:
                # Format to frame_000.jpg, frame_001.jpg, etc.
                file_number_string = str(faces_saved_count).zfill(3)
                file_name = "frame_" + file_number_string + ".jpg"
                save_path = os.path.join(output_folder, file_name)
                
                cv2.imwrite(save_path, cropped_face_result)
                faces_saved_count = faces_saved_count + 1
                
        print("Faces saved: " + str(faces_saved_count))
        
    except Exception as e:
        print("Error processing video pipeline:")
        print(e)
