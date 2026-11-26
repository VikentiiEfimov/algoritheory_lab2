#!/bin/sh
set -e

SEED_DB="/app/seed/tournament.db"
DATA_DB="${DATA_DIR:-/app/data}/tournament.db"

if [ -f "$SEED_DB" ] && [ ! -f "$DATA_DB" ]; then
    echo "[entrypoint] Инициализирую БД из seed: $DATA_DB"
    mkdir -p "$(dirname "$DATA_DB")"
    cp "$SEED_DB" "$DATA_DB"
fi

exec "$@"