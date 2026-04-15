# 25. Matriz de Probabilidad e Impacto

## Escala
- **Impacto (X):** Bajo (1) - Medio (2) - Alto (3)
- **Probabilidad (Y):** Baja (1) - Media (2) - Alta (3)
- **Zona Verde:** 1 a 3 (Aceptable)
- **Zona Amarilla:** 4 a 6 (Requiere Plan de Mitigación)
- **Zona Roja:** 9 (Requiere Acción Inmediata)

## Matriz

| Probabilidad \ Impacto | Bajo (1) | Medio (2) | Alto (3) |
|------------------------|:--------:|:---------:|:--------:|
| **Alta (3)**           |          |           | 🔴 **R01** |
| **Media (2)**          |          | 🟡 **R03**, **R06** | 🟡 **R02** |
| **Baja (1)**           |          | 🟢 **R07** | 🟢 **R04**, **R05** |

*R01 (Inestabilidad ESP32) se resolvió de forma inmediata creando el Simulador de Software IoT.*
