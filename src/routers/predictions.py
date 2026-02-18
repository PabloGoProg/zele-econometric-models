"""Rutas de predicción para los modelos econométricos."""

from fastapi import APIRouter, Depends

from src.schemas.predictions import (
    BusinessGrowthPredictionRequest,
    EconGrowthPredictionRequest,
    PredictionResponse,
    UnemploymentPredictionRequest,
)
from src.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predicciones"])


def get_prediction_service() -> PredictionService:
    """Dependencia que provee el servicio de predicción."""
    return PredictionService()


@router.post(
    "/economic-growth",
    response_model=PredictionResponse,
    summary="Predicción de Crecimiento Económico",
    description=(
        "Predice la tasa de crecimiento del PIB de Pereira (Δln PIB) "
        "a partir de variaciones en exportaciones, importaciones, remesas, "
        "inversión y número de empresas."
    ),
)
def predict_economic_growth(
    request: EconGrowthPredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    return service.predict_econ_growth(request)


@router.post(
    "/unemployment",
    response_model=PredictionResponse,
    summary="Predicción de Tasa de Desempleo",
    description=(
        "Predice la variación de la tasa de desempleo en Pereira A.M. (Δln TD) "
        "a partir del crecimiento del PIB, exportaciones, importaciones, "
        "pobreza multidimensional y competitividad departamental."
    ),
)
def predict_unemployment(
    request: UnemploymentPredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    return service.predict_unemployment(request)


@router.post(
    "/business-growth",
    response_model=PredictionResponse,
    summary="Predicción de Crecimiento Empresarial",
    description=(
        "Predice la variación del número de empresas en Pereira (Δln EMP) "
        "a partir del crecimiento del PIB, exportaciones y remesas."
    ),
)
def predict_business_growth(
    request: BusinessGrowthPredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    return service.predict_business_growth(request)
