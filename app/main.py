from fastapi import FastAPI

from app.api.users import router as users_router

app = FastAPI(
    title="QA Demo Platform",
    version="0.1.0",
)

app.include_router(users_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "qa-demo-platform",
    }
