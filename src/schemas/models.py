"""Schemas para los endpoints de modelos (listado y schema)."""

from pydantic import BaseModel, Field


class ModelListItem(BaseModel):
    """Elemento del listado de modelos."""

    id: int
    name: str
    display_name: str
    description: str

    model_config = {"from_attributes": True}


class VariableSchemaItem(BaseModel):
    """Descripción de una variable dentro del schema de un modelo."""

    name: str
    description: str
    meaning: str
    default_value: float
    min: float = Field(..., validation_alias="min_value")
    max: float = Field(..., validation_alias="max_value")
    step: float

    model_config = {"from_attributes": True, "populate_by_name": True}


class ModelSchemaResponse(BaseModel):
    """Schema completo de un modelo con sus variables y metadata."""

    id: int
    name: str
    display_name: str
    description: str
    version: str
    trained_at: str
    target_variable: str
    r_squared: float
    variables: list[VariableSchemaItem]


class GenericPredictRequest(BaseModel):
    """Solicitud genérica de predicción: diccionario de valores por variable."""

    values: dict[str, float] = Field(
        ..., description="Valores de las variables para la predicción"
    )
