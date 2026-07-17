"""Testes dos caminhos críticos: health, listagem+contagem (cache),
liberação de acesso por pagamento e webhook do Mercado Pago."""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Licitacao, Usuario
from app.services.licitacao_service import contar_licitacoes


def _registrar_usuario(client, email="critico@example.com"):
    resp = client.post(
        "/auth/registrar",
        json={"nome": "Critico", "email": email, "senha": "senha-segura"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    usuario_id = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    ).json()["id"]
    return token, usuario_id


def _add_licitacoes(engine, itens):
    with Session(engine) as db:
        db.add_all(
            [
                Licitacao(
                    fonte="PNCP",
                    fonte_id=fid,
                    titulo=fid,
                    status=status,
                    dados_originais={},
                )
                for fid, status in itens
            ]
        )
        db.commit()


def test_health_responde_ok(db_app):
    from fastapi.testclient import TestClient
    from app.main import app

    resp = TestClient(app).get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_listagem_filtra_por_status_e_retorna_total(db_app):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.routes.pagamentos import _liberar_acesso

    _add_licitacoes(
        db_app,
        [("ab-1", "aberta"), ("ab-2", "aberta"), ("enc-1", "encerrada")],
    )
    client = TestClient(app)
    token, usuario_id = _registrar_usuario(client)

    # sem acesso liberado -> 402
    assert client.get(
        "/licitacoes", headers={"Authorization": f"Bearer {token}"}
    ).status_code == 402

    with Session(db_app) as db:
        _liberar_acesso(db, str(usuario_id), "mp_critico")

    resp = client.get(
        "/licitacoes?status=aberta",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["X-Total-Count"] == "2"
    assert {item["fonte_id"] for item in resp.json()} == {"ab-1", "ab-2"}


def test_cache_de_contagem_serve_valor_ate_expirar(db_app):
    """Prova que contar_licitacoes serve o valor cacheado e refaz após clear."""
    from app.services import licitacao_service

    _add_licitacoes(db_app, [("c-1", "aberta"), ("c-2", "aberta")])
    with Session(db_app) as db:
        total_inicial = contar_licitacoes(db, status="aberta")
        assert total_inicial == 2

        _add_licitacoes(db_app, [("c-3", "aberta")])
        # ainda dentro do TTL -> valor cacheado (2), não 3
        assert contar_licitacoes(db, status="aberta") == 2

        # após limpar o cache, reflete o estado real (3)
        licitacao_service._count_cache.clear()
        assert contar_licitacoes(db, status="aberta") == 3


def test_webhook_mercado_pago_libera_acesso(db_app, monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.routes import pagamentos

    client = TestClient(app)
    _, usuario_id = _registrar_usuario(client, email="pagante@example.com")

    monkeypatch.setattr(pagamentos.settings, "mp_access_token", "test-token")
    monkeypatch.setattr(pagamentos.settings, "mp_webhook_secret", None)

    class _FakePayment:
        def get(self, _pid):
            return {
                "status": 200,
                "response": {
                    "status": "approved",
                    "external_reference": str(usuario_id),
                },
            }

    class _FakeSDK:
        def __init__(self, _token):
            pass

        def payment(self):
            return _FakePayment()

    monkeypatch.setattr(pagamentos.mercadopago, "SDK", _FakeSDK)

    resp = client.post(
        "/pagamentos/webhook",
        json={"type": "payment", "data": {"id": "99999"}},
    )
    assert resp.status_code == 200

    with Session(db_app) as db:
        usuario = db.get(Usuario, usuario_id)
        assert usuario.acesso_liberado is True
        assert usuario.mp_payment_id == "99999"
