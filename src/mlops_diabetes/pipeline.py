from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import joblib
import os
from typing import Tuple, Dict, Any, Optional, List
from .model_versioning import ModelRegistry

class DataLoader(BaseEstimator, TransformerMixin):
    """Load and prepare the diabetes dataset."""
    
    def __init__(self):
        self.feature_names = None
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return X

class FeaturePreprocessor(BaseEstimator, TransformerMixin):
    """Preprocess features using StandardScaler."""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def fit(self, X, y=None):
        self.scaler.fit(X)
        return self
    
    def transform(self, X):
        return self.scaler.transform(X)

class ModelTrainer:
    """Handle model training and evaluation."""
    
    def __init__(self, model=None):
        self.model = model if model is not None else RandomForestRegressor()
        self.pipeline = None
        self.registry = ModelRegistry()
        
    def create_pipeline(self) -> Pipeline:
        """Create the ML pipeline."""
        return Pipeline([
            ('data_loader', DataLoader()),
            ('preprocessor', FeaturePreprocessor()),
            ('model', self.model)
        ])
    
    def train(self, X: np.ndarray, y: np.ndarray, description: str = "") -> Dict[str, Any]:
        """Train the model and return metrics."""
        self.pipeline = self.create_pipeline()
        self.pipeline.fit(X, y)
        
        # Get predictions
        y_pred = self.pipeline.predict(X)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y, y_pred)
        
        # Save pipeline and register version
        temp_path = os.path.join("models", "temp_pipeline.joblib")
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.pipeline, temp_path)
        
        version = self.registry.register_model(
            pipeline_path=temp_path,
            metrics=metrics,
            description=description
        )
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {
            "metrics": metrics,
            "version": version
        }
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate model performance metrics."""
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_true - y_pred))
        r2 = 1 - (np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2))
        
        return {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
    
    def load_pipeline(self, version: Optional[str] = None) -> None:
        """Load a specific version of the pipeline."""
        pipeline_path = self.registry.get_model_path(version)
        self.pipeline = joblib.load(pipeline_path)

class MLPipeline:
    """Main pipeline class to orchestrate the ML workflow."""
    
    def __init__(self, model=None):
        self.trainer = ModelTrainer(model)
        
    def run(self, X: np.ndarray, y: np.ndarray, 
            description: str = "",
            save_path: str = 'models/pipeline.joblib') -> Dict[str, Any]:
        """Run the complete ML pipeline."""
        
        print("Starting ML pipeline...")
        print(f"Data shape: {X.shape}")
        
        # Train model and get metrics
        print("\nTraining model...")
        result = self.trainer.train(X, y, description)
        
        print("\nPipeline completed successfully!")
        print(f"Model version: {result['version']}")
        return result
    
    def predict(self, X: np.ndarray, version: Optional[str] = None) -> np.ndarray:
        """Make predictions using a specific model version."""
        self.trainer.load_pipeline(version)
        return self.trainer.pipeline.predict(X)
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all model versions."""
        return self.trainer.registry.list_versions()
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get information about a specific version."""
        return self.trainer.registry.get_version_info(version) 