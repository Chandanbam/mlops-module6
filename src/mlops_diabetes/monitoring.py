from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from typing import Dict, Any
import psutil
import time

# Create a registry for custom metrics
registry = CollectorRegistry()

# API Metrics
MODEL_TRAIN_COUNTER = Counter(
    "model_training_total",
    "Total number of model training runs",
    registry=registry
)

PREDICTION_COUNTER = Counter(
    "model_predictions_total",
    "Total number of predictions made",
    ["model_version"],
    registry=registry
)

# Model Performance Metrics
MODEL_METRICS_GAUGE = Gauge(
    "model_performance_metrics",
    "Model performance metrics",
    ["metric_name", "model_version"],
    registry=registry
)

# Prediction Latency
PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds",
    "Time taken for model predictions",
    ["model_version"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

# System Metrics
SYSTEM_MEMORY_USAGE = Gauge(
    "system_memory_usage_bytes",
    "System memory usage in bytes",
    ["type"],
    registry=registry
)

SYSTEM_CPU_USAGE = Gauge(
    "system_cpu_usage_percent",
    "System CPU usage percentage",
    registry=registry
)

def setup_monitoring(app):
    """Set up FastAPI monitoring with custom metrics."""
    
    # Initialize FastAPI instrumentator
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[".*admin.*", "/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="fastapi_inprogress",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.add(
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_namespace="fastapi",
            metric_subsystem="http",
        )
    ).add(
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_namespace="fastapi",
            metric_subsystem="http",
        )
    ).add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_namespace="fastapi",
            metric_subsystem="http",
        )
    ).add(
        metrics.requests(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
            metric_namespace="fastapi",
            metric_subsystem="http",
        )
    )

    # Instrument app
    instrumentator.instrument(app).expose(app, include_in_schema=True, should_gzip=True)

def record_prediction_metrics(version: str, latency: float):
    """Record metrics for a prediction."""
    PREDICTION_COUNTER.labels(model_version=version).inc()
    PREDICTION_LATENCY.labels(model_version=version).observe(latency)

def record_training_metrics(version: str, metrics: Dict[str, float]):
    """Record metrics from model training."""
    MODEL_TRAIN_COUNTER.inc()
    
    # Record each metric
    for metric_name, value in metrics.items():
        MODEL_METRICS_GAUGE.labels(
            metric_name=metric_name,
            model_version=version
        ).set(value)

def update_system_metrics():
    """Update system resource metrics."""
    # Memory metrics
    memory = psutil.virtual_memory()
    SYSTEM_MEMORY_USAGE.labels(type="total").set(memory.total)
    SYSTEM_MEMORY_USAGE.labels(type="available").set(memory.available)
    SYSTEM_MEMORY_USAGE.labels(type="used").set(memory.used)
    
    # CPU metrics
    SYSTEM_CPU_USAGE.set(psutil.cpu_percent(interval=1)) 