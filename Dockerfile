# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install the package and test dependencies
COPY . .
RUN pip install -e . && \
    pip install pytest pytest-cov flake8

# Run tests and linting
RUN flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics && \
    pytest tests/ --cov=src/ --cov-report=xml && \
    python src/train_model.py && \
    python src/validate_model.py --threshold-r2 0.4 --threshold-mse 3000

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only runtime dependencies from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/

# Copy application code and package
COPY src/ ./src/
COPY models/ ./models/
COPY setup.py .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/models
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "mlops_diabetes.api:app", "--host", "0.0.0.0", "--port", "8000"] 