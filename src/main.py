"""Punto de entrada de la API de modelos econométricos ZELE Pereira."""

from fastapi import FastAPI

from src.routers.predictions import router as predictions_router

app = FastAPI(
    title="ZELE Modelos Econométricos",
    description=(
        "API para la predicción de indicadores económicos de Pereira "
        "mediante modelos econométricos OLS. Expone tres modelos: "
        "crecimiento económico (PIB), tasa de desempleo y tejido empresarial."
    ),
    version="0.1.0",
)

app.include_router(predictions_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    """Verificación de salud de la API."""
    return {"status": "ok"}
