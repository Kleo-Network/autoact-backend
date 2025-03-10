# AutoAct Backend Reference

## Commands
- **Run API server**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Docker deployment**: `docker-compose -f dockerfiles/docker-compose.yml up -d`
- **Run a test file**: `python -m app.tests.form` (replace with specific test module)
- **Install dependencies**: `pip install -r requirements.txt`

## Code Style Guidelines
- **Framework**: FastAPI with MongoDB for storage
- **Naming**: snake_case for variables/functions, CamelCase for classes, ALL_CAPS for constants
- **Typing**: Use type hints everywhere with Pydantic models for validation
- **Imports**: Group by standard lib → third-party → local (app.*)
- **Error handling**: Use try/except with FastAPI HTTPException for API errors
- **Logging**: Use app's logger with appropriate level (app.logging_config)
- **API structure**: Routes in app/api/, models in app/models/, business logic in app/services/
- **Documentation**: Docstrings for functions, inline comments for complex logic
- **Environment**: Config via settings.py with dotenv for environment variables