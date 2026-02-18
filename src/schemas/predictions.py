"""Schemas de entrada y salida para los endpoints de predicción."""

from pydantic import BaseModel, Field


class EconGrowthPredictionRequest(BaseModel):
    """Solicitud de predicción para el modelo de crecimiento económico.

    Variables explicativas (tasas de cambio logarítmicas):
        - delta_ln_EXP: Δln(Exportaciones)
        - delta_ln_IMP: Δln(Importaciones)
        - delta_ln_REM: Δln(Remesas)
        - delta_ln_INV: Δln(Inversión)
        - delta_ln_EMP: Δln(Empresas)
    """

    delta_ln_EXP: float = Field(
        ..., description="Tasa de cambio logarítmica de las exportaciones"
    )
    delta_ln_IMP: float = Field(
        ..., description="Tasa de cambio logarítmica de las importaciones"
    )
    delta_ln_REM: float = Field(
        ..., description="Tasa de cambio logarítmica de las remesas"
    )
    delta_ln_INV: float = Field(
        ..., description="Tasa de cambio logarítmica de la inversión neta"
    )
    delta_ln_EMP: float = Field(
        ..., description="Tasa de cambio logarítmica del número de empresas"
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

    Variables explicativas:
        - delta_ln_PIB: Δln(PIB)
        - delta_ln_EXP: Δln(Exportaciones)
        - delta_ln_IMP: Δln(Importaciones)
        - IPM: Incidencia de Pobreza Multidimensional
        - IDC: Índice de Competitividad Departamental
    """

    delta_ln_PIB: float = Field(
        ..., description="Tasa de cambio logarítmica del PIB"
    )
    delta_ln_EXP: float = Field(
        ..., description="Tasa de cambio logarítmica de las exportaciones"
    )
    delta_ln_IMP: float = Field(
        ..., description="Tasa de cambio logarítmica de las importaciones"
    )
    IPM: float = Field(
        ..., description="Incidencia de Pobreza Multidimensional de Risaralda"
    )
    IDC: float = Field(
        ..., description="Índice de Competitividad Departamental (valor normalizado)"
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

    Variables explicativas (tasas de cambio logarítmicas):
        - delta_ln_PIB: Δln(PIB)
        - delta_ln_EXP: Δln(Exportaciones)
        - delta_ln_REM: Δln(Remesas)
    """

    delta_ln_PIB: float = Field(
        ..., description="Tasa de cambio logarítmica del PIB"
    )
    delta_ln_EXP: float = Field(
        ..., description="Tasa de cambio logarítmica de las exportaciones"
    )
    delta_ln_REM: float = Field(
        ..., description="Tasa de cambio logarítmica de las remesas"
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
