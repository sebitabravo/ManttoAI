#!/usr/bin/env bash
set -euo pipefail

mkdir -p backups
OUTPUT="backups/manttoai_$(date +%Y%m%d_%H%M%S).sql"

docker compose exec -T mysql sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" manttoai_db' > "$OUTPUT"

printf 'Backup generado en %s\n' "$OUTPUT"
