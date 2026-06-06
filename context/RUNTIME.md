# Runtime
- Covers `src/main.py`, `src/core/settings.py`, and `src/database.py`.
- App startup validates settings first.
- In `development`, startup always creates tables and seeds the SQLite database; in other environments it does this bootstrap only when the configured SQLite file does not exist.
- Startup creates the configured SQLite parent directory before bootstrapping a missing database.
- The development seed path also adds missing SQLite variable metadata columns before upserting catalog data.
- SQLite path, JWT settings, CORS origins, and port come from `Settings` and `.env`.
- `poetry.toml` keeps the Poetry virtualenv inside the repository as `.venv/`.
- The app exposes `/health` and mounts all API routers under `/api/v1`.
- If startup behavior changes, revisit the deployment note about required artifacts before assuming a boot failure is unrelated.
