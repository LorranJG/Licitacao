import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import SyncState


def registrar_status_fonte(
    db: Session,
    chave: str,
    *,
    status: str,
    recebidas: int = 0,
    criadas: int = 0,
    atualizadas: int = 0,
    mensagem: str | None = None,
) -> None:
    valor = json.dumps(
        {
            "ultima_execucao_em": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "recebidas": recebidas,
            "criadas": criadas,
            "atualizadas": atualizadas,
            "mensagem": mensagem,
        }
    )
    estado = db.get(SyncState, chave)
    if estado is None:
        db.add(SyncState(chave=chave, valor=valor))
    else:
        estado.valor = valor
    db.commit()
