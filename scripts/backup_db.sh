#!/usr/bin/env bash
set -euo pipefail

# Configuración
BACKUP_DIR="backups"
MAX_BACKUPS=4  # Mantener solo últimos 4 backups (1 mes semanal)
DB_NAME="manttoai_db"

mkdir -p "$BACKUP_DIR"

# Generar nombre de archivo con timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_SQL="$BACKUP_DIR/manttoai_${TIMESTAMP}.sql"
OUTPUT_GZ="${OUTPUT_SQL}.gz"

# Ejecutar mysqldump y comprimir
echo "Iniciando backup de $DB_NAME..."
docker compose exec -T mysql sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" manttoai_db' | gzip -9 > "$OUTPUT_GZ"

# Verificar que el archivo no esté vacío
if [ -s "$OUTPUT_GZ" ]; then
    SIZE=$(du -h "$OUTPUT_GZ" | cut -f1)
    echo "Backup generado: $OUTPUT_GZ ($SIZE)"
else
    echo "ERROR: El backup está vacío"
    exit 1
fi

# Rotación: eliminar backups antiguos dejando solo MAX_BACKUPS
BACKUPS=$(ls -1t "$BACKUP_DIR"/manttoai_*.sql.gz 2>/dev/null || true)
COUNT=$(echo "$BACKUPS" | wc -l)

if [ "$COUNT" -gt "$MAX_BACKUPS" ]; then
    echo "Rotando backups (manteniendo últimos $MAX_BACKUPS)..."
    echo "$BACKUPS" | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f
fi

# Mostrar backups disponibles
echo ""
echo "Backups disponibles:"
ls -lh "$BACKUP_DIR"/manttoai_*.sql.gz 2>/dev/null || echo "  (ninguno)"

echo ""
echo "=== Respaldo completado ==="
