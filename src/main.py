from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core import settings
from src.database import Base, SessionLocal, engine
from src.api.routers.auth import router as auth_router
from src.api.routers.models import router as models_router
from src.api.routers.predictions import router as predictions_router
from .seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate settings and bootstrap SQLite when needed."""
    settings.validate()

    db_path = Path(settings.SQLITE_DB_PATH)
    should_bootstrap = settings.NODE_ENV == "development" or not db_path.exists()

    if should_bootstrap:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()

    yield


app = FastAPI(
    title="ZELE Econometric Models",
    description=(
        "API for predicting economic indicators for Pereira with OLS "
        "econometric models. It exposes models for economic growth, "
        "unemployment, and business growth. JWT authentication is required "
        "for prediction access."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(models_router, prefix=API_PREFIX)
app.include_router(predictions_router, prefix=API_PREFIX)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
