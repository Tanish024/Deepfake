import os
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import timm

# Global variable to avoid reloading the model on every single video upload
global_loaded_model = None

# Loads the PyTorch model into memory if it is not already loaded
def load_deepfake_model(model_path):
    """
    Initializes the EfficientNet-B0 model with a 2-class classifier,
    and loads the trained weights from the specified .pth file.
    
    Args:
        model_path (str): The path to the trained deepfake_model.pth file.
        
    Returns:
        The loaded and ready PyTorch model, or None if it fails.
    """
    try:
        global global_loaded_model
        
        if global_loaded_model is not None:
            return global_loaded_model
            
        print("Loading deepfake AI model into memory...")
        model = timm.create_model('efficientnet_b0', pretrained=False)
        number_of_features = model.classifier.in_features
        model.classifier = nn.Linear(number_of_features, 2)
        
        # Check for CUDA availability without using ternary operators
        has_cuda = torch.cuda.is_available()
        device_string = "cpu"
        if has_cuda:
            device_string = "cuda"
            
        device = torch.device(device_string)
        
        # Load weights and set to evaluation mode
        loaded_state = torch.load(model_path, map_location=device, weights_only=True)
        model.load_state_dict(loaded_state)
        
        model.to(device)
        model.eval()
        
        global_loaded_model = model
        print("Model loaded successfully!")
        return global_loaded_model
        
    except Exception as e:
        print("Error loading deepfake model:")
        print(e)
        return None

# Analyzes a folder of cropped face images to determine if the video is real or fake
def analyze_faces_in_directory(faces_directory_path, model_path="../model/deepfake_model.pth"):
    """
    Reads all .jpg files inside a directory, runs them through the deepfake model,
    and calculates the final verdict, confidence score, and suspicious frames.
    
    Args:
        faces_directory_path (str): The folder containing the face crops.
        model_path (str): The absolute or relative path to the trained .pth file.
        
    Returns:
        dict: A dictionary containing the analysis results.
    """
    try:
        # Load the AI brain
        model = load_deepfake_model(model_path)
        
        if model is None:
            return {"error": "Failed to load AI model"}
            
        # Determine device without ternary operators
        has_cuda = torch.cuda.is_available()
        device_string = "cpu"
        if has_cuda:
            device_string = "cuda"
            
        device = torch.device(device_string)
        
        # The exact mathematical transformations used during training
        image_transformer = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Grab all face files
        faces_files = []
        if os.path.exists(faces_directory_path):
            faces_files = os.listdir(faces_directory_path)
            
        # Ensure they are sorted so frame 0 is first, frame 1 is second...
        faces_files.sort()
        
        total_frames = len(faces_files)
        if total_frames == 0:
            return {"error": "No face images found in the directory"}
            
        fake_votes = 0
        total_confidence_sum = 0.0
        suspicious_frames_indices = []
        
        # Run inference without tracking gradients to save memory
        with torch.no_grad():
            for index in range(total_frames):
                file_name = faces_files[index]
                file_path = os.path.join(faces_directory_path, file_name)
                
                # Open image, transform it, add batch dimension, and move to GPU/CPU
                image = Image.open(file_path).convert("RGB")
                input_tensor = image_transformer(image)
                input_tensor = input_tensor.unsqueeze(0)
                input_tensor = input_tensor.to(device)
                
                # Get raw model outputs
                outputs = model(input_tensor)
                
                # Convert raw outputs into perfectly balanced percentages (0 to 1)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                
                # Kaggle datasets using ImageFolder usually sort alphabetically
                # So Index 0 = FAKE, Index 1 = REAL
                probability_fake = probabilities[0].item()
                probability_real = probabilities[1].item()
                
                # If it's more than 50% sure it's fake, we count it as a suspicious frame
                if probability_fake > 0.5:
                    fake_votes = fake_votes + 1
                    suspicious_frames_indices.append(index)
                    total_confidence_sum = total_confidence_sum + probability_fake
                else:
                    total_confidence_sum = total_confidence_sum + probability_real
                    
        # Final calculations
        verdict = "REAL"
        
        # If more than 30% of the visible faces are fake, we flag the entire video as a deepfake
        fake_ratio = fake_votes / total_frames
        if fake_ratio >= 0.3:
            verdict = "FAKE"
            
        # Convert the average raw confidence into a readable percentage
        average_confidence_decimal = total_confidence_sum / total_frames
        average_confidence_percentage = round(average_confidence_decimal * 100, 1)
        
        # Build the final response dictionary
        final_results = {
            "verdict": verdict,
            "confidence": average_confidence_percentage,
            "frames_analyzed": total_frames,
            "suspicious_frames": suspicious_frames_indices
        }
        
        return final_results
        
    except Exception as e:
        print("Error analyzing faces:")
        print(e)
        return {"error": "Inference analysis failed"}

if __name__ == "__main__":
    # Example usage for testing
    example_path = "output_faces/"
    print(analyze_faces_in_directory(example_path, "deepfake_model.pth"))
