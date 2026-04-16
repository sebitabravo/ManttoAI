### E2E Tests: Wizard de Onboarding

**Suite ID:** `ONBOARDING-E2E`
**Feature:** Wizard de configuración inicial para nuevos usuarios

---

## Test Case: `ONBOARDING-E2E-001` - Completa el wizard de onboarding exitosamente

**Priority:** `critical`

**Tags:**
- type → @e2e
- feature → @onboarding

**Description/Objective:** Verificar que un usuario nuevo puede completar el wizard de onboarding guiado, creando un equipo, configurando umbrales, generando una API key y finalizando el proceso exitosamente.

**Preconditions:**
- Usuario autenticado con rol admin
- Usuario no ha completado el onboarding
- APIs mockeadas para simular respuestas del backend

### Flow Steps:
1. Navegar a `/onboarding`
2. Verificar paso 1 (Bienvenida) con mensaje de bienvenida
3. Hacer clic en "Comenzar" para avanzar al paso 2
4. Llenar formulario de equipo con nombre y ubicación
5. Hacer clic en "Siguiente" para avanzar al paso 3
6. Verificar umbrales pre-configurados (temperatura: 80°C, vibración: 0.5g)
7. Hacer clic en "Siguiente" para avanzar al paso 4
8. Hacer clic en "Generar API Key"
9. Verificar que se muestra la API Key generada
10. Hacer clic en "Siguiente" para avanzar al paso 5
11. Verificar resumen de configuración completada
12. Hacer clic en "Ir al Dashboard"
13. Verificar redirección a `/dashboard`

### Expected Result:
- Usuario completa todos los 5 pasos del wizard
- Se crea un equipo con los datos proporcionados
- Se configuran umbrales de temperatura y vibración
- Se genera una API Key para el dispositivo IoT
- El wizard marca el onboarding como completado
- Usuario es redirigido al dashboard

### Key verification points:
- Paso 1: Mensaje de bienvenida visible
- Paso 2: Formulario de equipo funcional
- Paso 3: Umbrales con valores por defecto
- Paso 4: API Key generada y visible
- Paso 5: Resumen de configuración
- Redirección final a `/dashboard`

### Notes:
- Este test verifica el flujo completo del wizard
- Todos los endpoints del backend están mockeados
- El test simula un usuario real completando el wizard

---

## Test Case: `ONBOARDING-E2E-002` - Permite saltar el wizard

**Priority:** `medium`

**Tags:**
- type → @e2e
- feature → @onboarding

**Description/Objective:** Verificar que el usuario puede saltar el wizard de onboarding y configurarlo después.

**Preconditions:**
- Usuario autenticado
- Usuario no ha completado el onboarding

### Flow Steps:
1. Navegar a `/onboarding`
2. Verificar que el botón "Saltar y configurar después" es visible
3. Hacer clic en "Saltar y configurar después"
4. Verificar redirección a `/dashboard`

### Expected Result:
- Usuario puede saltar el wizard en cualquier momento
- El onboarding se marca como completado (sin recursos creados)
- Usuario es redirigido al dashboard

### Key verification points:
- Botón de saltar visible en todos los pasos
- Redirección a dashboard al saltar

### Notes:
- Esta funcionalidad permite a usuarios expertos configurar el sistema manualmente
- El wizard marca el onboarding como completado pero sin crear recursos

---

## Test Case: `ONBOARDING-E2E-003` - Permite navegar entre pasos

**Priority:** `medium`

**Tags:**
- type → @e2e
- feature → @onboarding

**Description/Objective:** Verificar que el usuario puede navegar hacia adelante y atrás entre los pasos del wizard.

**Preconditions:**
- Usuario autenticado
- Usuario no ha completado el onboarding

### Flow Steps:
1. Navegar a `/onboarding`
2. Verificar paso 1 visible
3. Hacer clic en "Comenzar" para avanzar al paso 2
4. Verificar paso 2 visible
5. Hacer clic en "Anterior" para volver al paso 1
6. Verificar paso 1 visible con título de bienvenida
7. Hacer clic en "Comenzar" para avanzar nuevamente al paso 2
8. Verificar paso 2 visible

### Expected Result:
- Usuario puede navegar hacia adelante en el wizard
- Usuario puede navegar hacia atrás en el wizard
- El progreso del paso se guarda correctamente
- El contenido de cada paso se muestra correctamente

### Key verification points:
- Botón "Anterior" aparece en pasos 2-5
- Navegación hacia adelante actualiza el paso actual
- Navegación hacia atrás restaura el paso anterior
- Barra de progreso refleja el paso actual

### Notes:
- Esta funcionalidad permite a los usuarios corregir errores en pasos anteriores
- El progreso se persiste en el backend

---

## Test Case: `ONBOARDING-E2E-004` - Muestra error cuando falla la creación de equipo

**Priority:** `low`

**Tags:**
- type → @e2e
- feature → @onboarding

**Description/Objective:** Verificar que el wizard maneja correctamente los errores del backend, mostrando mensajes de error claros al usuario.

**Preconditions:**
- Usuario autenticado
- Usuario está en el paso 2 del wizard
- API de equipos retorna error 500

### Flow Steps:
1. Navegar a `/onboarding`
2. Avanzar al paso 2
3. Llenar formulario de equipo
4. Intentar avanzar al paso 3
5. Verificar que se muestra mensaje de error

### Expected Result:
- El wizard detecta el error del backend
- Se muestra un mensaje de error claro al usuario
- El usuario permanece en el paso actual
- El usuario puede intentar nuevamente

### Key verification points:
- Mensaje de error visible
- Usuario no es redirigido al siguiente paso
- Botón de reintentar funcional

### Notes:
- Este test verifica el manejo de errores del wizard
- Los mensajes de error deben ser claros y accionables
