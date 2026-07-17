#!/usr/bin/env bash
# Auto-check de saúde do Radar Licitações. Verifica containers, disco, /health
# e a coleta (sync_states) e avisa por Telegram quando algo muda. Anti-spam:
# só reenvia quando o conjunto de problemas muda, e avisa ao normalizar.
#
# Requer no .env.vps: TELEGRAM_BOT_TOKEN e MONITOR_TELEGRAM_CHAT_ID.
# Agende no cron, ex.: */15 * * * * /opt/licitacao/deploy/scripts/monitorar.sh
set -u

PROJECT_DIR="${PROJECT_DIR:-/opt/licitacao}"
ENV_FILE="$PROJECT_DIR/.env.vps"
STATE_FILE="${STATE_FILE:-/var/lib/radar-monitor.state}"
DISK_THRESHOLD="${DISK_THRESHOLD:-85}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health}"
SYNC_MAX_AGE_MIN="${SYNC_MAX_AGE_MIN:-90}"
PG_CONTAINER="${PG_CONTAINER:-licitacao-postgres-1}"

EXPECTED="licitacao-postgres-1 licitacao-backend-1 licitacao-pncp-worker-1 \
licitacao-pncp-open-worker-1 licitacao-pncp-backfill-worker-1 \
licitacao-compras-gov-worker-1 licitacao-compras-gov-backfill-worker-1"

TOKEN="$(grep -E '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE" 2>/dev/null | cut -d= -f2-)"
CHAT="$(grep -E '^MONITOR_TELEGRAM_CHAT_ID=' "$ENV_FILE" 2>/dev/null | cut -d= -f2-)"

problems=""

# 1) containers no ar
for c in $EXPECTED; do
    st="$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null)"
    [ "$st" = "running" ] || problems="$problems"$'\n'"- container $c: ${st:-ausente}"
done

# 2) disco
disk="$(df / | awk 'NR==2{gsub("%","",$5); print $5}')"
if [ "${disk:-0}" -ge "$DISK_THRESHOLD" ]; then
    problems="$problems"$'\n'"- disco em ${disk}% (limite ${DISK_THRESHOLD}%)"
fi

# 3) health
code="$(curl -s -m 8 -o /dev/null -w '%{http_code}' "$HEALTH_URL" 2>/dev/null)"
[ "$code" = "200" ] || problems="$problems"$'\n'"- /health retornou ${code:-sem resposta}"

# 4) coleta (sync_states)
check_sync() {
    key="$1"; label="$2"
    row="$(docker exec "$PG_CONTAINER" psql -U postgres -d radar_licitacoes -tAc \
        "SELECT valor FROM sync_states WHERE chave='$key'" 2>/dev/null)"
    [ -n "$row" ] || return
    st="$(printf '%s' "$row" | grep -oE '"status" *: *"[^"]*"' | head -1 | sed -E 's/.*"([^"]*)"$/\1/')"
    [ "$st" = "erro" ] && problems="$problems"$'\n'"- coleta $label em ERRO"
    ts="$(printf '%s' "$row" | grep -oE '"ultima_execucao_em" *: *"[^"]*"' | head -1 | sed -E 's/.*"([^"]*)"$/\1/')"
    if [ -n "$ts" ]; then
        ts_clean="$(printf '%s' "$ts" | sed -E 's/\.[0-9]+//')"
        epoch="$(date -u -d "$ts_clean" +%s 2>/dev/null || echo 0)"
        [ "$epoch" -gt 0 ] || return
        age=$(( ( $(date -u +%s) - epoch ) / 60 ))
        [ "$age" -gt "$SYNC_MAX_AGE_MIN" ] && \
            problems="$problems"$'\n'"- coleta $label parada ha ${age}min"
    fi
}
check_sync status_pncp "PNCP"
check_sync status_comprasgov "Compras.gov"

send_telegram() {
    [ -n "$TOKEN" ] && [ -n "$CHAT" ] || return
    curl -s -m 10 "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        --data-urlencode "chat_id=${CHAT}" \
        --data-urlencode "text=$1" >/dev/null 2>&1
}

prev="$(cat "$STATE_FILE" 2>/dev/null || true)"
if [ -n "$problems" ]; then
    if [ "$problems" != "$prev" ]; then
        send_telegram "🚨 Radar Licitações — problemas detectados:${problems}"
        printf '%s' "$problems" > "$STATE_FILE"
    fi
    printf '%s\n' "PROBLEMAS:${problems}"
else
    if [ -n "$prev" ]; then
        send_telegram "✅ Radar Licitações — tudo normalizado."
        : > "$STATE_FILE"
    fi
    echo "OK - sem problemas"
fi
