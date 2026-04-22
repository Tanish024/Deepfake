import os
import json
import traceback
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import timm

# Load the class-to-index mapping that was used when the model was trained.
# This file exists because torchvision's ImageFolder assigns indices alphabetically
# by training-folder name, so the mapping is entirely dataset-dependent.
# Storing it as a sidecar JSON means inference will never silently use the wrong
# index even if someone renames the training folders later.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_CLASS_TO_IDX_PATH = os.path.join(_THIS_DIR, "class_to_idx.json")

with open(_CLASS_TO_IDX_PATH, "r") as _f:
    _CLASS_TO_IDX: dict = json.load(_f)

_IDX_FAKE: int = _CLASS_TO_IDX["FAKE"]
_IDX_REAL: int = _CLASS_TO_IDX["REAL"]

# Supported image extensions for face images
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Cache keyed by absolute model path so different .pth files are handled correctly
_model_cache: dict = {}


def load_deepfake_model(model_path):
    """
    Initializes the EfficientNet-B0 model with a 2-class classifier,
    and loads the trained weights from the specified .pth file.
    The result is cached per model_path so repeated calls are free.

    Args:
        model_path (str): The path to the trained deepfake_model.pth file.

    Returns:
        The loaded and ready PyTorch model, or None if it fails.
    """
    try:
        canonical_path = os.path.abspath(model_path)

        if canonical_path in _model_cache:
            return _model_cache[canonical_path]

        if not os.path.exists(canonical_path):
            print(f"Model file not found: {canonical_path}")
            return None

        print("Loading deepfake AI model into memory...")
        model = timm.create_model('efficientnet_b0', pretrained=False)
        number_of_features = model.classifier.in_features
        model.classifier = nn.Linear(number_of_features, 2)

        has_cuda = torch.cuda.is_available()
        device_string = "cuda" if has_cuda else "cpu"
        device = torch.device(device_string)

        loaded_state = torch.load(canonical_path, map_location=device, weights_only=True)
        model.load_state_dict(loaded_state)

        model.to(device)
        model.eval()

        _model_cache[canonical_path] = model
        print(f"Model loaded successfully on {device_string.upper()}!")
        return model

    except Exception as e:
        print("Error loading deepfake model:")
        traceback.print_exc()
        return None

# Analyzes a folder of cropped face images to determine if the video is real or fake
def analyze_faces_in_directory(faces_directory_path, model_path="../model/deepfake_model.pth"):
    """
    Reads all image files inside a directory, runs them through the deepfake model,
    and calculates the final verdict, confidence score, and suspicious frames.

    Args:
        faces_directory_path (str): The folder containing the face crops.
        model_path (str): The absolute or relative path to the trained .pth file.

    Returns:
        dict: A dictionary containing the analysis results.
    """
    try:
        model = load_deepfake_model(model_path)

        if model is None:
            return {"error": "Failed to load AI model"}

        # Derive the device from the model's own parameters — avoids mismatches
        device = next(model.parameters()).device

        image_transformer = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Grab all image files, skipping non-image entries (avoids PIL crash)
        all_entries = []
        if os.path.exists(faces_directory_path):
            all_entries = os.listdir(faces_directory_path)

        faces_files = [
            f for f in all_entries
            if os.path.splitext(f)[1].lower() in _IMAGE_EXTENSIONS
        ]
        faces_files.sort()

        total_frames = len(faces_files)
        if total_frames == 0:
            return {"error": "No face images found in the directory"}

        fake_votes = 0
        total_confidence_sum = 0.0
        suspicious_frames_indices = []

        with torch.no_grad():
            for index, file_name in enumerate(faces_files):
                file_path = os.path.join(faces_directory_path, file_name)

                image = Image.open(file_path).convert("RGB")
                input_tensor = image_transformer(image).unsqueeze(0).to(device)

                outputs = model(input_tensor)
                # softmax over class dimension; indices come from class_to_idx.json
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                probability_fake = probabilities[_IDX_FAKE].item()
                probability_real = probabilities[_IDX_REAL].item()

                # Require 65% fake confidence per frame to avoid false positives
                # (training data was 83% FAKE so model is biased toward FAKE)
                if probability_fake > 0.65:
                    fake_votes += 1
                    suspicious_frames_indices.append(index)
                    total_confidence_sum += probability_fake
                else:
                    total_confidence_sum += probability_real

        fake_ratio = fake_votes / total_frames
        # Flag as FAKE if 30%+ of frames are suspicious
        # Real videos typically score ~20%, fakes score ~33%+ so 30% is the sweet spot
        verdict = "FAKE" if fake_ratio >= 0.30 else "REAL"

        average_confidence_percentage = round((total_confidence_sum / total_frames) * 100, 1)

        return {
            "verdict": verdict,
            "confidence": average_confidence_percentage,
            "frames_analyzed": total_frames,
            "suspicious_frames": suspicious_frames_indices,
        }

    except Exception as e:
        print("Error analyzing faces:")
        traceback.print_exc()
        return {"error": "Inference analysis failed"}

if __name__ == "__main__":
    # Example usage for testing
    example_path = "output_faces/"
    print(analyze_faces_in_directory(example_path, "deepfake_model.pth"))
