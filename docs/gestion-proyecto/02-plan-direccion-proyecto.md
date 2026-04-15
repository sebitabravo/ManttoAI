# 02. Plan para la Dirección del Proyecto

**Enfoque Metodológico:** Híbrido. Marco predictivo (PMBOK 6ª edición) para la planificación y control académico, combinado con prácticas ágiles (Sprints quincenales, CI/CD con GitHub Actions, despliegue continuo con Dokploy y contenedores Docker).

## Ciclo de Vida del Proyecto (6 Fases)
1. **Inicio:** Definición del alcance y acta de constitución.
2. **Planificación:** Diseño de arquitectura (FastAPI + React + Mosquitto) y PMBOK.
3. **Ejecución (Desarrollo):** Construcción del backend, frontend, modelo Random Forest y firmware IoT / Simulador.
4. **Pruebas (QA):** Pytest (Backend), Playwright (Frontend E2E).
5. **Despliegue:** Configuración en VPS Hetzner usando Dokploy.
6. **Cierre:** Documentación final y defensa académica.

## Líneas Base
- **Alcance:** Definido en el [Enunciado del Alcance](../alcance/06-enunciado-alcance.md) y [EDT](../alcance/07-edt-wbs.md).
- **Cronograma:** Sprints definidos en la [Lista de Actividades](../cronograma/10-lista-actividades.md).
- **Costos:** Presupuesto académico de CLP $9.790.000 vs real de USD $98.

## Control de Cambios
Cualquier modificación al alcance (ej. integración del simulador IoT en el backend) debe ser documentada, evaluada por su impacto en tiempo/costo, y aprobada por el Director del Proyecto antes de integrarse a la rama `main` de GitHub.
