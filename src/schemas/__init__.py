"""Schemas para los modelos econométricos."""

from src.schemas.predictions import (
    EconGrowthPredictionRequest,
    UnemploymentPredictionRequest,
    BusinessGrowthPredictionRequest,
    PredictionResponse,
)

__all__ = [
    "EconGrowthPredictionRequest",
    "UnemploymentPredictionRequest",
    "BusinessGrowthPredictionRequest",
    "PredictionResponse",
]
