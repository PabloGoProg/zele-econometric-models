# Project Snapshot
- Python 3.12+ FastAPI service for econometric predictions.
- Package manager: Poetry 2.x; `poetry.toml` keeps the virtualenv in-project.
- Build system: Poetry / `poetry-core`.
- Runtime: Uvicorn + FastAPI + SQLAlchemy + SQLite.
- Main app entrypoint: `src/main.py`.
- Main source roots: `src/`, especially `src/api/`, `src/services/`, `src/models/`, `src/schemas/`, `src/core/`.
- Main data/artifact paths: `data/zele-econometric-models.db`, `src/models/artifacts/v1/`.
- Main test directory: `tests/`.
- Test framework: pytest.
- Main validation commands: `poetry install`, `poetry run pytest`, `uvicorn src.main:app --host 0.0.0.0 --port $PORT`.

# Required Workflow
1. Read this file first.
2. Read only the context files relevant to the task.
3. Inspect the related source before editing.
4. Make the smallest coherent change.
5. Update tests or add new ones when behavior changes and tests exist.
6. Update context files when ownership, flows, artifacts, or responsibilities change.
7. Run the most relevant validation command available in the repo.
8. Report what changed, what was validated, and whether context files changed.

# Context Routing
- Auth, sessions, passwords, JWT, login/logout, or `get_current_user`: read `context/AUTH.md` first.
- Model catalog, schemas, metadata, or `EconModel`/`Variable` relationships: read `context/MODELS.md` first.
- Predictions, inference, rate limiting, artifacts, or model loading: read `context/PREDICTIONS.md` first.
- App startup, SQLite, seeding, CORS, env settings, or deployment boot flow: read `context/RUNTIME.md` first.

# Validation
- Use `poetry run pytest` for the formal test suite.
- Use the smallest relevant check for the changed area when a full suite is unnecessary.
- For runtime smoke checks, use the documented Uvicorn startup command.

# File Change Policy
- Inspect the source of truth before editing; prefer code over README when they disagree.
- Keep edits minimal and localized.
- Do not change generated or runtime data files unless the task is explicitly about them: `src/models/artifacts/v1/*.pkl`, `data/zele-econometric-models.db`, `__pycache__/`.
- Update `context/*.md` when file ownership, runtime flow, or model responsibilities change.

# Documentation Policy
- Keep `AGENTS.md` short and operational.
- Put stable module detail in `context/*.md`, not here.
- Only document facts verified by repository files.

# Security Policy
- Never commit `.env`, tokens, or other secrets.
- Auth uses the `access_token` httpOnly cookie; production cookie settings differ from development.
- Treat the local SQLite DB and model artifacts as operational data.

# Final Response Requirements
- State the files changed.
- State the validation run, or say when none was run.
- State whether any context files changed.
- Call out anything that remains unverified or blocked.
