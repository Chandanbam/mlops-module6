import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import shutil

class ModelRegistry:
    """Manages model versions and their metadata."""
    
    def __init__(self, registry_dir: str = "models"):
        self.registry_dir = registry_dir
        self.metadata_file = os.path.join(registry_dir, "model_registry.json")
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Initialize the registry directory and metadata file."""
        os.makedirs(self.registry_dir, exist_ok=True)
        if not os.path.exists(self.metadata_file):
            self._save_metadata({
                "versions": [],
                "latest_version": None
            })
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load the registry metadata."""
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save the registry metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def register_model(self, 
                      pipeline_path: str,
                      metrics: Dict[str, float],
                      description: str = "") -> str:
        """
        Register a new model version.
        Returns the version ID.
        """
        metadata = self._load_metadata()
        
        # Generate new version ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"v_{timestamp}"
        
        # Create version directory
        version_dir = os.path.join(self.registry_dir, version)
        os.makedirs(version_dir, exist_ok=True)
        
        # Copy model file to version directory
        new_pipeline_path = os.path.join(version_dir, "pipeline.joblib")
        shutil.copy2(pipeline_path, new_pipeline_path)
        
        # Update metadata
        version_info = {
            "version_id": version,
            "created_at": datetime.now().isoformat(),
            "metrics": metrics,
            "description": description,
            "pipeline_path": new_pipeline_path
        }
        
        metadata["versions"].append(version_info)
        metadata["latest_version"] = version
        
        self._save_metadata(metadata)
        return version
    
    def get_model_path(self, version: Optional[str] = None) -> str:
        """
        Get the path to a model version.
        If version is None, returns the latest version.
        """
        metadata = self._load_metadata()
        
        if version is None:
            version = metadata["latest_version"]
            if version is None:
                raise ValueError("No models have been registered yet")
        
        for v in metadata["versions"]:
            if v["version_id"] == version:
                return v["pipeline_path"]
        
        raise ValueError(f"Version {version} not found")
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all registered model versions."""
        metadata = self._load_metadata()
        return metadata["versions"]
    
    def get_latest_version(self) -> str:
        """Get the latest version ID."""
        metadata = self._load_metadata()
        if metadata["latest_version"] is None:
            raise ValueError("No models have been registered yet")
        return metadata["latest_version"]
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get information about a specific version."""
        metadata = self._load_metadata()
        for v in metadata["versions"]:
            if v["version_id"] == version:
                return v
        raise ValueError(f"Version {version} not found") 