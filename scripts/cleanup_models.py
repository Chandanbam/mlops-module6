from mlops_diabetes.model_versioning import ModelRegistry

def main():
    registry = ModelRegistry()
    
    print("Cleaning up models, keeping only the 5 most recent versions...")
    deleted_versions = registry.cleanup_models(keep_last_n=5)
    
    if deleted_versions:
        print("\nDeleted the following model versions:")
        for version in deleted_versions:
            print(f"- {version}")
    else:
        print("\nNo models were deleted (5 or fewer models exist)")
    
    print("\nRemaining models:")
    for version in registry.list_versions():
        print(f"- {version['version_id']} (created at {version['created_at']})")

if __name__ == "__main__":
    main() 