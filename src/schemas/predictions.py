"""Schemas for input and output for prediction endpoints."""

from pydantic import BaseModel, Field


class EconGrowthPredictionRequest(BaseModel):
    """Prediction request for the economic growth model.

    All fields are optional. If not provided, the values saved from the user's profile or the default values of the variable are used.
    The values used are saved in the user's profile.

    Attributes:
        delta_ln_EXP: Logarithmic change rate of exports
        delta_ln_IMP: Logarithmic change rate of imports
        delta_ln_REM: Logarithmic change rate of remittances
        delta_ln_INV: Logarithmic change rate of net investment
        delta_ln_EMP: Logarithmic change rate of number of businesses
    """

    delta_ln_EXP: float | None = Field(
        None, description="Logarithmic change rate of exports"
    )
    delta_ln_IMP: float | None = Field(
        None, description="Logarithmic change rate of imports"
    )
    delta_ln_REM: float | None = Field(
        None, description="Logarithmic change rate of remittances"
    )
    delta_ln_INV: float | None = Field(
        None, description="Logarithmic change rate of net investment"
    )
    delta_ln_EMP: float | None = Field(
        None, description="Logarithmic change rate of number of businesses"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "delta_ln_EXP": 0.05,
                    "delta_ln_IMP": 0.03,
                    "delta_ln_REM": 0.02,
                    "delta_ln_INV": 0.01,
                    "delta_ln_EMP": 0.04,
                }
            ]
        }
    }


class UnemploymentPredictionRequest(BaseModel):
    """Prediction request for the unemployment model.

    All fields are optional. If not provided, the values saved from the user's profile or the default values of the variable are used.
    The values used are saved in the user's profile.

    Attributes:
        delta_ln_PIB: Logarithmic change rate of PIB
        delta_ln_EXP: Logarithmic change rate of exports
        delta_ln_IMP: Logarithmic change rate of imports
        IPM: Incidence of Multidimensional Poverty in Risaralda
        IDC: Departmental Competitiveness Index (normalized value)
    """

    delta_ln_PIB: float | None = Field(
        None, description="Logarithmic change rate of PIB"
    )
    delta_ln_EXP: float | None = Field(
        None, description="Logarithmic change rate of exports"
    )
    delta_ln_IMP: float | None = Field(
        None, description="Logarithmic change rate of imports"
    )
    IPM: float | None = Field(
        None, description="Incidence of Multidimensional Poverty in Risaralda"
    )
    IDC: float | None = Field(
        None, description="Departmental Competitiveness Index (normalized value)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "delta_ln_PIB": 0.07,
                    "delta_ln_EXP": 0.05,
                    "delta_ln_IMP": 0.03,
                    "IPM": 15.0,
                    "IDC": 5.5,
                }
            ]
        }
    }


class BusinessGrowthPredictionRequest(BaseModel):
    """Prediction request for the business growth model.

    All fields are optional. If not provided, the values saved from the user's profile or the default values of the variable are used.
    The values used are saved in the user's profile.

    Attributes:
        delta_ln_PIB: Logarithmic change rate of PIB
        delta_ln_EXP: Logarithmic change rate of exports
        delta_ln_REM: Logarithmic change rate of remittances
    """

    delta_ln_PIB: float | None = Field(
        None, description="Logarithmic change rate of PIB"
    )
    delta_ln_EXP: float | None = Field(
        None, description="Logarithmic change rate of exports"
    )
    delta_ln_REM: float | None = Field(
        None, description="Logarithmic change rate of remittances"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "delta_ln_PIB": 0.07,
                    "delta_ln_EXP": 0.05,
                    "delta_ln_REM": 0.02,
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Prediction response for an econometric model.
    
    Attributes:
        model_name: Name of the model used.
        prediction: Predicted value by the model (logarithmic change rate)
        variable: Dependent variable predicted
        r_squared: Coefficient of determination (R²) of the model
        values_used: Values of the variables used for the prediction
        contributions: Contribution of each variable to the result (coef × value)
        version: Version of the model
        trained_at: Date of training of the model
    """

    model_name: str = Field(..., description="Name of the model used")
    prediction: float = Field(
        ..., description="Predicted value by the model (logarithmic change rate)"
    )
    variable: str = Field(..., description="Dependent variable predicted")
    r_squared: float = Field(
        ..., description="Coefficient of determination (R²) of the model"
    )
    values_used: dict[str, float] = Field(
        ..., description="Values of the variables used for the prediction"
    )
    contributions: dict[str, float] = Field(
        ..., description="Contribution of each variable to the result (coef × value)"
    )
    version: str = Field(..., description="Version of the model")
    trained_at: str = Field(..., description="Date of training of the model")
