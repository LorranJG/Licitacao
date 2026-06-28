#!/usr/bin/env sh
set -eu

PROJECT_DIR="${PROJECT_DIR:-/opt/licitacao}"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-radar_licitacoes}"

if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi

mkdir -p "$BACKUP_DIR"
cd "$PROJECT_DIR"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_FILE="$BACKUP_DIR/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

$COMPOSE --env-file .env.vps -f docker-compose.prod.yml exec -T postgres \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

find "$BACKUP_DIR" -type f -name "${POSTGRES_DB}_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

echo "Backup criado em $BACKUP_FILE"
