import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# Load pre-trained model (will download on first run)
print("Loading AI model...")
model = MobileNetV2(weights='imagenet')
print("Model loaded successfully!")

def classify_image(img_path):
    """
    Classify an image using MobileNetV2
    
    Args:
        img_path: Path to the image file
        
    Returns:
        List of (class_name, probability) tuples
    """
    try:
        # Load and preprocess image
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        
        # Decode predictions
        decoded = decode_predictions(predictions, top=5)[0]
        
        # Format results
        results = []
        for pred in decoded:
            results.append({
                'label': pred[1],
                'confidence': float(pred[2])
            })
        
        return results
    
    except Exception as e:
        print(f"Error classifying image: {e}")
        return []

def map_to_civic_issue(predictions):
    """
    Map ImageNet predictions to civic issue categories
    
    Args:
        predictions: List of predictions from classify_image
        
    Returns:
        (issue_type, confidence) tuple
    """
    
    # Mapping keywords to civic issues
    ISSUE_MAPPING = {
        'pothole': ['street', 'pavement', 'asphalt', 'road', 'manhole'],
        'garbage': ['trash', 'plastic', 'bottle', 'waste', 'bin', 'bag', 'container'],
        'drainage': ['water', 'puddle', 'sewer', 'grate', 'drain'],
        'streetlight': ['lamp', 'light', 'bulb', 'pole', 'street_light'],
        'vegetation': ['tree', 'plant', 'branch', 'leaf'],
        'animal': ['dog', 'cat', 'cow', 'animal'],
        'damage': ['crack', 'broken', 'damaged', 'wall', 'fence']
    }
    
    # Check each prediction against mapping
    for pred in predictions:
        label = pred['label'].lower()
        
        for issue_type, keywords in ISSUE_MAPPING.items():
            if any(keyword in label for keyword in keywords):
                return issue_type, pred['confidence']
    
    # If no match found, return the top prediction
    if predictions:
        return 'other', predictions[0]['confidence']
    
    return 'unknown', 0.0

# Test the model when file is run directly
if __name__ == '__main__':
    print("AI Model Test")
    print("-" * 50)
    
    # This will download the model if not already present
    test_predictions = classify_image('test.jpg') if os.path.exists('test.jpg') else []
    
    if test_predictions:
        print("Predictions:")
        for pred in test_predictions:
            print(f"  - {pred['label']}: {pred['confidence']*100:.2f}%")
    else:
        print("No test image found. Model ready to use.")