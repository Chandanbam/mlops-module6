# MLOps Module 6 - Diabetes Prediction

This project demonstrates MLOps practices using the diabetes dataset from scikit-learn. The project includes data preprocessing, model training, evaluation components, model versioning, monitoring, and a REST API.

## Project Structure

```
mlops-module6/
├── data/                    # Data directory
├── models/                  # Saved models and versioning
│   ├── latest/             # Latest production model
│   └── model_registry.json # Model version metadata
├── src/                    # Source code
│   └── mlops_diabetes/     # Main package
│       ├── __init__.py
│       ├── train.py        # Training script
│       ├── predict.py      # Prediction script
│       ├── utils.py        # Utility functions
│       ├── pipeline.py     # ML pipeline components
│       ├── model_versioning.py  # Model versioning system
│       ├── monitoring.py   # Monitoring and metrics
│       ├── api.py          # FastAPI application
│       └── run_server.py   # Server startup script
├── tests/                  # Test files
├── scripts/                # Deployment and setup scripts
│   ├── deploy_aws.sh      # AWS deployment script
│   ├── setup_ec2.sh       # EC2 setup script
│   ├── docker_push.sh     # Docker image push script
│   └── setup_api_gateway.sh # API Gateway setup script
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Dockerfile for the API
├── prometheus.yml         # Prometheus configuration
├── setup.py              # Package installation configuration
└── README.md             # Project documentation
```

## Setup

### Docker Hub Configuration

1. Create a Docker Hub account if you don't have one:
   - Visit [Docker Hub](https://hub.docker.com) and sign up
   - Note your username and password

2. Configure Docker Hub credentials:
   ```bash
   # For local development (interactive)
   docker login -u your-username
   # Enter your password when prompted
   
   # For CI/CD or scripts (non-interactive)
   echo "$DOCKER_PASS_TOKEN" | docker login -u "$DOCKER_USER_NAME" --password-stdin
   ```

3. Set up GitHub Secrets for CI/CD:
   - Go to your GitHub repository settings
   - Navigate to Secrets and Variables > Actions
   - Add the following secrets:
     - `DOCKER_USER_NAME`: Your Docker Hub username
     - `DOCKER_PASS_TOKEN`: Your Docker Hub access token (create one in Docker Hub account settings)

4. Manual Docker image push (if needed):
   ```bash
   # Build the image
   docker build -t your-username/mlops-diabetes:latest .
   
   # Push to Docker Hub
   docker push your-username/mlops-diabetes:latest
   ```

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

2. Install the package in development mode:
```bash
# The '.' specifies the current directory as the package to install
pip install -e .
```

## Usage

### Command Line Interface

1. Train the model:
```bash
python -m mlops_diabetes.train
```

2. Make predictions:
```bash
python -m mlops_diabetes.predict
```

3. Validate model:
```bash
python -m mlops_diabetes.validate_model --threshold-r2 0.4 --threshold-mse 3000
```

4. Run the API server:
```bash
python -m mlops_diabetes.run_server
```

### Running with Docker Compose

Start the entire stack (API, Prometheus, and Grafana):

1. First, create a `.env` file in the project root:
```bash
# Create .env file in the same directory as docker-compose.yml
cat << EOF > .env
DOCKER_USER_NAME=your-docker-username
VERSION=latest
EOF
```

2. Start the services:
```bash
docker-compose up -d
```

This will start:
- API server on http://localhost:8000
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3000 (default credentials: admin/admin)

### Deployment Scripts

The project includes several deployment scripts in the `scripts/` directory:

1. Deploy to AWS:
```bash
EC2_HOST=your-ec2-host SSH_KEY=path/to/key.pem DOCKER_HUB_USERNAME=username ./scripts/deploy_aws.sh
```

2. Set up EC2 instance:
```bash
./scripts/setup_ec2.sh
```

3. Push Docker image:
```bash
DOCKER_HUB_USERNAME=username ./scripts/docker_push.sh
```

4. Set up API Gateway:
```bash
EC2_HOST=your-ec2-ip ./scripts/setup_api_gateway.sh
```

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
- Keeps the latest production model in `models/latest/`

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
python -m pytest tests/
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
curl -X POST "http://localhost:8000/predict?version=v_20240315_123456" \
  -H "Content-Type: application/json" \
  -d '{"features": [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]}'
```