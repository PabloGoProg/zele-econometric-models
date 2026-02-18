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
    """Table of users in the system."""

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
    """Table of models available."""

    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(String(500), nullable=False)

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
    """Table of variables used by the models."""

    __tablename__ = "variables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=False)
    meaning = Column(String(500), nullable=False)
    default_value = Column(Float, nullable=False, default=0.0)

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
    """Table of relationship between models and their variables (defines which variables each model uses)."""

    __tablename__ = "model_variables"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    variable_id = Column(Integer, ForeignKey("variables.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("model_id", "variable_id", name="uq_model_variable"),
    )


class UserModelVariable(Base):
    """Table of triple relationship: specific variable values for a user and model."""

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
