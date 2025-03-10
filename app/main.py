# app/main.py
from app.mongodb import close_db_connection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.form import router as form_router
from app.api.form_detect import router as form_detect_router
from app.settings import settings
from app.logging_config import setup_logging, logger
from prometheus_fastapi_instrumentator import Instrumentator

# Set up logging
setup_logging()

app = FastAPI(title=settings.PROJECT_NAME)


# Add CORS middleware
origins = [
    "http://localhost:5173",  # Your local development
    "https://www.app.kleo.network",  # Your deployed app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows only these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the API routers
app.include_router(form_router, prefix="/api/v1/form")
app.include_router(form_detect_router, prefix="/api/v1")

Instrumentator().instrument(app).expose(app)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}


# Optional: Log startup events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the FastAPI application.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the FastAPI application.")
    await close_db_connection()
