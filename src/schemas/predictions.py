"""Schemas de entrada y salida para los endpoints de predicción."""

from pydantic import BaseModel, Field


class EconGrowthPredictionRequest(BaseModel):
    """Solicitud de predicción para el modelo de crecimiento económico.

    Todos los campos son opcionales. Si no se proporcionan, se usan los valores
    guardados del perfil del usuario o los valores por defecto de la variable.
    """

    delta_ln_EXP: float | None = Field(
        None, description="Tasa de cambio logarítmica de las exportaciones"
    )
    delta_ln_IMP: float | None = Field(
        None, description="Tasa de cambio logarítmica de las importaciones"
    )
    delta_ln_REM: float | None = Field(
        None, description="Tasa de cambio logarítmica de las remesas"
    )
    delta_ln_INV: float | None = Field(
        None, description="Tasa de cambio logarítmica de la inversión neta"
    )
    delta_ln_EMP: float | None = Field(
        None, description="Tasa de cambio logarítmica del número de empresas"
    )

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "delta_ln_EXP": 0.05,
                "delta_ln_IMP": 0.03,
                "delta_ln_REM": 0.02,
                "delta_ln_INV": 0.01,
                "delta_ln_EMP": 0.04,
            }
        ]
    }}


class UnemploymentPredictionRequest(BaseModel):
    """Solicitud de predicción para el modelo de tasa de desempleo.

    Todos los campos son opcionales. Si no se proporcionan, se usan los valores
    guardados del perfil del usuario o los valores por defecto de la variable.
    """

    delta_ln_PIB: float | None = Field(
        None, description="Tasa de cambio logarítmica del PIB"
    )
    delta_ln_EXP: float | None = Field(
        None, description="Tasa de cambio logarítmica de las exportaciones"
    )
    delta_ln_IMP: float | None = Field(
        None, description="Tasa de cambio logarítmica de las importaciones"
    )
    IPM: float | None = Field(
        None, description="Incidencia de Pobreza Multidimensional de Risaralda"
    )
    IDC: float | None = Field(
        None, description="Índice de Competitividad Departamental (valor normalizado)"
    )

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "delta_ln_PIB": 0.07,
                "delta_ln_EXP": 0.05,
                "delta_ln_IMP": 0.03,
                "IPM": 15.0,
                "IDC": 5.5,
            }
        ]
    }}


class BusinessGrowthPredictionRequest(BaseModel):
    """Solicitud de predicción para el modelo de crecimiento empresarial.

    Todos los campos son opcionales. Si no se proporcionan, se usan los valores
    guardados del perfil del usuario o los valores por defecto de la variable.
    """

    delta_ln_PIB: float | None = Field(
        None, description="Tasa de cambio logarítmica del PIB"
    )
    delta_ln_EXP: float | None = Field(
        None, description="Tasa de cambio logarítmica de las exportaciones"
    )
    delta_ln_REM: float | None = Field(
        None, description="Tasa de cambio logarítmica de las remesas"
    )

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "delta_ln_PIB": 0.07,
                "delta_ln_EXP": 0.05,
                "delta_ln_REM": 0.02,
            }
        ]
    }}


class PredictionResponse(BaseModel):
    """Respuesta de predicción de un modelo econométrico."""

    model_name: str = Field(
        ..., description="Nombre del modelo utilizado"
    )
    prediction: float = Field(
        ..., description="Valor predicho por el modelo (tasa de cambio logarítmica)"
    )
    variable: str = Field(
        ..., description="Variable dependiente predicha"
    )
    r_squared: float = Field(
        ..., description="Coeficiente de determinación (R²) del modelo"
    )
    values_used: dict[str, float] = Field(
        ..., description="Valores de las variables usados para la predicción"
    )
