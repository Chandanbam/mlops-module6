import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "mlops_diabetes.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    ) 