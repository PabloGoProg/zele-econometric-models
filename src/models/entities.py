"""SQLAlchemy models for the database."""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    """
    Table of users in the system.

    Attributes:
        id: Unique identifier for the user.
        name: Name of the user.
        email: Email address of the user.
        password: Hashed password of the user.
        created_at: Timestamp of when the user was created.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user_model_variables = relationship(
        "UserModelVariable", back_populates="user", cascade="all, delete-orphan"
    )


class EconModel(Base):
    """
    Table of models available.

    Attributes:
        id: Unique identifier for the model.
        name: Name of the model.
        display_name: Display name of the model.
        description: Description of the model.
        version: Version of the model.
        trained_at: Timestamp of when the model was trained.
        target_variable: Name of the target variable of the model.
        user_model_variables: Relationship to the UserModelVariable table.
        variables: Relationship to the Variable table.
    """

    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    display_name = Column(String(300), nullable=False)
    description = Column(String(500), nullable=False)
    version = Column(String(20), nullable=False, default="1.0.0")
    trained_at = Column(String(20), nullable=False, default="2025-06-15")
    target_variable = Column(String(100), nullable=False, default="")

    user_model_variables = relationship(
        "UserModelVariable", back_populates="model", cascade="all, delete-orphan"
    )
    variables = relationship(
        "Variable",
        secondary="model_variables",
        back_populates="models",
        viewonly=True,
    )


class Variable(Base):
    """Table of variables used by the models.

    Attributes:
        id: Unique identifier for the variable.
        name: Name of the variable.
        description: Description of the variable.
        meaning: Meaning of the variable.
        default_value: Default value of the variable.
        min_value: Minimum value of the variable.
        max_value: Maximum value of the variable.
        step: Step size of the variable.
        user_model_variables: Relationship to the UserModelVariable table.
        models: Relationship to the EconModel table.
    """

    __tablename__ = "variables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=False)
    meaning = Column(String(500), nullable=False)
    default_value = Column(Float, nullable=False, default=0.0)
    min_value = Column(Float, nullable=False, default=-1.0)
    max_value = Column(Float, nullable=False, default=1.0)
    step = Column(Float, nullable=False, default=0.01)

    user_model_variables = relationship(
        "UserModelVariable", back_populates="variable", cascade="all, delete-orphan"
    )
    models = relationship(
        "EconModel",
        secondary="model_variables",
        back_populates="variables",
        viewonly=True,
    )


class ModelVariable(Base):
    """Table of relationship between models and their variables (defines which variables each model uses).

    Attributes:
        id: Unique identifier for the relationship.
        model_id: Foreign key to the EconModel table.
        variable_id: Foreign key to the Variable table.
    """

    __tablename__ = "model_variables"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    variable_id = Column(Integer, ForeignKey("variables.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("model_id", "variable_id", name="uq_model_variable"),
    )


class UserModelVariable(Base):
    """Table of triple relationship: specific variable values for a user and model.

    Attributes:
        id: Unique identifier for the relationship.
        user_id: Foreign key to the User table.
        model_id: Foreign key to the EconModel table.
        variable_id: Foreign key to the Variable table.
        value: Value of the variable for the user and model.
        updated_at: Timestamp of when the value was last updated.
        user: Relationship to the User table.
        model: Relationship to the EconModel table.
        variable: Relationship to the Variable table.
    """

    __tablename__ = "user_model_variables"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    variable_id = Column(Integer, ForeignKey("variables.id"), nullable=False)
    value = Column(Float, nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="user_model_variables")
    model = relationship("EconModel", back_populates="user_model_variables")
    variable = relationship("Variable", back_populates="user_model_variables")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "model_id", "variable_id", name="uq_user_model_variable"
        ),
    )
