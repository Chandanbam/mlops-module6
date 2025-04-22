import os
import json
from datetime import datetime, timedelta
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
        os.makedirs(os.path.join(self.registry_dir, "latest"), exist_ok=True)
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
        
        # Copy to latest directory
        latest_dir = os.path.join(self.registry_dir, "latest")
        latest_pipeline_path = os.path.join(latest_dir, "pipeline.joblib")
        shutil.copy2(pipeline_path, latest_pipeline_path)
        
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
    
    def cleanup_models(self, 
                      keep_last_n: Optional[int] = None,
                      older_than_days: Optional[int] = None,
                      min_r2_score: Optional[float] = None) -> List[str]:
        """
        Clean up old model versions based on specified criteria.
        
        Args:
            keep_last_n: Number of most recent models to keep
            older_than_days: Delete models older than this many days
            min_r2_score: Keep models with R2 score >= this value
            
        Returns:
            List of deleted version IDs
        """
        metadata = self._load_metadata()
        versions = metadata["versions"]
        latest_version = metadata["latest_version"]
        deleted_versions = []
        
        # Sort versions by creation time
        versions.sort(key=lambda x: x["created_at"])
        
        # Filter versions to keep
        versions_to_keep = versions.copy()
        
        # Apply age filter
        if older_than_days is not None:
            cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            versions_to_keep = [
                v for v in versions_to_keep 
                if v["created_at"] > cutoff_date or v["version_id"] == latest_version
            ]
        
        # Apply R2 score filter
        if min_r2_score is not None:
            versions_to_keep = [
                v for v in versions_to_keep 
                if v["metrics"]["R2"] >= min_r2_score or v["version_id"] == latest_version
            ]
        
        # Apply keep last N filter
        if keep_last_n is not None:
            versions_to_keep = versions_to_keep[-keep_last_n:]
            # Make sure latest version is kept
            if latest_version not in [v["version_id"] for v in versions_to_keep]:
                latest_version_info = next(v for v in versions if v["version_id"] == latest_version)
                versions_to_keep.append(latest_version_info)
        
        # Get versions to delete
        versions_to_delete = [
            v for v in versions 
            if v["version_id"] not in [keep["version_id"] for keep in versions_to_keep]
        ]
        
        # Delete files and update metadata
        for version in versions_to_delete:
            version_dir = os.path.dirname(version["pipeline_path"])
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir)
            deleted_versions.append(version["version_id"])
        
        # Update metadata
        metadata["versions"] = versions_to_keep
        self._save_metadata(metadata)
        
        return deleted_versions

    def delete_version(self, version_id: str) -> bool:
        """
        Delete a specific model version.
        
        Args:
            version_id: The version ID to delete
            
        Returns:
            True if version was deleted, False if version not found or is latest
        """
        metadata = self._load_metadata()
        
        # Don't delete the latest version
        if version_id == metadata["latest_version"]:
            return False
        
        # Find the version
        version_info = None
        for v in metadata["versions"]:
            if v["version_id"] == version_id:
                version_info = v
                break
                
        if version_info is None:
            return False
            
        # Delete the files
        version_dir = os.path.dirname(version_info["pipeline_path"])
        if os.path.exists(version_dir):
            shutil.rmtree(version_dir)
            
        # Update metadata
        metadata["versions"] = [
            v for v in metadata["versions"] 
            if v["version_id"] != version_id
        ]
        self._save_metadata(metadata)
        
        return True 