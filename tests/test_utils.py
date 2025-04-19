import numpy as np
import pytest
from src.utils import preprocess_data, evaluate_predictions

def test_preprocess_data():
    # Test data
    X = np.array([[1, 2], [3, 4], [5, 6]])
    
    # Test preprocessing without existing scaler
    X_scaled, scaler = preprocess_data(X)
    assert X_scaled.shape == X.shape
    assert np.allclose(X_scaled.mean(axis=0), [0, 0], atol=1e-10)
    assert np.allclose(X_scaled.std(axis=0), [1, 1], atol=1e-10)

def test_evaluate_predictions():
    # Test data
    y_true = np.array([1, 2, 3, 4, 5])
    y_pred = np.array([1.1, 2.1, 3.1, 4.1, 5.1])
    
    # Get metrics
    metrics = evaluate_predictions(y_true, y_pred)
    
    # Check if all metrics exist
    assert all(metric in metrics for metric in ['MSE', 'RMSE', 'MAE', 'R2'])
    
    # Check if metrics are reasonable
    assert metrics['MSE'] >= 0
    assert metrics['RMSE'] >= 0
    assert metrics['MAE'] >= 0
    assert metrics['R2'] <= 1 