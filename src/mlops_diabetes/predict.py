import os
import joblib
import numpy as np
from sklearn.datasets import load_diabetes
from pipeline import MLPipeline

def load_model(filename='model.joblib'):
    """Load the trained model."""
    model_path = os.path.join('models', filename)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    return joblib.load(model_path)

def get_sample_data():
    """Get a sample from the diabetes dataset for prediction."""
    diabetes = load_diabetes()
    # Get first 5 samples
    return diabetes.data[:5], diabetes.feature_names

def main():
    try:
        # Load pipeline
        print("Loading pipeline...")
        pipeline = MLPipeline()
        pipeline.trainer.load_pipeline('models/pipeline.joblib')
        
        # Get sample data
        X_sample, feature_names = get_sample_data()
        
        # Make predictions
        print("\nMaking predictions for 5 samples...")
        predictions = pipeline.predict(X_sample)
        
        # Print results
        print("\nPredictions:")
        for i, pred in enumerate(predictions):
            print(f"Sample {i+1}: Predicted disease progression: {pred:.2f}")
            print("Feature values:")
            for fname, fvalue in zip(feature_names, X_sample[i]):
                print(f"  {fname}: {fvalue:.2f}")
            print()
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 