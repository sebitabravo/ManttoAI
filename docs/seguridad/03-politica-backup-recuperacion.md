# Politica de Backup y Recuperacion

- **Version:** 1.0
- **Fecha:** 2026-06-09
- **Clasificacion:** Uso interno / Confidencial
- **Aprobado por:** Director de Proyecto — ManttoAI
- **Proxima revision:** 2026-09-09 (trimestral)

---

## 1. Proposito

Establecer los procedimientos para la realizacion de backups y la recuperacion de datos de la plataforma ManttoAI, garantizando la disponibilidad e integridad de la informacion ante fallos tecnicos, errores humanos, incidentes de seguridad o desastres naturales.

## 2. Objetivos de Recuperacion

| Metric | Objetivo | Definicion |
|---|---|---|
| **RPO (Recovery Point Objective)** | 24 horas | Cantidad maxima de datos que se puede perder (ultimas 24h de telemetria) |
| **RTO (Recovery Time Objective)** | 4 horas | Tiempo maximo para restaurar el servicio completo desde la declaracion del desastre |
| **RTO parcial (datos solamente)** | 1 hora | Tiempo maximo para restaurar la base de datos |

### 2.1 Justificacion de RPO

El RPO de 24 horas se define considerando:

- La telemetria IoT se genera continuamente, pero el analisis de tendencias no requiere datos minuto a minuto
- El modelo ML se entrena con ventanas de tiempo (horas/dias), no con datos en tiempo real
- Una perdida de hasta 24 horas de telemetria no afecta la capacidad de generar predicciones ni alertas historicas

### 2.2 Justificacion de RTO

El RTO de 4 horas se define considerando:

- Infraestructura: VPS simple sin clustering, el restore requiere aprovisionar un nuevo VPS
- Tiempo real de restore probado: ~60 minutos para la base de datos + 30 minutos para contenedores
- El margen adicional cubre imprevistos: latencia de DNS, provisionamiento del VPS secundario

## 3. Alcance

Esta politica aplica a todos los datos e infraestructura de ManttoAI:

| Componente | Backup requerido? | Prioridad |
|---|---|---|
| Base de datos MySQL (telemetria, equipos, usuarios, alertas, mantenimientos) | Si | Critica |
| Archivos de configuracion (Docker Compose, .env, Nginx, Mosquitto) | Si | Alta |
| Codigo fuente (Git — respaldado por GitHub) | Si (repositorio remoto) | Alta |
| Modelo ML entrenado (joblib) | Si | Media |
| Logs de aplicacion | No (recreables) | Baja |
| Dashboard estatico (build de React) | No (recreable desde codigo) | Baja |

## 4. Procedimiento de Backup Diario

### 4.1 Backup de base de datos MySQL

```bash
#!/bin/bash
# backup-manttoai.sh — Programado via cron a las 03:00 AM Chile

BACKUP_DIR="/var/backups/manttoai"
DB_NAME="manttoai"
DB_USER="root"
DB_PASS=$(cat /run/secrets/db_root_password)
DATE=$(date +%Y-%m-%d)
FILENAME="manttoai_db_${DATE}.sql.gz"
ENCRYPTED_FILENAME="${FILENAME}.gpg"

mkdir -p "${BACKUP_DIR}/daily"
mkdir -p "${BACKUP_DIR}/monthly"

# 1. Dump de la base de datos con compresion
mysqldump --user="${DB_USER}" --password="${DB_PASS}" \
    --single-transaction --routines --triggers --events \
    "${DB_NAME}" | gzip > "${BACKUP_DIR}/daily/${FILENAME}"

# 2. Cifrado del backup (GPG con clave simetrica)
gpg --batch --yes --passphrase-file /run/secrets/backup_key \
    --symmetric --cipher-algo AES256 \
    "${BACKUP_DIR}/daily/${FILENAME}"

# 3. Eliminar archivo sin cifrar
rm "${BACKUP_DIR}/daily/${FILENAME}"

# 4. Verificar integridad del archivo cifrado
gpg --batch --yes --passphrase-file /run/secrets/backup_key \
    --decrypt "${BACKUP_DIR}/daily/${ENCRYPTED_FILENAME}" \
    | gzip -t || echo "ERROR: Backup corrupto"

# 5. Copia a almacenamiento externo (SCP a VPS secundario o bucket S3 compatible)
scp "${BACKUP_DIR}/daily/${ENCRYPTED_FILENAME}" \
    backup@storage-vps:/backups/manttoai/daily/

echo "Backup completado: ${ENCRYPTED_FILENAME}"
```

### 4.2 Backup de configuracion

```bash
#!/bin/bash
# backup-config.sh

BACKUP_DIR="/var/backups/manttoai/config"
DATE=$(date +%Y-%m-%d)

tar -czf "${BACKUP_DIR}/config_${DATE}.tar.gz" \
    /opt/manttoai/docker-compose.yml \
    /opt/manttoai/.env \
    /etc/nginx/sites-available/manttoai \
    /etc/mosquitto/mosquitto.conf \
    /etc/mosquitto/conf.d/

# Cifrar
gpg --batch --yes --passphrase-file /run/secrets/backup_key \
    --symmetric --cipher-algo AES256 \
    "${BACKUP_DIR}/config_${DATE}.tar.gz"

rm "${BACKUP_DIR}/config_${DATE}.tar.gz"
```

### 4.3 Backup del modelo ML

```bash
#!/bin/bash
# backup-model.sh

cp /opt/manttoai/models/modelo_rf.joblib \
    "/var/backups/manttoai/model/modelo_rf_$(date +%Y-%m-%d).joblib"
```

### 4.4 Programacion

| Backup | Frecuencia | Hora | Responsable |
|---|---|---|---|
| BD MySQL | Diaria | 03:00 AM Chile | Cron + script |
| Configuracion | Diaria | 03:30 AM Chile | Cron + script |
| Modelo ML | Post-entrenamiento | N/A | Manual |
| Copia externa | Diaria (post-cifrado) | 04:00 AM Chile | Cron + script |

## 5. Retencion de Backups

| Tipo | Retencion | Destino |
|---|---|---|
| Backups diarios | 30 dias | VPS local + almacenamiento externo |
| Backups mensuales | 12 meses | Almacenamiento externo |
| Backups anuales | 3 anos | Almacenamiento externo (archivo) |

### 5.1 Rotacion mensual

El primer dia de cada mes, el backup diario mas reciente se copia a la carpeta `monthly/`:

```bash
cp "${BACKUP_DIR}/daily/$(ls -t ${BACKUP_DIR}/daily/ | head -1)" \
    "${BACKUP_DIR}/monthly/manttoai_db_$(date +%Y-%m).sql.gz.gpg"
```

### 5.2 Limpieza automatica

```bash
# Eliminar backups diarios mayores a 30 dias
find "${BACKUP_DIR}/daily/" -name "*.gpg" -mtime +30 -delete

# Eliminar backups mensuales mayores a 12 meses
find "${BACKUP_DIR}/monthly/" -name "*.gpg" -mtime +365 -delete
```

## 6. Almacenamiento de Backups

### 6.1 Local (VPS principal)

- Directorio: `/var/backups/manttoai/`
- Backup diario retenido por 30 dias
- Disco: minimo 10 GB reservados para backups
- Particion separada para evitar llenar el disco del sistema

### 6.2 Externo (VPS secundario o S3)

- Replica cifrada de cada backup diario
- Transferencia via SCP o rsync sobre SSH
- Retencion: 30 dias diarios + 12 meses mensuales
- Almacenamiento en Digital Ocean Spaces, Backblaze B2, o VPS secundario

### 6.3 Off-site

Se considera almacenamiento off-site al VPS secundario en una region distinta (ejemplo: VPS en Santiago + backup en Sao Paulo).

## 7. Prueba de Restore Trimestral

### 7.1 Procedimiento

Cada trimestre (enero, abril, julio, octubre) se debe realizar una prueba completa de restore:

```
1. PREPARACION
   - Notificar al equipo con 48 horas de anticipacion
   - Preparar entorno de prueba (VPS staging o contenedor local)
   - Obtener el backup cifrado mas reciente

2. RESTORE DE BASE DE DATOS
   - Descifrar backup: gpg --decrypt backup.gpg | gunzip > restore.sql
   - Crear base de datos temporal en el entorno de prueba
   - Importar: mysql -u root manttoai_test < restore.sql
   - Verificar integridad: contar registros, validar tablas, checksums

3. RESTORE DE CONFIGURACION
   - Descomprimir config backup
   - Verificar que los archivos de configuracion sean validos
   - Comparar checksums con la configuracion actual

4. VALIDACION FUNCIONAL
   - Iniciar los servicios en el entorno de prueba
   - Verificar que la API responde correctamente
   - Verificar que el dashboard carga sin errores
   - Verificar que los datos historicos sean accesibles
   - Verificar que las alertas se muestran correctamente

5. DOCUMENTACION
   - Registrar tiempo total del restore
   - Documentar cualquier incidencia
   - Firmar el formulario de prueba de restore
```

### 7.2 Formulario de prueba de restore

```
PRUEBA DE RESTORE — MANTTOAI
==============================

Fecha de prueba: [DD/MM/AAAA]
Responsable: [Nombre]
Backup utilizado: [nombre del archivo]
Fecha del backup: [DD/MM/AAAA]

TIEMPOS:
- Inicio de prueba: [HH:MM]
- Restore BD completado: [HH:MM] ([X] min)
- Restore config completado: [HH:MM] ([X] min)
- Validacion funcional completada: [HH:MM] ([X] min)
- Tiempo total: [HH:MM] ([X] min)

RESULTADOS:
- Integridad de BD: [OK / ERROR]
- Integridad de config: [OK / ERROR]
- API funcional: [OK / ERROR]
- Dashboard funcional: [OK / ERROR]
- Datos historicos accesibles: [OK / ERROR]

INCIDENCIAS:
- [Descripcion de cualquier problema encontrado]

ACCIONES CORRECTIVAS:
- [Pasos tomados para corregir incidencias]

Visto bueno: [Firma Director]
```

### 7.3 Criterios de aprobacion

La prueba se considera exitosa si:

- La base de datos se restaura completamente sin errores
- Todos los servicios se inician correctamente
- La API responde a consultas de lectura y escritura
- El dashboard carga los datos historicos correctamente
- El tiempo total es menor al RTO (4 horas)

## 8. Procedimiento de Recuperacion

### 8.1 Restore por fallo menor (corrupcion parcial de datos)

```
1. Identificar la tabla o dataset afectado
2. Restaurar desde el backup mas reciente solo ese dataset
3. Verificar consistencia con los datos existentes
4. Notificar al equipo
```

### 8.2 Restore completo por desastre

```
1. DECLARAR DESASTRE
   - Notificar al equipo completo
   - Activar DRP (ver doc 01, Seccion 7.2)

2. PROVISIONAR INFRAESTRUCTURA
   - Crear nuevo VPS con las mismas especificaciones
   - Instalar Docker, Docker Compose, Nginx
   - Configurar firewall y acceso SSH

3. RESTAURAR CONFIGURACION
   - Descargar backup de configuracion desde almacenamiento externo
   - Descifrar y descomprimir
   - Copiar docker-compose.yml, .env, nginx.conf al nuevo VPS

4. RESTAURAR BASE DE DATOS
   - Descargar backup de BD mas reciente
   - Descifrar y descomprimir
   - Importar en MySQL

5. INICIAR SERVICIOS
   - docker compose up -d
   - Verificar que todos los contenedores esten healthy

6. VALIDAR
   - Probar endpoints de la API
   - Verificar dashboard web
   - Verificar conexion MQTT
   - Ejecutar pruebas de integracion basicas

7. REDIRIGIR DNS
   - Actualizar registro A al nuevo VPS
   - Esperar propagacion (TTL configurado a 5 minutos)

8. COMUNICAR
   - Notificar restauracion a stakeholders
   - Registrar tiempo total de recuperacion
```

## 9. Seguridad de los Backups

### 9.1 Cifrado

- Todos los backups incluyendo datos confidenciales se cifran con GPG AES-256
- La clave de cifrado se almacena en el gestor de secrets (1Password / Infisical)
- La clave no se almacena en el mismo servidor que los backups

### 9.2 Acceso

- Solo el rol Ops y el Director de Proyecto tienen acceso a los backups
- Los backups en almacenamiento externo requieren autenticacion SSH con clave
- No se almacenan backups sin cifrar en ningun destino

### 9.3 Verificacion de integridad

- Cada backup se verifica automaticamente post-creacion (integritiy check)
- La prueba de restore trimestral verifica que los datos se restauren correctamente
- Se mantiene un SHA-256 hash de cada backup para verificacion futura

## 10. Responsabilidades

| Rol | Responsabilidad |
|---|---|
| **Ops** | Ejecutar backup diario automatico, monitorear completitud, ejecutar restore trimestral |
| **Director de Proyecto** | Aprobar cambios en la politica, revisar resultados de pruebas de restore, asegurar cumplimiento de RPO/RTO |

## 11. Excepciones

Toda situacion que impida la ejecucion del backup programado debe:

1. Ser documentada inmediatamente
2. Reprogramarse dentro de las siguientes 12 horas
3. Ser informada al Director de Proyecto
4. Ser analizada para prevenir recurrencia

Si el backup no se ejecuta por 2 dias consecutivos, se considera un incidente P2.

## 12. Documentos Relacionados

- [01-politica-seguridad-informacion.md](./01-politica-seguridad-informacion.md) — Politica SGSI (BCP/DRP)
- [00-gap-assessment.md](./00-gap-assessment.md) — Evaluacion de brecha

## Control de Cambios

| Version | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-06-09 | Version inicial | Director de Proyecto |

---

> Documento generado en el contexto del proyecto academico ManttoAI — INACAP.
> Proyecto: Plataforma de Monitoreo IoT por Rubro.
