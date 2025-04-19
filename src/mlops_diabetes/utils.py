import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

def preprocess_data(X, scaler=None):
    """
    Preprocess the data using StandardScaler.
    If scaler is not provided, creates a new one.
    """
    if scaler is None:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = scaler.transform(X)
    return X_scaled, scaler

def plot_feature_importance(model, feature_names, output_path=None):
    """
    Plot feature importance for linear models.
    """
    importance = np.abs(model.coef_)
    plt.figure(figsize=(10, 6))
    plt.bar(feature_names, importance)
    plt.xticks(rotation=45, ha='right')
    plt.title('Feature Importance in Diabetes Prediction')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()
    plt.close()

def evaluate_predictions(y_true, y_pred):
    """
    Calculate various regression metrics.
    """
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