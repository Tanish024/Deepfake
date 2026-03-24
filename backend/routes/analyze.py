import os
import time
import tempfile
import uuid
import shutil
import traceback
from flask import Blueprint, request, jsonify

from model.pipeline import process_video
from model.inference import analyze_faces_in_directory

analyze_blueprint = Blueprint("analyze_blueprint", __name__)

# Allowed video MIME types/extensions — tighter server-side validation
_ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi", ".mkv"}

# 50 MB limit: keeps /tmp usage bounded and prevents single large uploads from
# blocking the server for minutes during frame extraction and inference.
_MAX_UPLOAD_BYTES = 50 * 1024 * 1024


@analyze_blueprint.route("/analyze", methods=["POST"])
def analyze_video():
    """
    Accepts a video file upload via multipart/form-data.
    Saves it to a temporary location, runs the face extraction pipeline,
    and returns a JSON response with the deepfake verdict.

    Returns:
        JSON response with the verdict and analysis details.
    """
    temporary_video_path = None
    output_faces_directory = None

    try:
        start_handle_time = time.time()

        if "video" not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video_uploaded_file = request.files["video"]

        if not video_uploaded_file.filename:
            return jsonify({"error": "No selected file"}), 400

        # Preserve the original file extension so OpenCV can identify the codec
        original_extension = os.path.splitext(video_uploaded_file.filename)[1].lower()
        if original_extension not in _ALLOWED_VIDEO_EXTENSIONS:
            return jsonify({"error": f"Unsupported file type: '{original_extension}'"}), 415

        # Check file size before writing anything to disk.
        # seek(0, 2) moves to the end of the stream; tell() returns the byte offset.
        # We then seek back to 0 so the subsequent .save() reads from the beginning.
        video_uploaded_file.stream.seek(0, 2)
        upload_size_bytes = video_uploaded_file.stream.tell()
        video_uploaded_file.stream.seek(0)

        if upload_size_bytes > _MAX_UPLOAD_BYTES:
            return jsonify({"error": "File too large. Maximum size is 50MB."}), 413

        temporary_directory = tempfile.gettempdir()
        unique_file_identifier = str(uuid.uuid4())
        temporary_video_filename = unique_file_identifier + original_extension
        temporary_video_path = os.path.join(temporary_directory, temporary_video_filename)

        video_uploaded_file.save(temporary_video_path)

        output_faces_directory = os.path.join(temporary_directory, "faces_" + unique_file_identifier)

        process_video(temporary_video_path, output_faces_directory)

        # Count only actual image files, not all directory entries
        saved_faces_count = 0
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        if os.path.exists(output_faces_directory):
            for entry in os.listdir(output_faces_directory):
                ext = os.path.splitext(entry)[1].lower()
                if ext in image_extensions:
                    saved_faces_count += 1

        if saved_faces_count == 0:
            return jsonify({"error": "No face detected in the uploaded video"}), 400

        current_dir = os.path.dirname(__file__)
        model_file_absolute = os.path.abspath(
            os.path.join(current_dir, "..", "..", "model", "deepfake_model.pth")
        )

        response_dictionary = analyze_faces_in_directory(output_faces_directory, model_file_absolute)

        # Check if inference returned an error
        if "error" in response_dictionary:
            return jsonify(response_dictionary), 500

        end_handle_time = time.time()
        response_dictionary["processing_time_ms"] = int((end_handle_time - start_handle_time) * 1000)

        return jsonify(response_dictionary), 200

    except Exception as e:
        print("Error during video analysis route handling:")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

    finally:
        # Always clean up temp files, even if an exception occurred
        if temporary_video_path and os.path.exists(temporary_video_path):
            os.remove(temporary_video_path)
        if output_faces_directory and os.path.exists(output_faces_directory):
            shutil.rmtree(output_faces_directory)

