from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
import numpy as np
from typing import List, Dict, Optional
from sklearn.datasets import load_diabetes
from mlops_diabetes.pipeline import MLPipeline
import time
from mlops_diabetes.monitoring import (
    setup_monitoring,
    record_prediction_metrics,
    record_training_metrics,
    update_system_metrics
)
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
import psutil

app = FastAPI(
    title="Diabetes Prediction API",
    description="API for training models and making predictions on diabetes progression",
    version="1.0.0"
)

# Set up monitoring
setup_monitoring(app)

# Initialize global pipeline
pipeline = MLPipeline()

class PredictionInput(BaseModel):
    features: List[List[float]]

class PredictionResponse(BaseModel):
    predictions: List[float]
    version: str
    latency: float

class TrainingResponse(BaseModel):
    metrics: Dict[str, float]
    version: str
    message: str

class VersionInfo(BaseModel):
    version_id: str
    created_at: str
    metrics: Dict[str, float]
    description: str

def update_metrics_background(background_tasks: BackgroundTasks):
    """Add system metrics update to background tasks."""
    background_tasks.add_task(update_system_metrics)

@app.post("/train", response_model=TrainingResponse)
async def train_model(description: str = "", background_tasks: BackgroundTasks = None):
    """
    Train a new model using the diabetes dataset.
    Returns the training metrics and version information.
    """
    try:
        # Load data
        diabetes = load_diabetes()
        X, y = diabetes.data, diabetes.target
        
        # Train model
        result = pipeline.run(X, y, description=description)
        
        # Record metrics
        record_training_metrics(result["version"], result["metrics"])
        
        # Update system metrics in background
        if background_tasks:
            update_metrics_background(background_tasks)
        
        return TrainingResponse(
            metrics=result["metrics"],
            version=result["version"],
            message="Model trained successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=PredictionResponse)
async def predict(
    input_data: PredictionInput,
    version: Optional[str] = Query(None, description="Model version to use for prediction"),
    background_tasks: BackgroundTasks = None
):
    """
    Make predictions using the trained model.
    Optionally specify a model version to use.
    """
    try:
        # Convert input data to numpy array
        features = np.array(input_data.features)
        
        # Validate input shape
        if features.shape[1] != 10:  # Diabetes dataset has 10 features
            raise ValueError("Input must have 10 features per sample")
        
        # Record prediction start time
        start_time = time.time()
        
        # Make predictions
        predictions = pipeline.predict(features, version=version)
        
        # Calculate latency
        latency = time.time() - start_time
        
        # Get the version that was actually used (latest if none specified)
        used_version = version or pipeline.trainer.registry.get_latest_version()
        
        # Record metrics
        record_prediction_metrics(used_version, latency)
        
        # Update system metrics in background
        if background_tasks:
            update_metrics_background(background_tasks)
        
        return PredictionResponse(
            predictions=predictions.tolist(),
            version=used_version,
            latency=latency
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models", response_model=List[VersionInfo])
async def list_models(background_tasks: BackgroundTasks = None):
    """
    List all available model versions.
    """
    try:
        if background_tasks:
            update_metrics_background(background_tasks)
        return pipeline.list_versions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{version}", response_model=VersionInfo)
async def get_model_info(version: str, background_tasks: BackgroundTasks = None):
    """
    Get information about a specific model version.
    """
    try:
        if background_tasks:
            update_metrics_background(background_tasks)
        return pipeline.get_version_info(version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/features")
async def get_feature_names(background_tasks: BackgroundTasks = None):
    """
    Get the names of the features used in the model.
    """
    try:
        if background_tasks:
            update_metrics_background(background_tasks)
        diabetes = load_diabetes()
        return {"features": diabetes.feature_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check(background_tasks: BackgroundTasks = None):
    """
    Check if the API is running.
    """
    if background_tasks:
        update_metrics_background(background_tasks)
    return {"status": "healthy"} 