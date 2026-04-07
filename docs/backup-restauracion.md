# Backup y Restauración de Base de Datos

Este documento describe el procedimiento de respaldo y restauración de la base de datos MySQL de ManttoAI.

## Respaldo Automático

### Script de Backup

El proyecto incluye un script automatizado en `scripts/backup_db.sh`:

```bash
# Ejecutar manualmente
bash scripts/backup_db.sh

# Verificar backups disponibles
ls -lh backups/
```

El script:
1. Genera un archivo `.sql.gz` con compression
2. Mantiene solo los ultimos 4 backups (rotacion automatica)
3. Verifica que el backup no este vacio

### Programacion Semanal (VPS)

En el VPS, configurar un cron semanal para ejecutacion automatica:

```bash
# Editar crontab
crontab -e

# Agregar esta linea para ejecutar ogni domingo a las 3:00 AM
0 3 * * 0 cd /home/manttoai/ManttoAI && bash scripts/backup_db.sh >> /var/log/manttoai_backup.log 2>&1
```

Verificar que el log rote mensualmente para evitar acumulacion.

---

## Restauracion Paso a Paso

### Paso 1: Identificar el Backup

```bash
# Ver backups disponibles
ls -lh backups/

# Ejemplo de archivo: manttoai_20260407_030000.sql.gz
```

### Paso 2: Detener Servicios (Recomendado)

```bash
# Detener servicios que escriban a la BD
docker compose stop backend mqtt
```

### Paso 3: Restaurar la Base de Datos

**Opcion A: Restaurar desde archivo .sql.gz (recomendado)**

```bash
# Descomprimir y restaurar en un paso
gunzip -c backups/manttoai_YYYYMMDD_HHMMSS.sql.gz | docker compose exec -T mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" manttoai_db'
```

**Opcion B: Restaurar desde archivo .sql (sin comprimir)**

```bash
# Primero descomprimir
gunzip backups/manttoai_YYYYMMDD_HHMMSS.sql.gz

# Luego restaurar
docker compose exec -T mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" manttoai_db' < backups/manttoai_YYYYMMDD_HHMMSS.sql
```

**Nota:** Reemplazar `YYYYMMDD_HHMMSS` con el timestamp real del archivo.

### Paso 4: Verificar Restauracion

```bash
# Iniciar servicios
docker compose up -d backend

# Verificar que la API responde
curl -s http://localhost:8000/health | jq

# Verificar datos en la base
docker compose exec mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "USE manttoai_db; SELECT COUNT(*) FROM equipos;"
```

### Paso 5: Reinciar Servicios

```bash
# Iniciar todos los servicios
docker compose up -d

# Verificar estado
docker compose ps
```

---

## Verificacion del Backup

Para verificar que un backup es usable sin restaurar:

```bash
# Ver contenido sin descomprimir todo
gunzip -l backups/manttoai_YYYYMMDD_HHMMSS.sql.gz

# Extraer solo la estructura (sin datos) para verificar
gunzip -c backups/manttoai_YYYYMMDD_HHMMSS.sql.gz | head -50
```

El backup valido debe contener:
- `CREATE DATABASE` o `USE manttoai_db`
- `CREATE TABLE` para todas las entidades
- `INSERT INTO` con datos

---

## Consideraciones de Seguridad

1. **Almacenamiento**: Los backups se guardan en el servidor. Para produccion real, considerar almacenamiento offsite o encriptado.
2. **Credenciales**: El script usa la variable `MYSQL_ROOT_PASSWORD` del archivo `.env`. No incluir credenciales en el repo.
3. **Permisos**: El directorio `backups/` debe tener permisos `chmod 700` para proteger los datos.

---

## Comandos Utiles

```bash
# Ver tamano total de backups
du -sh backups/

# Ver ultimos 7 dias de backups
find backups/ -name "*.sql.gz" -mtime -7 -ls

# Restaurar a un punto especifico (requiere backup de ese momento)
gunzip -c backups/manttoai_20260401_030000.sql.gz | docker compose exec -T mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" manttoai_db'
```

---

## Frecuencia Recomendada

| Tipo | Frecuencia | Retencion |
|------|-------------|-----------|
| Automatico | Semanal | 4 semanas |
| Manual | Antes de actualizaciones mayores | Infinite |

Para el MVP de este proyecto, el backup semanal es suficiente.