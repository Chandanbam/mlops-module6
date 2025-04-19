# MLOps Module 6 - Diabetes Prediction

This project demonstrates MLOps practices using the diabetes dataset from scikit-learn. The project includes data preprocessing, model training, evaluation components, model versioning, monitoring, and a REST API.

## Project Structure

```
mlops-module6/
├── data/              # Data directory
├── models/            # Saved models and versioning
│   └── model_registry.json  # Model version metadata
├── src/               # Source code
│   ├── train.py      # Training script
│   ├── predict.py    # Prediction script
│   ├── utils.py      # Utility functions
│   ├── pipeline.py   # ML pipeline components
│   ├── model_versioning.py  # Model versioning system
│   ├── monitoring.py # Monitoring and metrics
│   ├── api.py        # FastAPI application
│   └── run_server.py # Server startup script
├── tests/            # Test files
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile        # Dockerfile for the API
├── prometheus.yml    # Prometheus configuration
├── requirements.txt  # Project dependencies
└── README.md        # Project documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

1. Train the model:
```bash
python src/train.py
```

2. Make predictions:
```bash
python src/predict.py
```

### Running with Docker Compose

Start the entire stack (API, Prometheus, and Grafana):
```bash
docker-compose up -d
```

This will start:
- API server on http://localhost:8000
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3000

### Monitoring

The project includes comprehensive monitoring using Prometheus and Grafana:

#### Metrics Available

1. **API Metrics**
   - Request counts
   - Response times
   - Error rates
   - Request sizes
   - Response sizes

2. **Model Metrics**
   - Training runs
   - Prediction counts by version
   - Model performance metrics (MSE, RMSE, MAE, R²)
   - Prediction latency

3. **System Metrics**
   - CPU usage
   - Memory usage
   - Available disk space

#### Accessing Metrics

1. **Raw Metrics**
   - Available at `http://localhost:8000/metrics`
   - Prometheus format

2. **Prometheus**
   - Access at `http://localhost:9090`
   - Query metrics using PromQL
   - View targets and alerts

3. **Grafana**
   - Access at `http://localhost:3000`
   - Default credentials: admin/admin
   - Pre-configured dashboards available

#### Setting up Grafana

1. Log in to Grafana at http://localhost:3000
2. Add Prometheus as a data source:
   - URL: http://prometheus:9090
   - Access: Server (default)
3. Import the provided dashboards

### REST API

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

#### API Endpoints

1. **Health Check**
   - GET `/health`
   - Returns API health status

2. **Get Features**
   - GET `/features`
   - Returns the list of feature names used in the model

3. **Train Model**
   - POST `/train`
   - Query Parameters:
     - `description`: Optional description of the model version
   - Returns training metrics and version information

4. **Make Predictions**
   - POST `/predict`
   - Query Parameters:
     - `version`: Optional model version to use (uses latest if not specified)
   - Request body:
     ```json
     {
       "features": [[feature1, feature2, ..., feature10], ...]
     }
     ```
   - Returns predictions, version used, and latency

5. **List Models**
   - GET `/models`
   - Returns a list of all available model versions with their metadata

6. **Get Model Info**
   - GET `/models/{version}`
   - Returns detailed information about a specific model version

## Model Versioning

The project includes a model versioning system that:
- Automatically versions each trained model
- Stores model artifacts and metadata
- Tracks performance metrics
- Allows loading specific versions for prediction
- Maintains a registry of all models

### Version Information

Each model version includes:
- Version ID (timestamp-based)
- Creation timestamp
- Performance metrics
- Description
- Model artifact path

## Testing

Run the test suite:
```bash
pytest tests/
```

## Dataset

The project uses the diabetes dataset from scikit-learn, which contains 10 baseline variables that predict disease progression.

## API Examples

### Training a New Model

```bash
# Train with description
curl -X POST "http://localhost:8000/train?description=Initial%20model"
```

### Making Predictions

```bash
# Using latest model version
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]}'

# Using specific model version
curl -X POST "http://localhost:8000/predict?version=v_20240101_120000" \
  -H "Content-Type: application/json" \
  -d '{"features": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]}'
```

### Listing Models

```bash
curl http://localhost:8000/models
```

### Getting Model Info

```bash
curl http://localhost:8000/models/v_20240101_120000
```