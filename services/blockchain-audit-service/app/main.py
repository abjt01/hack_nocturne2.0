from fastapi import FastAPI
from app.routes import router
from app import database
import os

app = FastAPI(
    title="Python Blockchain Backend",
    description="Microservice to interact with Ethereum Hardhat for Audit Logging",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    database.init_db()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    from app.config import SERVICE_PORT
    uvicorn.run("app.main:app", host="0.0.0.0", port=SERVICE_PORT, reload=False)
