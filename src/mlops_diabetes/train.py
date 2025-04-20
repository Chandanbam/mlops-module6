import os
import joblib
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from mlops_diabetes.pipeline import MLPipeline

def load_data():
    """Load the diabetes dataset."""
    diabetes = load_diabetes()
    X = diabetes.data
    y = diabetes.target
    feature_names = diabetes.feature_names
    return X, y, feature_names

def save_model(model, filename='model.joblib'):
    """Save the trained model."""
    if not os.path.exists('models'):
        os.makedirs('models')
    model_path = os.path.join('models', filename)
    joblib.dump(model, model_path)
    return model_path

def main():
    # Load data
    print("Loading diabetes dataset...")
    X, y, feature_names = load_data()
    print(f"Dataset loaded. Features: {feature_names}")
    
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Create and run pipeline
    pipeline = MLPipeline()
    result = pipeline.run(X_train, y_train)
    
    # Evaluate on test set
    y_pred = pipeline.predict(X_test)
    test_metrics = pipeline.trainer._calculate_metrics(y_test, y_pred)
    
    # Print metrics
    print("\nTraining Metrics:")
    for metric, value in result['metrics'].items():
        print(f"{metric}: {value:.4f}")
    
    print("\nTest Metrics:")
    for metric, value in test_metrics.items():
        print(f"{metric}: {value:.4f}")

    print(f"\nModel version: {result['version']}")

if __name__ == "__main__":
    main() 