"""Rutas de predicción para los modelos econométricos (protegidas con JWT)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.entities import User
from src.schemas.predictions import (
    BusinessGrowthPredictionRequest,
    EconGrowthPredictionRequest,
    PredictionResponse,
    UnemploymentPredictionRequest,
)
from src.services.auth_service import get_current_user
from src.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predicciones"])

_prediction_service = PredictionService()


@router.post(
    "/economic-growth",
    response_model=PredictionResponse,
    summary="Predicción de Crecimiento Económico",
    description=(
        "Predice la tasa de crecimiento del PIB de Pereira (Δln PIB). "
        "Los campos son opcionales: si no se envían, se usan los valores "
        "guardados del usuario o los valores por defecto. "
        "Los valores usados se guardan en el perfil del usuario."
    ),
)
def predict_economic_growth(
    request: EconGrowthPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    return _prediction_service.predict_econ_growth(request, current_user, db)


@router.post(
    "/unemployment",
    response_model=PredictionResponse,
    summary="Predicción de Tasa de Desempleo",
    description=(
        "Predice la variación de la tasa de desempleo en Pereira A.M. (Δln TD). "
        "Los campos son opcionales: si no se envían, se usan los valores "
        "guardados del usuario o los valores por defecto. "
        "Los valores usados se guardan en el perfil del usuario."
    ),
)
def predict_unemployment(
    request: UnemploymentPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    return _prediction_service.predict_unemployment(request, current_user, db)


@router.post(
    "/business-growth",
    response_model=PredictionResponse,
    summary="Predicción de Crecimiento Empresarial",
    description=(
        "Predice la variación del número de empresas en Pereira (Δln EMP). "
        "Los campos son opcionales: si no se envían, se usan los valores "
        "guardados del usuario o los valores por defecto. "
        "Los valores usados se guardan en el perfil del usuario."
    ),
)
def predict_business_growth(
    request: BusinessGrowthPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    return _prediction_service.predict_business_growth(request, current_user, db)
