from fastapi import FastAPI

app = FastAPI(
    title="QA Demo Platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
      "status": "healthy",
      "service": "qa-demo-platform",
    }
