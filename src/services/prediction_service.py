"""Servicio de predicción para los modelos econométricos."""

import pickle
from pathlib import Path

import numpy as np
import statsmodels.api as sm

from src.schemas.predictions import (
    BusinessGrowthPredictionRequest,
    EconGrowthPredictionRequest,
    PredictionResponse,
    UnemploymentPredictionRequest,
)

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "models" / "artifacts" / "v1"


class PredictionService:
    """Servicio que carga los modelos econométricos y expone predicciones."""

    def __init__(self) -> None:
        self._econ_growth_model = self._load_model("econ_growth_model.pkl")
        self._td_model = self._load_model("td_model.pkl")
        self._emp_model = self._load_model("emp_model.pkl")

    @staticmethod
    def _load_model(filename: str):
        """Carga un modelo serializado desde la carpeta de artefactos."""
        path = ARTIFACTS_DIR / filename
        with open(path, "rb") as f:
            return pickle.load(f)

    def predict_econ_growth(
        self, request: EconGrowthPredictionRequest
    ) -> PredictionResponse:
        """Predice la tasa de crecimiento económico (Δln PIB).

        Modelo 1: Determinantes del Crecimiento Económico de Pereira.
        """
        features = np.array([[
            request.delta_ln_EXP,
            request.delta_ln_IMP,
            request.delta_ln_REM,
            request.delta_ln_INV,
            request.delta_ln_EMP,
        ]])
        features_with_const = sm.add_constant(features, has_constant="add")
        prediction = self._econ_growth_model.predict(features_with_const)

        return PredictionResponse(
            model_name="Determinantes del Crecimiento Económico de Pereira",
            prediction=round(float(prediction[0]), 6),
            variable="delta_ln_PIB",
            r_squared=round(self._econ_growth_model.rsquared, 4),
        )

    def predict_unemployment(
        self, request: UnemploymentPredictionRequest
    ) -> PredictionResponse:
        """Predice la variación de la tasa de desempleo (Δln TD).

        Modelo 2: Determinantes de la Tasa de Desempleo en Pereira A.M.
        """
        features = np.array([[
            request.delta_ln_PIB,
            request.delta_ln_EXP,
            request.delta_ln_IMP,
            request.IPM,
            request.IDC,
        ]])
        features_with_const = sm.add_constant(features, has_constant="add")
        prediction = self._td_model.predict(features_with_const)

        return PredictionResponse(
            model_name="Determinantes de la Tasa de Desempleo en Pereira A.M.",
            prediction=round(float(prediction[0]), 6),
            variable="delta_ln_TD",
            r_squared=round(self._td_model.rsquared, 4),
        )

    def predict_business_growth(
        self, request: BusinessGrowthPredictionRequest
    ) -> PredictionResponse:
        """Predice la variación del tejido empresarial (Δln EMP).

        Modelo 3: Determinantes del Crecimiento del Tejido Empresarial.
        """
        features = np.array([[
            request.delta_ln_PIB,
            request.delta_ln_EXP,
            request.delta_ln_REM,
        ]])
        features_with_const = sm.add_constant(features, has_constant="add")
        prediction = self._emp_model.predict(features_with_const)

        return PredictionResponse(
            model_name="Determinantes del Crecimiento del Tejido Empresarial",
            prediction=round(float(prediction[0]), 6),
            variable="delta_ln_EMP",
            r_squared=round(self._emp_model.rsquared, 4),
        )
