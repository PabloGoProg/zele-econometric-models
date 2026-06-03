"""Database and ORM behavior tests."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.entities import EconModel, ModelVariable, User, UserModelVariable, Variable
from src.seed import MODELS_DATA, VARIABLES_DATA, seed_database


def test_seed_creates_models_variables_and_relationships(db_session: Session) -> None:
    models = db_session.query(EconModel).all()
    variables = db_session.query(Variable).all()

    assert len(models) == len(MODELS_DATA)
    assert len(variables) == len(VARIABLES_DATA)

    econ_growth = db_session.query(EconModel).filter_by(name="econ_growth").one()
    assert econ_growth.display_name
    assert len(econ_growth.description) > 250
    assert {variable.name for variable in econ_growth.variables} == set(
        MODELS_DATA[0]["variables"]
    )

    variable = db_session.query(Variable).filter_by(name="delta_ln_EXP").one()
    assert variable.display_name == "Crecimiento de exportaciones"
    assert variable.value_type == "log_change_rate"
    assert "porcentual aproximada" in variable.meaning


def test_seed_is_idempotent_and_updates_existing_metadata(db_session: Session) -> None:
    variable = db_session.query(Variable).filter_by(name="delta_ln_EXP").one()
    variable.display_name = "Valor antiguo"
    db_session.commit()

    seed_database(db_session)

    assert db_session.query(EconModel).count() == len(MODELS_DATA)
    assert db_session.query(Variable).count() == len(VARIABLES_DATA)
    assert db_session.query(ModelVariable).count() == sum(
        len(model["variables"]) for model in MODELS_DATA
    )
    assert variable.display_name == "Crecimiento de exportaciones"


def test_unique_user_email_constraint(db_session: Session) -> None:
    db_session.add(User(name="One", email="same@example.com", password="hash-1"))
    db_session.commit()

    db_session.add(User(name="Two", email="same@example.com", password="hash-2"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_model_variable_unique_triple(db_session: Session) -> None:
    user = User(name="One", email="one@example.com", password="hash")
    model = db_session.query(EconModel).filter_by(name="econ_growth").one()
    variable = db_session.query(Variable).filter_by(name="delta_ln_EXP").one()
    db_session.add(user)
    db_session.flush()

    db_session.add_all(
        [
            UserModelVariable(
                user_id=user.id,
                model_id=model.id,
                variable_id=variable.id,
                value=0.1,
            ),
            UserModelVariable(
                user_id=user.id,
                model_id=model.id,
                variable_id=variable.id,
                value=0.2,
            ),
        ]
    )

    with pytest.raises(IntegrityError):
        db_session.commit()
