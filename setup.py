from setuptools import setup, find_packages

setup(
    name="mlops-diabetes",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.2.0",
        "matplotlib>=3.7.0",
        "pytest>=7.3.1",
        "python-dotenv>=1.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.2",
        "prometheus-client>=0.19.0",
        "prometheus-fastapi-instrumentator>=6.1.0",
        "psutil>=5.9.0"
    ],
    python_requires=">=3.9",
) 