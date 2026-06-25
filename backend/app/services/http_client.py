import ssl
from functools import lru_cache

import httpx

from app.config import get_settings


@lru_cache
def ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    settings = get_settings()
    if settings.relax_x509_strict and hasattr(ssl, "VERIFY_X509_STRICT"):
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return context


def async_client(**kwargs) -> httpx.AsyncClient:
    return httpx.AsyncClient(verify=ssl_context(), **kwargs)


def client(**kwargs) -> httpx.Client:
    return httpx.Client(verify=ssl_context(), **kwargs)
