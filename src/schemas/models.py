"""Schemas for model listing, schema, variables, and generic prediction APIs."""

from pydantic import BaseModel, Field


class ModelListItem(BaseModel):
    """Compact item returned by the model listing endpoint."""

    id: int
    name: str
    display_name: str
    description: str

    model_config = {"from_attributes": True}


class VariableSchemaItem(BaseModel):
    """Variable metadata exposed in model schema responses."""

    name: str
    display_name: str
    description: str
    meaning: str
    value_type: str
    default_value: float
    min: float = Field(..., validation_alias="min_value")
    max: float = Field(..., validation_alias="max_value")
    step: float

    model_config = {"from_attributes": True, "populate_by_name": True}


class ModelSchemaResponse(BaseModel):
    """Full model schema with model metadata and input variables."""

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
    """Generic prediction request keyed by variable name."""

    values: dict[str, float] = Field(
        ..., description="Variable values to use for the prediction"
    )
