# Predictions
- Covers `src/api/routers/predictions.py`, `src/services/prediction_service.py`, and `src/services/rate_limiter.py`.
- The prediction service loads `.pkl` artifacts from `src/models/artifacts/v1/` during startup.
- Missing artifacts prevent the app from starting.
- Prediction inputs are resolved in this order: request value, saved user value, variable default, then `0.0`.
- Resolved values are persisted to `user_model_variables` for reuse by the same user and model.
- Prediction endpoints require authenticated users and are rate-limited in memory per user.
- The rate limiter is process-local; it resets on restart and does not share state across workers.
- Each prediction response includes the prediction, R2, used values, and per-variable contributions.
