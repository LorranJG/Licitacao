from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import auth, conta, health, licitacoes, mvp, pagamentos, telegram

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para consulta e coleta de licitações públicas.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

app.include_router(health.router)
app.include_router(licitacoes.router)
app.include_router(auth.router)
app.include_router(pagamentos.router)
app.include_router(conta.router)
app.include_router(telegram.router)
app.include_router(mvp.router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "message": "Radar Licitações API",
        "docs": "/docs",
        "health": "/health",
    }
