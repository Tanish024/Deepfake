import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
import timm

# Builds and returns the EfficientNet model with a 2-class classifier
def build_model():
    """
    Loads a pretrained EfficientNet-B0 model from timm.
    Replaces the final classification layer to output exactly 2 classes: Real and Fake.
    
    Returns:
        The modified PyTorch model.
    """
    try:
        model = timm.create_model('efficientnet_b0', pretrained=True)
        number_of_features = model.classifier.in_features
        model.classifier = nn.Linear(number_of_features, 2)
        return model
    except Exception as e:
        print("Error building model:")
        print(e)
        return None

# Prepares the data loaders for training and validation datasets
def get_data_loaders(data_directory, batch_size=32):
    """
    Creates torchvision datasets and PyTorch DataLoaders from a directory.
    Applies necessary image transformations like resizing and normalization.
    
    Args:
        data_directory (str): The root dataset directory path containing train/val folders.
        batch_size (int): The number of images per batch.
        
    Returns:
        DataLoader: The training data loader.
        DataLoader: The validation data loader.
    """
    try:
        image_transformer = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        train_path = data_directory + "/train"
        val_path = data_directory + "/val"
        
        train_dataset = datasets.ImageFolder(root=train_path, transform=image_transformer)
        val_dataset = datasets.ImageFolder(root=val_path, transform=image_transformer)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        return train_loader, val_loader
    except Exception as e:
        print("Error setting up data loaders:")
        print(e)
        return None, None

# Executes the PyTorch model training loop
def train_model(model, train_loader, val_loader, num_epochs=10):
    """
    Trains the model across the specified number of epochs.
    Calculates the loss, updates the weights, and prints the accuracy.
    Saves the best model to deepfake_model.pth.
    
    Args:
        model (nn.Module): The EfficientNet model.
        train_loader (DataLoader): The training data loader.
        val_loader (DataLoader): The validation data loader.
        num_epochs (int): The number of epochs to train for.
    """
    try:
        has_cuda = torch.cuda.is_available()
        device_string = "cpu"
        if has_cuda:
            device_string = "cuda"
            
        device = torch.device(device_string)
        model.to(device)
        
        loss_function = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        best_accuracy = 0.0
        
        for epoch in range(num_epochs):
            print("Epoch " + str(epoch + 1) + " of " + str(num_epochs))
            
            # Training Phase
            model.train()
            running_loss = 0.0
            
            for inputs, labels in train_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                optimizer.zero_grad()
                
                outputs = model(inputs)
                loss = loss_function(outputs, labels)
                loss.backward()
                optimizer.step()
                
                running_loss = running_loss + loss.item()
                
            average_train_loss = running_loss / len(train_loader)
            print("Average Training Loss: " + str(average_train_loss))
            
            # Validation Phase
            model.eval()
            correct_predictions = 0
            total_predictions = 0
            
            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs = inputs.to(device)
                    labels = labels.to(device)
                    
                    outputs = model(inputs)
                    
                    # Get predicted class (the index of the maximum probability logit)
                    _, predicted = torch.max(outputs.data, 1)
                    
                    batch_labels_size = labels.size(0)
                    total_predictions = total_predictions + batch_labels_size
                    
                    correct_matches = (predicted == labels).sum().item()
                    correct_predictions = correct_predictions + correct_matches
                    
            validation_accuracy = 100 * correct_predictions / total_predictions
            print("Validation Accuracy: " + str(validation_accuracy) + "%")
            
            # Save the model if it is the best so far
            if validation_accuracy > best_accuracy:
                best_accuracy = validation_accuracy
                print("New best model found! Saving...")
                torch.save(model.state_dict(), "deepfake_model.pth")
                
        print("Training completed. Best accuracy: " + str(best_accuracy) + "%")
        
    except Exception as e:
        print("Error during model training:")
        print(e)

if __name__ == "__main__":
    dataset_directory_path = "dataset"
    
    deepfake_model = build_model()
    
    if deepfake_model is not None:
        training_data_loader, validation_data_loader = get_data_loaders(dataset_directory_path)
        
        if training_data_loader is not None:
            train_model(deepfake_model, training_data_loader, validation_data_loader, num_epochs=10)
