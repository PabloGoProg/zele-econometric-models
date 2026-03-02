"""
Prediction service for OLS econometric models.

This module is the core inference layer of the application. It loads pre-trained
OLS (Ordinary Least Squares) regression models from serialized pickle artifacts
and exposes methods to run predictions against them.

Architecture overview
---------------------
Each econometric model is:
  1. **Trained offline** with statsmodels and serialized as a `.pkl` file
     under ``src/models/artifacts/v1/``.
  2. **Registered in the database** as an ``EconModel`` row, linked to its
     ``Variable`` rows through the ``model_variables`` junction table.
  3. **Loaded at startup** by ``PredictionService.__init__`` into an in-memory
     dictionary keyed by a short internal identifier (e.g. ``"econ_growth"``).

Variable resolution strategy
----------------------------
When a prediction is requested the caller may omit some (or all) feature
values. The service resolves every feature with a three-tier fallback:

    request value  →  user-saved value  →  variable default value

After resolution the final values are **persisted** back to
``user_model_variables`` so the next request for the same user+model will
reuse them as the second-tier fallback.

Available models
----------------
+-------------------+---------------------+--------------------------------------+
| Internal key      | DB name             | Predicts (target variable)           |
+===================+=====================+======================================+
| econ_growth       | econ_growth         | Δln PIB  (GDP growth)                |
+-------------------+---------------------+--------------------------------------+
| unemployment      | unemployment        | Δln TD   (unemployment rate change)  |
+-------------------+---------------------+--------------------------------------+
| business_growth   | business_growth     | Δln EMP  (business fabric growth)    |
+-------------------+---------------------+--------------------------------------+
"""

import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.entities import EconModel, User, UserModelVariable, Variable
from src.schemas.predictions import (
    BusinessGrowthPredictionRequest,
    EconGrowthPredictionRequest,
    PredictionResponse,
    UnemploymentPredictionRequest,
)

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "models" / "artifacts" / "v1"
"""Absolute path to the directory that stores serialized model artifacts."""

MODEL_CONFIGS: dict[str, dict] = {
    # ── Model 1: Economic Growth ─────────────────────────────────────────
    "econ_growth": {
        "artifact": "econ_growth_model.pkl",
        "db_name": "econ_growth",
        "display_name": "Determinantes del Crecimiento Económico de Pereira",
        "target_variable": "delta_ln_PIB",
        "version": "1.0.0",
        "trained_at": "2025-06-15",
        # Order must match the column order used during training
        "feature_order": [
            "delta_ln_EXP",   # Δln Exports
            "delta_ln_IMP",   # Δln Imports
            "delta_ln_REM",   # Δln Remittances
            "delta_ln_INV",   # Δln Net Investment
            "delta_ln_EMP",   # Δln Number of Businesses
        ],
    },
    # ── Model 2: Unemployment ────────────────────────────────────────────
    "unemployment": {
        "artifact": "td_model.pkl",
        "db_name": "unemployment",
        "display_name": "Determinantes de la Tasa de Desempleo en Pereira A.M.",
        "target_variable": "delta_ln_TD",
        "version": "1.0.0",
        "trained_at": "2025-06-15",
        "feature_order": [
            "delta_ln_PIB",   # Δln GDP
            "delta_ln_EXP",   # Δln Exports
            "delta_ln_IMP",   # Δln Imports
            "IPM",            # Multidimensional Poverty Index
            "IDC",            # Departmental Competitiveness Index
        ],
    },
    # ── Model 3: Business Growth ─────────────────────────────────────────
    "business_growth": {
        "artifact": "emp_model.pkl",
        "db_name": "business_growth",
        "display_name": "Determinantes del Crecimiento del Tejido Empresarial",
        "target_variable": "delta_ln_EMP",
        "version": "1.0.0",
        "trained_at": "2025-06-15",
        "feature_order": [
            "delta_ln_PIB",   # Δln GDP
            "delta_ln_EXP",   # Δln Exports
            "delta_ln_REM",   # Δln Remittances
        ],
    },
}
"""
Static registry that maps each internal model key to its configuration.

Keys in each config dict:
    artifact       – Filename of the serialized `.pkl` model inside ARTIFACTS_DIR.
    db_name        – The ``EconModel.name`` value stored in the database.
    display_name   – Human-readable name returned in API responses.
    target_variable – Name of the dependent (predicted) variable.
    version        – Semantic version of the trained artifact.
    trained_at     – ISO date when the model was last trained.
    feature_order  – Ordered list of independent variable names; must match
                     the column order the model was trained with.
"""

DB_NAME_TO_KEY: dict[str, str] = {
    cfg["db_name"]: key for key, cfg in MODEL_CONFIGS.items()
}
"""Reverse lookup: maps a database model name to its internal config key."""


class PredictionService:
    """
    Stateful service that loads OLS econometric models at instantiation time
    and provides prediction capabilities through a unified interface.

    This class is designed to be instantiated **once** at application startup
    (typically as a FastAPI dependency) so the pickle deserialization cost is
    paid only once.

    Attributes:
        _models: In-memory cache mapping internal model keys (e.g.
                 ``"econ_growth"``) to their deserialized statsmodels
                 ``RegressionResultsWrapper`` objects.
    """

    def __init__(self) -> None:
        self._models: dict[str, sm.regression.linear_model.RegressionResultsWrapper] = {}
        for key, config in MODEL_CONFIGS.items():
            self._models[key] = self._load_model(config["artifact"])

    @staticmethod
    def _load_model(filename: str):
        """Deserialize a statsmodels OLS result from a pickle artifact.

        Args:
            filename: Name of the ``.pkl`` file inside ``ARTIFACTS_DIR``.

        Returns:
            A fitted statsmodels ``RegressionResultsWrapper`` ready for
            ``.predict()`` calls.
        """
        path = ARTIFACTS_DIR / filename
        with open(path, "rb") as f:
            return pickle.load(f)

    def get_r_squared(self, model_key: str) -> float:
        """Return the coefficient of determination (R²) for a loaded model.

        R² indicates how well the independent variables explain the variance
        of the dependent variable. Values closer to 1.0 indicate a better fit.

        Args:
            model_key: Internal identifier (must be a key in ``MODEL_CONFIGS``).

        Returns:
            R² rounded to four decimal places.
        """
        return round(self._models[model_key].rsquared, 4)

    def _resolve_values(
        self,
        model_key: str,
        request_values: dict[str, float | None],
        user: User,
        db: Session,
    ) -> dict[str, float]:
        """Resolve every feature value needed for prediction using a three-tier fallback.

        For each variable in the model's ``feature_order`` the resolution
        follows this priority chain:

        1. **Request value** – explicitly provided by the caller in the current
           request payload. This takes highest priority.
        2. **User-saved value** – previously persisted in ``user_model_variables``
           from an earlier prediction by the same user on the same model.
        3. **Variable default** – the ``default_value`` column on the
           ``variables`` table (seeded at database init). Falls back to ``0.0``
           if the variable row is missing entirely.

        Args:
            model_key:      Internal identifier (key in ``MODEL_CONFIGS``).
            request_values: Mapping of variable names to caller-supplied values;
                            ``None`` entries trigger the fallback chain.
            user:           Authenticated user making the request.
            db:             Active SQLAlchemy session.

        Returns:
            A dict mapping every feature name to a concrete ``float`` value,
            guaranteed to contain all entries in ``feature_order``.
        """
        config = MODEL_CONFIGS[model_key]

        econ_model = (
            db.query(EconModel).filter(EconModel.name == config["db_name"]).first()
        )

        resolved: dict[str, float] = {}

        for var_name in config["feature_order"]:
            # Tier 1: explicit request value
            request_val = request_values.get(var_name)
            if request_val is not None:
                resolved[var_name] = request_val
                continue

            variable = db.query(Variable).filter(Variable.name == var_name).first()

            # Tier 2: previously saved value for this (user, model, variable) triple
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

            # Tier 3: global default from the variables table
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
        """Save the resolved feature values so they become the Tier-2 fallback
        for subsequent predictions by the same user on the same model.

        For each (user, model, variable) triple the method performs an
        **upsert**: if a ``UserModelVariable`` row already exists it updates
        the value and timestamp; otherwise it inserts a new row.

        The entire batch is committed in a single transaction.

        Args:
            model_key:       Internal identifier (key in ``MODEL_CONFIGS``).
            resolved_values: Fully resolved feature dict (output of
                             ``_resolve_values``).
            user:            Authenticated user making the request.
            db:              Active SQLAlchemy session.
        """
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

    def _compute_contributions(
        self, model_key: str, resolved_values: dict[str, float]
    ) -> dict[str, float]:
        """Calculate each independent variable's individual contribution to
        the predicted value.

        In a linear model  ŷ = β₀ + β₁x₁ + β₂x₂ + … + βₖxₖ  the
        "contribution" of variable *i* is simply  βᵢ · xᵢ.  This allows
        the frontend to display a decomposition of the prediction so users
        can see which variables drive the result the most.

        Note:
            ``params.iloc[0]`` is the intercept (constant term), so feature
            coefficients start at index 1.

        Args:
            model_key:       Internal identifier (key in ``MODEL_CONFIGS``).
            resolved_values: Fully resolved feature dict.

        Returns:
            A dict mapping each feature name to its rounded contribution.
        """
        config = MODEL_CONFIGS[model_key]
        stats_model = self._models[model_key]
        params = stats_model.params

        contributions: dict[str, float] = {}
        for i, var_name in enumerate(config["feature_order"]):
            coef = float(params.iloc[i + 1])
            contributions[var_name] = round(coef * resolved_values[var_name], 6)

        return contributions

    def _predict(
        self, model_key: str, resolved_values: dict[str, float]
    ) -> PredictionResponse:
        """Run the OLS model forward-pass and build a full response payload.

        Steps:
        1. Assemble the feature vector in the exact column order the model
           was trained with (``feature_order``).
        2. Prepend a constant (intercept) column via ``sm.add_constant``
           because statsmodels OLS does not include the intercept
           automatically at prediction time.
        3. Call ``model.predict()`` to obtain ŷ.
        4. Compute per-variable contributions for interpretability.
        5. Package everything into a ``PredictionResponse``.

        Args:
            model_key:       Internal identifier (key in ``MODEL_CONFIGS``).
            resolved_values: Fully resolved feature dict.

        Returns:
            A ``PredictionResponse`` containing the prediction, metadata,
            the values that were actually used, and each variable's
            contribution breakdown.
        """
        config = MODEL_CONFIGS[model_key]
        stats_model = self._models[model_key]

        features = np.array([[resolved_values[v] for v in config["feature_order"]]])
        features_with_const = sm.add_constant(features, has_constant="add")
        prediction = stats_model.predict(features_with_const)

        contributions = self._compute_contributions(model_key, resolved_values)

        return PredictionResponse(
            model_name=config["display_name"],
            prediction=round(float(prediction[0]), 6),
            variable=config["target_variable"],
            r_squared=round(stats_model.rsquared, 4),
            values_used=resolved_values,
            contributions=contributions,
            version=config["version"],
            trained_at=config["trained_at"],
        )

    # ── Public prediction entry-points ─────────────────────────────────

    def predict_by_model_id(
        self,
        model_id: int,
        values: dict[str, float],
        user: User,
        db: Session,
    ) -> PredictionResponse:
        """Unified prediction endpoint that accepts any model by its database
        primary key.

        This is the **preferred** entry-point used by the generic
        ``POST /models/{model_id}/predict`` router. It looks up the
        ``EconModel`` row, maps it to the internal config key, and delegates
        to the resolve → persist → predict pipeline.

        Args:
            model_id: Primary key of the ``EconModel`` row in the database.
            values:   Caller-supplied feature values (may be partial).
            user:     Authenticated user.
            db:       Active SQLAlchemy session.

        Returns:
            A ``PredictionResponse`` with prediction, metadata, and
            contribution breakdown.

        Raises:
            HTTPException 404: If the model ID doesn't exist in the database
                or if the database model has no corresponding prediction
                artifact registered in ``MODEL_CONFIGS``.
        """
        econ_model = db.query(EconModel).filter(EconModel.id == model_id).first()
        if not econ_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Modelo no encontrado",
            )

        model_key = DB_NAME_TO_KEY.get(econ_model.name)
        if not model_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El modelo no tiene un artefacto de predicción asociado",
            )

        request_values: dict[str, float | None] = {}
        config = MODEL_CONFIGS[model_key]
        for var_name in config["feature_order"]:
            request_values[var_name] = values.get(var_name)

        resolved = self._resolve_values(model_key, request_values, user, db)
        self._persist_values(model_key, resolved, user, db)
        return self._predict(model_key, resolved)

    # ── Legacy per-model methods (kept for backward compatibility) ────
    #
    # These typed endpoints accept a Pydantic request schema specific to
    # each model.  They are wrappers around the same internal pipeline
    # (resolve → persist → predict) but provide stricter input validation
    # through their dedicated request schemas.

    def predict_econ_growth(
        self,
        request: EconGrowthPredictionRequest,
        user: User,
        db: Session,
    ) -> PredictionResponse:
        """Predict Δln PIB — Model 1: Economic Growth of Pereira.

        Args:
            request: Typed request with optional macro-economic feature values.
            user:    Authenticated user.
            db:      Active SQLAlchemy session.
        """
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
        """Predict Δln TD — Model 2: Unemployment rate in Pereira A.M.

        Args:
            request: Typed request with optional socio-economic feature values.
            user:    Authenticated user.
            db:      Active SQLAlchemy session.
        """
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
        """Predict Δln EMP — Model 3: Business fabric growth.

        Args:
            request: Typed request with optional economic feature values.
            user:    Authenticated user.
            db:      Active SQLAlchemy session.
        """
        request_values = request.model_dump()
        resolved = self._resolve_values("business_growth", request_values, user, db)
        self._persist_values("business_growth", resolved, user, db)
        return self._predict("business_growth", resolved)
