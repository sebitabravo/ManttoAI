#!/usr/bin/env bash
set -euo pipefail
umask 0077

# Ruta absoluta basada en la ubicación del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
BACKUP_DIR="$REPO_ROOT/backups"
MAX_BACKUPS=4  # Mantener solo últimos 4 backups (1 mes semanal)
DB_NAME="manttoai_db"

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

# Generar nombre de archivo con timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_SQL="$BACKUP_DIR/manttoai_${TIMESTAMP}.sql"
OUTPUT_GZ="${OUTPUT_SQL}.gz"

# Ejecutar mysqldump y comprimir (con flags para consistencia InnoDB)
echo "Iniciando backup de $DB_NAME..."
docker compose exec -T mysql sh -c 'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysqldump --single-transaction --quick --routines --events --triggers -uroot '"$DB_NAME"'' | gzip -9 > "$OUTPUT_GZ"

# Establecer permisos restrictivos en el archivo de backup
chmod 600 "$OUTPUT_GZ"

# Verificar que el archivo no esté vacío
if [ -s "$OUTPUT_GZ" ]; then
    SIZE=$(du -h "$OUTPUT_GZ" | cut -f1)
    echo "Backup generado: $OUTPUT_GZ ($SIZE)"
else
    echo "ERROR: El backup está vacío"
    exit 1
fi

# Rotación segura usando array (compatible con bash 3.2+)
BACKUP_FILES=()
while IFS= read -r file; do
    BACKUP_FILES+=("$file")
done < <(ls -1t "$BACKUP_DIR"/manttoai_*.sql.gz 2>/dev/null || true)
COUNT=${#BACKUP_FILES[@]}

if [ "$COUNT" -gt "$MAX_BACKUPS" ]; then
    echo "Rotando backups (manteniendo últimos $MAX_BACKUPS)..."
    for ((i=MAX_BACKUPS; i<COUNT; i++)); do
        rm -f "${BACKUP_FILES[$i]}"
    done
fi

# Mostrar backups disponibles
echo ""
echo "Backups disponibles:"
ls -lh "$BACKUP_DIR"/manttoai_*.sql.gz 2>/dev/null || echo "  (ninguno)"

echo ""
echo "=== Respaldo completado ==="