"""Service for prediction of econometric models."""

import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from sqlalchemy.orm import Session

from src.models.entities import EconModel, User, UserModelVariable, Variable
from src.schemas.predictions import (
    BusinessGrowthPredictionRequest,
    EconGrowthPredictionRequest,
    PredictionResponse,
    UnemploymentPredictionRequest,
)

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "models" / "artifacts" / "v1"

MODEL_CONFIGS = {
    "econ_growth": {
        "artifact": "econ_growth_model.pkl",
        "db_name": "econ_growth",
        "display_name": "Determinantes del Crecimiento Económico de Pereira",
        "target_variable": "delta_ln_PIB",
        "feature_order": [
            "delta_ln_EXP",
            "delta_ln_IMP",
            "delta_ln_REM",
            "delta_ln_INV",
            "delta_ln_EMP",
        ],
    },
    "unemployment": {
        "artifact": "td_model.pkl",
        "db_name": "unemployment",
        "display_name": "Determinantes de la Tasa de Desempleo en Pereira A.M.",
        "target_variable": "delta_ln_TD",
        "feature_order": [
            "delta_ln_PIB",
            "delta_ln_EXP",
            "delta_ln_IMP",
            "IPM",
            "IDC",
        ],
    },
    "business_growth": {
        "artifact": "emp_model.pkl",
        "db_name": "business_growth",
        "display_name": "Determinantes del Crecimiento del Tejido Empresarial",
        "target_variable": "delta_ln_EMP",
        "feature_order": [
            "delta_ln_PIB",
            "delta_ln_EXP",
            "delta_ln_REM",
        ],
    },
}


class PredictionService:
    """Service that loads the econometric models and exposes predictions."""

    def __init__(self) -> None:
        self._models: dict = {}
        for key, config in MODEL_CONFIGS.items():
            self._models[key] = self._load_model(config["artifact"])

    @staticmethod
    def _load_model(filename: str):
        """Load a serialized model from the artifacts folder."""
        path = ARTIFACTS_DIR / filename
        with open(path, "rb") as f:
            return pickle.load(f)

    def _resolve_values(
        self,
        model_key: str,
        request_values: dict[str, float | None],
        user: User,
        db: Session,
    ) -> dict[str, float]:
        """Resolve the final values for the prediction.

        Priority: request value > user saved value > default value.
        """
        config = MODEL_CONFIGS[model_key]
        econ_model = (
            db.query(EconModel).filter(EconModel.name == config["db_name"]).first()
        )

        resolved: dict[str, float] = {}
        for var_name in config["feature_order"]:
            request_val = request_values.get(var_name)
            if request_val is not None:
                resolved[var_name] = request_val
                continue

            variable = db.query(Variable).filter(Variable.name == var_name).first()
            if variable and econ_model:
                umv = (
                    db.query(UserModelVariable)
                    .filter(
                        UserModelVariable.user_id == user.id,
                        UserModelVariable.model_id == econ_model.id,
                        UserModelVariable.variable_id == variable.id,
                    )
                    .first()
                )
                if umv:
                    resolved[var_name] = umv.value
                    continue

            if variable:
                resolved[var_name] = variable.default_value
            else:
                resolved[var_name] = 0.0

        return resolved

    def _persist_values(
        self,
        model_key: str,
        resolved_values: dict[str, float],
        user: User,
        db: Session,
    ) -> None:
        """Persist the values used in the prediction in user_model_variables."""
        config = MODEL_CONFIGS[model_key]
        econ_model = (
            db.query(EconModel).filter(EconModel.name == config["db_name"]).first()
        )
        if not econ_model:
            return

        for var_name, value in resolved_values.items():
            variable = db.query(Variable).filter(Variable.name == var_name).first()
            if not variable:
                continue

            umv = (
                db.query(UserModelVariable)
                .filter(
                    UserModelVariable.user_id == user.id,
                    UserModelVariable.model_id == econ_model.id,
                    UserModelVariable.variable_id == variable.id,
                )
                .first()
            )

            if umv:
                umv.value = value
                umv.updated_at = datetime.now(timezone.utc)
            else:
                umv = UserModelVariable(
                    user_id=user.id,
                    model_id=econ_model.id,
                    variable_id=variable.id,
                    value=value,
                    updated_at=datetime.now(timezone.utc),
                )
                db.add(umv)

        db.commit()

    def _predict(
        self, model_key: str, resolved_values: dict[str, float]
    ) -> PredictionResponse:
        """Execute the prediction with the econometric model."""
        config = MODEL_CONFIGS[model_key]
        stats_model = self._models[model_key]

        features = np.array([[resolved_values[v] for v in config["feature_order"]]])
        features_with_const = sm.add_constant(features, has_constant="add")
        prediction = stats_model.predict(features_with_const)

        return PredictionResponse(
            model_name=config["display_name"],
            prediction=round(float(prediction[0]), 6),
            variable=config["target_variable"],
            r_squared=round(stats_model.rsquared, 4),
            values_used=resolved_values,
        )

    def predict_econ_growth(
        self,
        request: EconGrowthPredictionRequest,
        user: User,
        db: Session,
    ) -> PredictionResponse:
        """Predict Δln PIB — Model 1: Economic Growth of Pereira."""
        request_values = request.model_dump()
        resolved = self._resolve_values("econ_growth", request_values, user, db)
        self._persist_values("econ_growth", resolved, user, db)
        return self._predict("econ_growth", resolved)

    def predict_unemployment(
        self,
        request: UnemploymentPredictionRequest,
        user: User,
        db: Session,
    ) -> PredictionResponse:
        """Predict Δln TD — Model 2: Unemployment in Pereira A.M."""
        request_values = request.model_dump()
        resolved = self._resolve_values("unemployment", request_values, user, db)
        self._persist_values("unemployment", resolved, user, db)
        return self._predict("unemployment", resolved)

    def predict_business_growth(
        self,
        request: BusinessGrowthPredictionRequest,
        user: User,
        db: Session,
    ) -> PredictionResponse:
        """Predict Δln EMP — Model 3: Business Growth."""
        request_values = request.model_dump()
        resolved = self._resolve_values("business_growth", request_values, user, db)
        self._persist_values("business_growth", resolved, user, db)
        return self._predict("business_growth", resolved)
