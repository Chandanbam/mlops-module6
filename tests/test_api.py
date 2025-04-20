import pytest
from fastapi.testclient import TestClient
from mlops_diabetes.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_features():
    response = client.get("/features")
    assert response.status_code == 200
    features = response.json()["features"]
    assert isinstance(features, list)
    assert len(features) == 10  # Diabetes dataset has 10 features

def test_train_model():
    response = client.post("/train", params={"description": "Test model"})
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "version" in data
    assert "message" in data
    assert data["message"] == "Model trained successfully"
    
    # Check metrics
    metrics = data["metrics"]
    assert all(metric in metrics for metric in ["MSE", "RMSE", "MAE", "R2"])
    
    # Store version for later tests
    return data["version"]

def test_predict():
    # First train the model and get version
    version = test_train_model()
    
    # Create sample input data (10 features)
    input_data = {
        "features": [
            [0.0] * 10,  # All zeros
            [1.0] * 10   # All ones
        ]
    }
    
    # Test prediction with specific version
    response = client.post(f"/predict?version={version}", json=input_data)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "version" in data
    assert data["version"] == version
    predictions = data["predictions"]
    assert isinstance(predictions, list)
    assert len(predictions) == 2  # Should match input samples
    
    # Test prediction with latest version
    response = client.post("/predict", json=input_data)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "version" in data

def test_predict_invalid_input():
    input_data = {
        "features": [
            [0.0] * 5  # Invalid: only 5 features (should be 10)
        ]
    }
    
    response = client.post("/predict", json=input_data)
    assert response.status_code == 400  # Bad request

def test_list_models():
    # Train a model first
    version = test_train_model()
    
    response = client.get("/models")
    assert response.status_code == 200
    models = response.json()
    assert isinstance(models, list)
    assert len(models) > 0
    
    # Check model info structure
    model = models[0]
    assert "version_id" in model
    assert "created_at" in model
    assert "metrics" in model
    assert "description" in model

def test_get_model_info():
    # Train a model first
    version = test_train_model()
    
    # Get info for valid version
    response = client.get(f"/models/{version}")
    assert response.status_code == 200
    model = response.json()
    assert model["version_id"] == version
    
    # Test invalid version
    response = client.get("/models/invalid_version")
    assert response.status_code == 404 