"""API prediction endpoint tests."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.entities import EconModel, UserModelVariable


def test_generic_prediction_endpoint_requires_authentication(client: TestClient) -> None:
    response = client.post("/api/v1/models/1/predict", json={"values": {}})

    assert response.status_code == 401


def test_generic_prediction_endpoint_returns_prediction(authenticated_client: TestClient) -> None:
    response = authenticated_client.post(
        "/api/v1/models/1/predict",
        json={
            "values": {
                "delta_ln_EXP": 0.05,
                "delta_ln_IMP": 0.03,
                "delta_ln_REM": 0.02,
                "delta_ln_INV": 0.01,
                "delta_ln_EMP": 0.04,
            }
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["model_name"] == "Determinantes del Crecimiento Económico de Pereira"
    assert body["variable"] == "delta_ln_PIB"
    assert set(body["values_used"]) == {
        "delta_ln_EXP",
        "delta_ln_IMP",
        "delta_ln_REM",
        "delta_ln_INV",
        "delta_ln_EMP",
    }
    assert set(body["contributions"]) == set(body["values_used"])


def test_prediction_persists_user_values(
    authenticated_client: TestClient, db_session: Session
) -> None:
    response = authenticated_client.post(
        "/api/v1/models/1/predict",
        json={"values": {"delta_ln_EXP": 0.12}},
    )

    assert response.status_code == 200
    model = db_session.query(EconModel).filter_by(name="econ_growth").one()
    persisted_values = (
        db_session.query(UserModelVariable)
        .filter(UserModelVariable.model_id == model.id)
        .all()
    )
    assert len(persisted_values) == 5
    assert any(value.value == 0.12 for value in persisted_values)


def test_legacy_prediction_endpoint_returns_prediction(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.post(
        "/api/v1/predictions/business-growth",
        json={"delta_ln_PIB": 0.07, "delta_ln_EXP": 0.05, "delta_ln_REM": 0.02},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["variable"] == "delta_ln_EMP"
    assert set(body["values_used"]) == {"delta_ln_PIB", "delta_ln_EXP", "delta_ln_REM"}
