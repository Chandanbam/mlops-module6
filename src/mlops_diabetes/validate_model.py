import argparse
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from pipeline import MLPipeline
import numpy as np

def validate_model(threshold_r2=0.4, threshold_mse=3000):
    """
    Validate model performance against threshold metrics.
    Returns True if model meets all criteria, False otherwise.
    """
    # Load data
    diabetes = load_diabetes()
    X, y = diabetes.data, diabetes.target
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Initialize and train pipeline
    pipeline = MLPipeline()
    result = pipeline.run(X_train, y_train)
    
    # Make predictions
    y_pred = pipeline.predict(X_test)
    
    # Calculate metrics
    mse = np.mean((y_test - y_pred) ** 2)
    r2 = result['metrics']['R2']
    
    print(f"Model Validation Results:")
    print(f"R² Score: {r2:.3f} (threshold: {threshold_r2})")
    print(f"MSE: {mse:.2f} (threshold: {threshold_mse})")
    
    # Check if model meets criteria
    meets_criteria = (r2 >= threshold_r2 and mse <= threshold_mse)
    
    if meets_criteria:
        print("✅ Model meets all validation criteria")
    else:
        print("❌ Model fails to meet validation criteria")
        if r2 < threshold_r2:
            print(f"- R² score {r2:.3f} below threshold {threshold_r2}")
        if mse > threshold_mse:
            print(f"- MSE {mse:.2f} above threshold {threshold_mse}")
    
    return meets_criteria

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate model performance")
    parser.add_argument("--threshold-r2", type=float, default=0.4,
                      help="Minimum R² score threshold")
    parser.add_argument("--threshold-mse", type=float, default=3000,
                      help="Maximum MSE threshold")
    
    args = parser.parse_args()
    
    # Exit with status code 1 if validation fails
    if not validate_model(args.threshold_r2, args.threshold_mse):
        exit(1) 