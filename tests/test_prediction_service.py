"""Prediction service tests with deterministic model doubles."""

import pandas as pd
from sqlalchemy.orm import Session

from src.models.entities import EconModel, User, UserModelVariable, Variable
from src.schemas.predictions import EconGrowthPredictionRequest
from src.services.prediction_service import PredictionService


class DummyStatsModel:
    rsquared = 0.98765
    params = pd.Series([1.0, 2.0, -1.0, 0.5, 0.25, 3.0])

    def predict(self, features_with_const):
        return features_with_const @ self.params.to_numpy()


def make_service() -> PredictionService:
    service = PredictionService.__new__(PredictionService)
    service._models = {"econ_growth": DummyStatsModel()}
    return service


def create_user(db_session: Session) -> User:
    user = User(name="Predictor", email="predictor@example.com", password="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_prediction_uses_request_values_and_persists_them(db_session: Session) -> None:
    service = make_service()
    user = create_user(db_session)
    request = EconGrowthPredictionRequest(
        delta_ln_EXP=0.10,
        delta_ln_IMP=0.03,
        delta_ln_REM=0.02,
        delta_ln_INV=0.01,
        delta_ln_EMP=0.04,
    )

    response = service.predict_econ_growth(request, user, db_session)

    assert response.prediction == 1.3025
    assert response.r_squared == 0.9877
    assert response.values_used["delta_ln_EXP"] == 0.10
    assert response.contributions == {
        "delta_ln_EXP": 0.2,
        "delta_ln_IMP": -0.03,
        "delta_ln_REM": 0.01,
        "delta_ln_INV": 0.0025,
        "delta_ln_EMP": 0.12,
    }

    model = db_session.query(EconModel).filter_by(name="econ_growth").one()
    variable = db_session.query(Variable).filter_by(name="delta_ln_EXP").one()
    persisted = (
        db_session.query(UserModelVariable)
        .filter_by(user_id=user.id, model_id=model.id, variable_id=variable.id)
        .one()
    )
    assert persisted.value == 0.10


def test_prediction_falls_back_to_saved_values_then_defaults(db_session: Session) -> None:
    service = make_service()
    user = create_user(db_session)
    model = db_session.query(EconModel).filter_by(name="econ_growth").one()
    variable = db_session.query(Variable).filter_by(name="delta_ln_EXP").one()
    db_session.add(
        UserModelVariable(
            user_id=user.id,
            model_id=model.id,
            variable_id=variable.id,
            value=0.22,
        )
    )
    db_session.commit()

    response = service.predict_econ_growth(EconGrowthPredictionRequest(), user, db_session)

    assert response.values_used["delta_ln_EXP"] == 0.22
    assert response.values_used["delta_ln_IMP"] == 0.03
    assert response.values_used["delta_ln_REM"] == 0.02
    assert response.values_used["delta_ln_INV"] == 0.01
    assert response.values_used["delta_ln_EMP"] == 0.04


def test_predict_by_model_id_rejects_unknown_model(db_session: Session) -> None:
    service = make_service()
    user = create_user(db_session)

    try:
        service.predict_by_model_id(999, {}, user, db_session)
    except Exception as exc:
        assert getattr(exc, "status_code") == 404
        assert getattr(exc, "detail") == "Modelo no encontrado"
    else:
        raise AssertionError("Expected 404 for unknown model")
