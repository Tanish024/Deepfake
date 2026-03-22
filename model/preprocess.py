import cv2

# Extracts 15 evenly spaced frames from any mp4 video
def extract_frames(video_path, num_frames=15):
    """
    Extracts evenly spaced frames from a given video file.
    
    Args:
        video_path (str): The path to the video file.
        num_frames (int): The number of frames to extract.
        
    Returns:
        list: A list of extracted frames (numpy arrays).
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print("Could not open video.")
            return []
            
        total_frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames_count == 0:
            return []
            
        # Calculate the step size to get evenly spaced frames
        frames_step = int(total_frames_count / num_frames)
        
        if frames_step == 0:
            frames_step = 1
            
        extracted_frames_list = []
        
        for index in range(num_frames):
            frame_position = index * frames_step
            if frame_position >= total_frames_count:
                frame_position = total_frames_count - 1
                
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
            success, current_frame = cap.read()
            
            if success:
                extracted_frames_list.append(current_frame)
                
        cap.release()
        return extracted_frames_list
        
    except Exception as e:
        print("Error during frame extraction:")
        print(e)
        return []
