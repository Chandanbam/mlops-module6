import numpy as np
import pytest
from mlops_diabetes.pipeline import DataLoader, FeaturePreprocessor, ModelTrainer, MLPipeline

def test_data_loader():
    loader = DataLoader()
    X = np.array([[1, 2], [3, 4]])
    X_transformed = loader.fit_transform(X)
    assert np.array_equal(X, X_transformed)

def test_feature_preprocessor():
    preprocessor = FeaturePreprocessor()
    X = np.array([[1, 2], [3, 4], [5, 6]])
    X_transformed = preprocessor.fit_transform(X)
    
    # Check if data is standardized
    assert np.allclose(X_transformed.mean(axis=0), [0, 0], atol=1e-10)
    assert np.allclose(X_transformed.std(axis=0), [1, 1], atol=1e-10)

def test_model_trainer():
    trainer = ModelTrainer()
    X = np.array([[1, 2], [3, 4], [5, 6]])
    y = np.array([2, 4, 6])
    
    result = trainer.train(X, y)
    print("\nActual metrics returned:", result)  # Add debug print
    
    assert isinstance(result, dict)
    assert 'metrics' in result  # Check if metrics is in the result dict
    metrics = result['metrics']  # Get the metrics from the result
    assert all(metric in metrics for metric in ['MSE', 'RMSE', 'MAE', 'R2'])
    assert all(isinstance(value, float) for value in metrics.values())

def test_ml_pipeline():
    pipeline = MLPipeline()
    X = np.array([[1, 2], [3, 4], [5, 6]])
    y = np.array([2, 4, 6])
    
    # Test training
    metrics = pipeline.run(X, y, save_path='models/test_pipeline.joblib')
    assert isinstance(metrics, dict)
    
    # Test prediction
    predictions = pipeline.predict(X)
    assert len(predictions) == len(X)
    assert isinstance(predictions, np.ndarray) 