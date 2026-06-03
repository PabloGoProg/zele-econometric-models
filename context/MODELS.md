# Models
- Covers the model catalog in `src/api/routers/models.py`, `src/models/entities.py`, and `src/seed.py`.
- The catalog is stored in SQLite as `EconModel`, `Variable`, and `ModelVariable` rows.
- Seed data defines three registered models: economic growth, unemployment, and business growth.
- Variables include UI metadata: `display_name`, `value_type`, long description, interpretation text, defaults, bounds, and step.
- `seed_database` upserts catalog metadata so existing development DBs receive updated model and variable descriptions.
- The schema endpoint returns DB metadata plus `r_squared` from the loaded prediction artifact, when one exists.
- `GET /api/v1/models/{model_id}/variables` returns only the enriched variable metadata for a model.
- The generic prediction endpoint only works for models that have a matching artifact mapping in `src/services/prediction_service.py`.
- If you add or rename a model, update seed data, the DB-to-artifact mapping, and the serialized artifact set together.
