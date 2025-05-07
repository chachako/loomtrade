import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This is useful for local development if DATABASE_URL is in a .env file
# For production/docker, DATABASE_URL should be set directly as an environment variable.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback or default, though it's better to ensure DATABASE_URL is always set.
    # For PostgreSQL, a typical URL is: postgresql://user:password@host:port/database
    # Example for local Docker setup as per docker-compose.yml:
    # DATABASE_URL = "postgresql://vibetrade_user:vibetrade_password@db:5432/vibetrade_db"
    # However, relying on getenv is preferred.
    # Raising an error or logging a warning might be appropriate if not found.
    print("Warning: DATABASE_URL environment variable not set. Using a default or expecting it to be set elsewhere.")
    # For the purpose of this task, we assume DATABASE_URL will be correctly set in the environment
    # where the application runs (e.g., via docker-compose.yml).
    # If running locally without Docker and without a .env, you'd need to set it manually.
    # For now, let's use a placeholder that matches the docker-compose if nothing is found.
    # This is NOT ideal for production but helps in a dev context if .env is missed.
    DATABASE_URL = "postgresql://vibetrade_user:vibetrade_password@db:5432/vibetrade_db"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Optional: A dependency for FastAPI to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()