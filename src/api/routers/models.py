"""Rutas para listado de modelos, schema y predicción genérica."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.entities import EconModel, User
from src.schemas.models import (
    GenericPredictRequest,
    ModelListItem,
    ModelSchemaResponse,
    VariableSchemaItem,
)
from src.schemas.predictions import PredictionResponse
from src.services.prediction_service import DB_NAME_TO_KEY, PredictionService
from src.services.rate_limiter import check_rate_limit

router = APIRouter(prefix="/models", tags=["Modelos"])

_prediction_service = PredictionService()


@router.get(
    "",
    response_model=list[ModelListItem],
    summary="Listar modelos",
    description="Retorna la lista de modelos econométricos disponibles.",
)
def list_models(db: Session = Depends(get_db)):
    models = db.query(EconModel).all()
    return models


@router.get(
    "/{model_id}/schema",
    response_model=ModelSchemaResponse,
    summary="Schema del modelo",
    description="Retorna el schema completo de un modelo con sus variables y metadata.",
)
def get_model_schema(model_id: int, db: Session = Depends(get_db)):
    econ_model = db.query(EconModel).filter(EconModel.id == model_id).first()
    if not econ_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado",
        )

    model_key = DB_NAME_TO_KEY.get(econ_model.name)
    r_squared = _prediction_service.get_r_squared(model_key) if model_key else 0.0

    variables = [
        VariableSchemaItem.model_validate(v)
        for v in econ_model.variables
    ]

    return ModelSchemaResponse(
        id=econ_model.id,
        name=econ_model.name,
        display_name=econ_model.display_name,
        description=econ_model.description,
        version=econ_model.version,
        trained_at=econ_model.trained_at,
        target_variable=econ_model.target_variable,
        r_squared=r_squared,
        variables=variables,
    )


@router.get(
    "/{model_id}/variables",
    response_model=list[VariableSchemaItem],
    summary="Variables del modelo",
    description="Retorna las variables de entrada del modelo con metadata para UI.",
)
def get_model_variables(model_id: int, db: Session = Depends(get_db)):
    econ_model = db.query(EconModel).filter(EconModel.id == model_id).first()
    if not econ_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado",
        )

    return [VariableSchemaItem.model_validate(v) for v in econ_model.variables]


@router.post(
    "/{model_id}/predict",
    response_model=PredictionResponse,
    summary="Predicción genérica",
    description=(
        "Ejecuta una predicción para el modelo indicado. "
        "El body debe contener un diccionario de valores por variable. "
        "Las variables no enviadas usarán los valores guardados del usuario o los defaults."
    ),
)
def predict(
    model_id: int,
    request: GenericPredictRequest,
    current_user: User = Depends(check_rate_limit),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    return _prediction_service.predict_by_model_id(
        model_id, request.values, current_user, db
    )
