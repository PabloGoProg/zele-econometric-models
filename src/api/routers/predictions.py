"""JWT-protected prediction routes for the econometric models."""

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

router = APIRouter(prefix="/predictions", tags=["Predictions"])

_prediction_service = PredictionService()


@router.post(
    "/economic-growth",
    response_model=PredictionResponse,
    summary="Economic growth prediction",
    description=(
        "Predict Pereira GDP growth (delta_ln_PIB). Fields are optional; "
        "omitted values use saved user values or seeded defaults. The values "
        "used are saved to the user's profile."
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
    summary="Unemployment prediction",
    description=(
        "Predict the unemployment rate change for Pereira A.M. (delta_ln_TD). "
        "Fields are optional; omitted values use saved user values or seeded "
        "defaults. The values used are saved to the user's profile."
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
    summary="Business growth prediction",
    description=(
        "Predict the change in Pereira active businesses (delta_ln_EMP). "
        "Fields are optional; omitted values use saved user values or seeded "
        "defaults. The values used are saved to the user's profile."
    ),
)
def predict_business_growth(
    request: BusinessGrowthPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    return _prediction_service.predict_business_growth(request, current_user, db)
