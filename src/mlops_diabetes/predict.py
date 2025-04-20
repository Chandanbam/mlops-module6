import os
import joblib
import numpy as np
from sklearn.datasets import load_diabetes
from mlops_diabetes.pipeline import MLPipeline

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
        
        # Try to load the latest model version
        try:
            pipeline.trainer.load_pipeline()  # No version specified will load latest
            print("Using latest model version")
        except ValueError as e:
            print("No trained model found. Please train a model first using:")
            print("python -m mlops_diabetes.train")
            return
        
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
        print("\nPlease ensure you have trained a model first using:")
        print("python -m mlops_diabetes.train")

if __name__ == "__main__":
    main() 