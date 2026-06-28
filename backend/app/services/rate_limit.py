from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status

_attempts: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def _client_ip(request: Request) -> str:
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return "unknown"


def rate_limit(
    scope: str,
    *,
    max_requests: int,
    window_seconds: int,
) -> Callable[[Request], None]:
    def dependency(request: Request) -> None:
        now = monotonic()
        cutoff = now - window_seconds
        key = f"{scope}:{_client_ip(request)}"

        with _lock:
            bucket = _attempts[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Muitas tentativas. Aguarde alguns minutos e tente novamente.",
                )
            bucket.append(now)

    return dependency
