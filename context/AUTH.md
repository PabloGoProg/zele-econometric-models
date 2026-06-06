# Auth
- Covers `src/api/routers/auth.py` and `src/services/auth_service.py`.
- Endpoints: register, login, logout, and `/me`.
- Passwords are hashed with bcrypt before persistence.
- Emails are normalized to lowercase on registration and looked up case-insensitively on login.
- JWTs are stored in the `access_token` httpOnly cookie.
- In production the cookie is `Secure` and `SameSite=None`; otherwise it is `Lax`.
- `get_current_user` reads the cookie, validates the JWT, loads the user from SQLite, and returns 401 on any invalid or missing credential.
- If you change the cookie name, JWT settings, or auth flow, update the router, service, and any callers together.
