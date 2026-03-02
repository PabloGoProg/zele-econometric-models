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
    """
    Startup event: create tables and execute seed data.
    """
    settings.validate()

    # Asegurar que el directorio data/ existe (requerido para SQLite en Render)
    # db_path = Path(settings.SQLITE_DB_PATH)
    # db_path.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="ZELE Modelos Econométricos",
    description=(
        "API para la predicción de indicadores económicos de Pereira "
        "mediante modelos econométricos OLS. Expone tres modelos: "
        "crecimiento económico (PIB), tasa de desempleo y tejido empresarial. "
        "Requiere autenticación JWT para acceder a las predicciones."
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
