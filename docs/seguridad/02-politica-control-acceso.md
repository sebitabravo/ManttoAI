# Politica de Control de Acceso

- **Version:** 1.0
- **Fecha:** 2026-06-09
- **Clasificacion:** Uso interno / Confidencial
- **Aprobado por:** Director de Proyecto — ManttoAI
- **Proxima revision:** 2026-09-09 (trimestral)

---

## 1. Proposito

Establecer las reglas para la gestion de identidades, accesos y privilegios en la plataforma ManttoAI, asegurando que cada usuario tenga unicamente los permisos necesarios para cumplir sus funciones (principio de minimo privilegio), y que dichos accesos sean revisados, revocados y auditados periodicamente.

## 2. Alcance

Esta politica aplica a:

- Todos los usuarios humanos: administradores, tecnicos y visualizadores
- Todas las cuentas de servicio y aplicaciones (backend, MQTT, base de datos)
- Todos los sistemas: API REST, dashboard web, MQTT broker, VPS, base de datos MySQL, repositorios Git

## 3. Principios Fundamentales

### 3.1 Principio de minimo privilegio

Cada usuario o proceso debe tener unicamente los permisos estrictamente necesarios para realizar su funcion. Ningun acceso debe ser concedido "por si acaso".

### 3.2 Separacion de funciones

Las responsabilidades deben segmentarse para evitar que una sola persona tenga control completo sobre un proceso critico. Ejemplo: quien desarrolla no despliega a produccion sin revision.

### 3.3 Acceso por defecto denegado

Todo acceso esta denegado por defecto. Los permisos se conceden explicitamente segun necesidad demostrada y aprobada.

### 3.4 Revision periodica

Todos los accesos se revisan trimestralmente para verificar que siguen siendo necesarios y apropiados.

### 3.5 Trazabilidad

Cada acceso debe ser atribuible a una identidad unica. No se permiten cuentas compartidas ni cuentas genericas.

## 4. Roles y Perfiles de Acceso

### 4.1 Roles del sistema

| Rol | Descripcion | Acceso a datos |
|---|---|---|
| **admin** | Administrador del sistema. Gestiona usuarios, configura umbrales, visualiza todo. | Lectura y escritura en todos los modulos |
| **tecnico** | Tecnico de mantenimiento. Visualiza equipos, registra mantenimientos, ve alertas. | Lectura en equipos y telemetria; escritura en mantenimiento |
| **visualizador** | Usuario final (cliente). Visualiza dashboard, alertas e historial de su rubro. | Solo lectura; limitado a su rubro |

### 4.2 Matriz de permisos por rol

| Recurso / Accion | admin | tecnico | visualizador |
|---|---|---|---|
| Dashboard (lectura) | Si | Si | Si (rubro propio) |
| Equipos — ver lista | Si | Si | Si (rubro propio) |
| Equipos — crear/editar/eliminar | Si | No | No |
| Telemetria — ver historial | Si | Si | Si (rubro propio) |
| Telemetria — exportar | Si | Si | No |
| Umbrales — configurar | Si | No | No |
| Alertas — ver | Si | Si | Si (rubro propio) |
| Alertas — confirmar/resolver | Si | Si | No |
| Mantenimiento — registrar | Si | Si | No |
| Mantenimiento — historial | Si | Si | Si (rubro propio) |
| Usuarios — gestionar | Si | No | No |
| Reportes — generar | Si | Parcial | No |
| Configuracion del sistema | Si | No | No |
| Logs de auditoria | Si | No | No |

### 4.3 Roles de infraestructura

Ademas de los roles del sistema, se definen roles funcionales para el equipo interno:

| Rol | Acceso VPS | Acceso MySQL | Acceso Git | Acceso MQTT |
|---|---|---|---|---|
| **Ops** | SSH completo | root | lectura | administrador |
| **Backend** | No directo | schema app | escritura (branch feature) | subscribe/publish |
| **Frontend** | No directo | No directo | escritura (branch feature) | No |
| **Hardware** | No directo | No directo | escritura (firmware) | publish solo |

## 5. Gestion de Identidades y Autenticacion

### 5.1 Autenticacion de usuarios del sistema (dashboard)

- Autenticacion via JWT (JSON Web Token) con expiracion de 24 horas
- Contrasenas con requisitos minimos: 12 caracteres, mayuscula, minuscula, numero, simbolo
- Bloqueo de cuenta tras 5 intentos fallidos durante 15 minutos
- Sesion inactiva se cierra automaticamente tras 30 minutos

### 5.2 Autenticacion de dispositivos IoT

- Cada dispositivo ESP32 autentica via credenciales MQTT unicas
- Las credenciales se asignan por MAC address del dispositivo
- El backend resuelve la MAC para identificar el equipo asociado

### 5.3 Autenticacion de servicios internos

- Comunicacion backend-MQTT: credenciales dedicadas desde `.env`
- Comunicacion backend-MySQL: usuario de aplicacion con schema limitado
- Acceso SSH al VPS: solo por clave publica, sin contrasena

## 6. Onboarding de Usuarios

### 6.1 Procedimiento de alta

```
1. SOLICITUD
   - El Director de Proyecto recibe la solicitud de nuevo usuario
   - Se define el rol y responsabilidades

2. APROBACION
   - El Director de Proyecto aprueba la solicitud
   - Se verifica la necesidad del acceso solicitado

3. CREACION DE CUENTA
   - El admin crea la cuenta en el sistema con el rol asignado
   - Se genera contrasena temporal (valida por 24 horas)
   - Se configuran permisos especificos si aplica

4. ENTREGA
   - Se entregan credenciales al usuario por canal seguro
   - El usuario debe cambiar la contrasena en el primer inicio de sesion
   - Se documenta la asignacion de activos (laptop, dispositivos de prueba)

5. CAPACITACION
   - El usuario recibe induccion en politicas de seguridad
   - Firma el Acuerdo de Uso Aceptable (AUP)
   - Confirma haber leido y entendido esta politica
```

### 6.2 Checklist de onboarding

| Elemento | Responsable | Estado |
|---|---|---|
| Cuenta de usuario creada | Admin | Pendiente |
| Rol y permisos configurados | Admin | Pendiente |
| Credenciales entregadas | Admin | Pendiente |
| Acceso a repositorios Git | Director | Pendiente |
| Induccion de seguridad realizada | Director | Pendiente |
| AUP firmado | Usuario | Pendiente |

## 7. Offboarding de Usuarios

### 7.1 Procedimiento de baja

```
1. NOTIFICACION
   - Se recibe notificacion de desvinculacion (renuncia, termino de contrato, cambio de rol)
   - El Director de Proyecto inicia el proceso de offboarding

2. REVOCACION INMEDIATA
   - Se deshabilita la cuenta de usuario en el sistema
   - Se revocan tokens JWT activos
   - Se eliminan credenciales de servicio si aplica

3. REVISION DE ACTIVOS
   - Se recuperan activos asignados (dispositivos, cuentas de terceros)
   - Se verifica que no queden accesos residuales

4. AUDITORIA
   - Se registra la fecha y hora de desvinculacion
   - Se ejecuta revision rapida de logs por actividad posterior a la baja

5. CIERRE
   - La cuenta permanece deshabilitada por 90 dias (periodo de retencion)
   - Posteriormente se elimina permanentemente
   - Se documenta el cierre
```

### 7.2 Tiempos de ejecucion

| Accion | Tiempo maximo |
|---|---|
| Revocacion de acceso al sistema | 1 hora desde la notificacion |
| Revocacion de accesos de infraestructura | 2 horas |
| Recuperacion de activos fisicos | 5 dias habiles |
| Eliminacion permanente de cuenta | 90 dias post-desvinculacion |

## 8. Revision Trimestral de Accesos

### 8.1 Proceso de revision

Cada trimestre, el Director de Proyecto debe:

1. **Extraer el listado** de todos los usuarios activos con sus roles y ultimo acceso
2. **Verificar cada cuenta**: si el usuario sigue activo en el proyecto y si su rol sigue siendo adecuado
3. **Identificar cuentas inactivas**: usuarios sin acceso en los ultimos 60 dias
4. **Revisar cuentas privilegiadas**: roles admin y accesos de infraestructura
5. **Documentar cambios**: aprobar elevaciones de privilegio, revocar accesos innecesarios

### 8.2 Formato de revision

```
Fecha: [DD/MM/AAAA]
Revisado por: [Nombre]

Usuarios activos: [N]
Cuentas admin: [N]
Cuentas inactivas (>60 dias): [N]
Cuentas revocadas: [N]
Elevaciones de privilegio: [N]

Observaciones:
- [Texto]

Visto bueno: [Firma Director]
```

## 9. Acceso Privilegiado

### 9.1 Cuentas admin

- Maximo 2 personas con rol admin en el sistema
- Acceso SSH al VPS solo por clave publica, con passphrase
- Toda accion privilegiada debe ser registrada en logs
- Las claves de acceso a infraestructura se almacenan en Gestor de Secrets (1Password / Infisical)

### 9.2 Acceso a base de datos

- El usuario `app_manttoai` solo tiene permisos CRUD sobre el schema `manttoai`
- El usuario `root` de MySQL solo se usa para migraciones, no para operacion diaria
- Conexiones MySQL solo desde localhost (Docker interno)

### 9.3 Acceso MQTT

- Credenciales separadas para publish (ESP32) y subscribe (backend)
- Las credenciales se rotan cada 6 meses o ante sospecha de compromiso

## 10. Registro y Auditoria de Accesos

### 10.1 Eventos auditados

| Evento | Registro | Retencion |
|---|---|---|
| Inicio de sesion exitoso | Log de aplicacion | 1 ano |
| Inicio de sesion fallido | Log de aplicacion | 1 ano |
| Cambio de contrasena | Log de auditoria | 1 ano |
| Creacion de usuario | Log de auditoria | 2 anos |
| Eliminacion de usuario | Log de auditoria | 2 anos |
| Cambio de rol/permisos | Log de auditoria | 2 anos |
| Acceso a datos de telemetria | Log de aplicacion | 90 dias |
| Acciones admin | Log de auditoria | 2 anos |
| Acceso SSH | Auth.log del VPS | 90 dias |

### 10.2 Proteccion de logs

- Los logs de auditoria son inmutables (append-only)
- Solo el rol admin puede acceder a logs de auditoria
- Los logs se respaldan junto con la base de datos

## 11. Excepciones

Toda excepcion a esta politica debe:

1. Ser solicitada por escrito al Director de Proyecto
2. Especificar el acceso requerido, la duracion y la justificacion
3. Ser aprobada por el Director de Proyecto
4. Tener una fecha de expiracion definida
5. Ser registrada en el registro de excepciones

Las excepciones se revisan en cada auditoria trimestral.

## 12. Documentos Relacionados

- [01-politica-seguridad-informacion.md](./01-politica-seguridad-informacion.md) — Politica SGSI (marco general)
- [03-politica-backup-recuperacion.md](./03-politica-backup-recuperacion.md) — Backup y recuperacion
- [04-politica-desarrollo-seguro.md](./04-politica-desarrollo-seguro.md) — Desarrollo seguro

## Control de Cambios

| Version | Fecha | Cambio | Autor |
|---|---|---|---|
| 1.0 | 2026-06-09 | Version inicial | Director de Proyecto |

---

> Documento generado en el contexto del proyecto academico ManttoAI — INACAP.
> Proyecto: Plataforma de Monitoreo IoT por Rubro.
