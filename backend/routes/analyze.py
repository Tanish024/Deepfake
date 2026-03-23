import os
import time
import tempfile
import uuid
import shutil
from flask import Blueprint, request, jsonify

# Import the process_video function from the model package
from model.pipeline import process_video
from model.inference import analyze_faces_in_directory

analyze_blueprint = Blueprint("analyze_blueprint", __name__)

# Handles the /analyze POST request for video deepfake detection
@analyze_blueprint.route("/analyze", methods=["POST"])
def analyze_video():
    """
    Accepts a video file upload via multipart/form-data.
    Saves it to a temporary location (/tmp/ equivalent), 
    runs the face extraction pipeline, and returns a JSON response.
    
    Returns:
        JSON response with the verdict and analysis details.
    """
    try:
        start_handle_time = time.time()
        
        if "video" not in request.files:
            return jsonify({"error": "No video file provided"}), 400
            
        video_uploaded_file = request.files["video"]
        
        if video_uploaded_file.filename == "":
            return jsonify({"error": "No selected file"}), 400
            
        # Save uploaded file temporarily (acting as /tmp/ directory)
        temporary_directory = tempfile.gettempdir()
        unique_file_identifier = str(uuid.uuid4())
        temporary_video_filename = unique_file_identifier + ".mp4"
        temporary_video_path = os.path.join(temporary_directory, temporary_video_filename)
        
        video_uploaded_file.save(temporary_video_path)
        
        output_faces_directory = os.path.join(temporary_directory, "faces_" + unique_file_identifier)
        
        # Run the extraction and cropping pipeline
        process_video(temporary_video_path, output_faces_directory)
        
        saved_faces_count = 0
        if os.path.exists(output_faces_directory):
            directory_contents_list = os.listdir(output_faces_directory)
            saved_faces_count = len(directory_contents_list)
            
        if saved_faces_count == 0:
            # Clean up before returning error
            if os.path.exists(temporary_video_path):
                os.remove(temporary_video_path)
            if os.path.exists(output_faces_directory):
                shutil.rmtree(output_faces_directory)
            return jsonify({"error": "No face detected"}), 400
            
        # Run the PyTorch AI inference on the extracted faces
        # Using abspath dynamically resolves the correct location of deepfake_model.pth
        current_dir = os.path.dirname(__file__)
        model_file_absolute = os.path.abspath(os.path.join(current_dir, "..", "..", "model", "deepfake_model.pth"))
        
        response_dictionary = analyze_faces_in_directory(output_faces_directory, model_file_absolute)
        
        # Clean up temporary video file and extracted faces directory
        if os.path.exists(temporary_video_path):
            os.remove(temporary_video_path)
            
        if os.path.exists(output_faces_directory):
            shutil.rmtree(output_faces_directory)
            
        # Check if inference returned an error
        if "error" in response_dictionary:
            return jsonify(response_dictionary), 500
            
        end_handle_time = time.time()
        calculate_time_taken = end_handle_time - start_handle_time
        time_taken_milliseconds = int(calculate_time_taken * 1000)
        
        # Add the processing time to the final results
        response_dictionary["processing_time_ms"] = time_taken_milliseconds
        
        return jsonify(response_dictionary), 200
        
    except Exception as e:
        print("Error during video analysis route handling:")
        print(e)
        return jsonify({"error": "Internal server error"}), 500
