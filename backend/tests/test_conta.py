from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Licitacao
from app.routes.pagamentos import _liberar_acesso


def test_fluxo_de_conta_favorito_e_validacao_de_lembrete(monkeypatch) -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine)

    def override_db():
        with test_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with Session(engine) as db:
            licitacao = Licitacao(
                fonte="PNCP",
                fonte_id="conta-teste",
                titulo="Licitação para testar favoritos",
                status="aberta",
                dados_originais={},
            )
            db.add(licitacao)
            db.commit()
            licitacao_id = licitacao.id

        client = TestClient(app)
        tokens: dict[str, str] = {}
        monkeypatch.setattr(
            "app.routes.auth.enviar_verificacao",
            lambda usuario, token: tokens.update(verificacao=token) or False,
        )
        monkeypatch.setattr(
            "app.routes.auth.enviar_redefinicao",
            lambda usuario, token: tokens.update(redefinicao=token) or False,
        )
        registro = client.post(
            "/auth/registrar",
            json={
                "nome": "Empresa Teste",
                "email": "teste@example.com",
                "senha": "senha-segura",
            },
        )
        assert registro.status_code == 201
        token = registro.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        confirmar = client.post(
            "/auth/confirmar-email",
            json={"token": tokens["verificacao"]},
        )
        assert confirmar.status_code == 200
        me = client.get("/auth/me", headers=headers).json()
        assert me["email_verificado"] is True
        assert me["acesso_liberado"] is False

        bloqueado = client.post(f"/favoritos/{licitacao_id}", headers=headers)
        assert bloqueado.status_code == 402

        with Session(engine) as db:
            _liberar_acesso(
                db,
                {
                    "id": "cs_test_conta",
                    "customer": "cus_test_conta",
                    "payment_status": "paid",
                    "metadata": {"usuario_id": str(me["id"])},
                },
            )
        assert client.get("/auth/me", headers=headers).json()["acesso_liberado"] is True

        favorito = client.post(f"/favoritos/{licitacao_id}", headers=headers)
        assert favorito.status_code == 201
        assert favorito.json()["licitacao"]["id"] == licitacao_id

        status = client.get(
            f"/favoritos/{licitacao_id}/status", headers=headers
        )
        assert status.json() == {"favorito": True}

        perfil = client.put(
            "/auth/me",
            headers=headers,
            json={
                "nome": "Empresa Atualizada",
                "telefone": "(11) 99999-0000",
                "razao_social": "Empresa Teste Ltda.",
                "nome_fantasia": "Empresa Teste",
                "cnpj": "00.000.000/0001-00",
                "segmentos": ["software"],
                "ufs_interesse": ["SP", "MG"],
                "municipios_interesse": ["São Paulo"],
                "valor_minimo_interesse": 10000,
                "valor_maximo_interesse": 500000,
                "palavras_chave": ["software", "nuvem"],
                "palavras_ignoradas": ["obra"],
                "modalidades_interesse": ["pregão eletrônico"],
                "orgaos_interesse": ["prefeituras"],
                "prazo_minimo_dias": 3,
                "alertar_novas_oportunidades": True,
                "alertas_antecedencia_horas": [72, 24],
                "frequencia_resumo": "diario",
                "horario_inicio_alertas": "08:00",
                "horario_fim_alertas": "20:00",
            },
        )
        assert perfil.status_code == 200
        assert perfil.json()["nome"] == "Empresa Atualizada"
        assert perfil.json()["palavras_chave"] == ["software", "nuvem"]

        senha = client.post(
            "/auth/alterar-senha",
            headers=headers,
            json={
                "senha_atual": "senha-segura",
                "nova_senha": "nova-senha-segura",
            },
        )
        assert senha.status_code == 200
        novo_login = client.post(
            "/auth/login",
            json={
                "email": "teste@example.com",
                "senha": "nova-senha-segura",
            },
        )
        assert novo_login.status_code == 200

        monkeypatch.setattr(
            "app.routes.auth.validar_google_id_token",
            lambda token, nonce: {
                "sub": "google-usuario-teste",
                "email": "teste@example.com",
                "email_verified": True,
                "name": "Empresa Google",
                "nonce": nonce,
            },
        )
        google_login = client.post(
            "/auth/google",
            json={"id_token": "token-google-de-teste-valido", "nonce": "nonce-teste"},
        )
        assert google_login.status_code == 200
        assert google_login.json()["usuario"]["google_conectado"] is True

        busca = client.post(
            "/buscas-salvas",
            headers=headers,
            json={
                "nome": "Software em SP",
                "filtros": {
                    "palavra_chave": "Licitação",
                    "uf": "SP",
                    "status": "aberta",
                },
                "alertas_ativos": True,
            },
        )
        assert busca.status_code == 201
        assert busca.json()["nome"] == "Software em SP"
        assert len(client.get("/buscas-salvas", headers=headers).json()) == 1

        solicitar = client.post(
            "/auth/solicitar-redefinicao",
            json={"email": "teste@example.com"},
        )
        assert solicitar.status_code == 200
        redefinir = client.post(
            "/auth/redefinir-senha",
            json={
                "token": tokens["redefinicao"],
                "nova_senha": "senha-final-segura",
            },
        )
        assert redefinir.status_code == 200
        assert client.post(
            "/auth/login",
            json={"email": "teste@example.com", "senha": "senha-final-segura"},
        ).status_code == 200

        lembrete = client.post(
            "/lembretes",
            headers=headers,
            json={
                "licitacao_id": licitacao_id,
                "lembrar_em": (
                    datetime.now(timezone.utc) + timedelta(hours=1)
                ).isoformat(),
            },
        )
        assert lembrete.status_code == 409
        assert "Telegram" in lembrete.json()["detail"]
    finally:
        app.dependency_overrides.clear()
