"""Rate limiter in-memory simple para predicciones."""

import math
import time
from collections import defaultdict

from fastapi import Depends, HTTPException, Response, status

from src.models.entities import User
from src.services.auth_service import get_current_user

MAX_REQUESTS = 20
WINDOW_SECONDS = 5 * 60

_user_timestamps: dict[int, list[float]] = defaultdict(list)


def _cleanup(user_id: int) -> list[float]:
    """Elimina timestamps fuera de la ventana activa."""
    cutoff = time.time() - WINDOW_SECONDS
    _user_timestamps[user_id] = [
        ts for ts in _user_timestamps[user_id] if ts > cutoff
    ]
    return _user_timestamps[user_id]


def check_rate_limit(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependencia que verifica el rate limit antes de permitir la predicción."""
    active = _cleanup(current_user.id)

    remaining = MAX_REQUESTS - len(active)
    response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))

    if remaining <= 0:
        oldest = min(active)
        retry_after = math.ceil(oldest + WINDOW_SECONDS - time.time())
        response.headers["Retry-After"] = str(max(retry_after, 1))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Has alcanzado el límite de predicciones. Intenta de nuevo más tarde.",
            headers={"Retry-After": str(max(retry_after, 1))},
        )

    _user_timestamps[current_user.id].append(time.time())
    return current_user
