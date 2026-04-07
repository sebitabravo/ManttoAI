# ADR-002: Selección de Random Forest para predicción de riesgo

**Fecha:** 2024-11-20  
**Estado:** Aceptado  
**Contexto:** Necesitamos un modelo de Machine Learning para predecir riesgo de falla en equipos. Las opciones consideradas fueron: Regresión Logística, Random Forest, XGBoost, y una red neuronal simple.

**Decisión:** Usar Random Forest Classifier del módulo scikit-learn.

**Razones:**
1. **Interpretabilidad**: Random Forest ofrece feature importance, permitiendo explicar qué variables (temperatura, vibración) contribuyen más al riesgo. Esto es crucial para el informe académico.
2. **Robustez**: No requiere normalización de features, menos sensible a outliers que otros modelos.
3. **Scikit-learn**: Se integra fácilmente con el backend FastAPI usando joblib para serialización.
4. **Dataset pequeño**: Con 1200 registros sintéticos, modelos complejos (deep learning) sobreajustarían.
5. **Objetivo académico**: Random Forest con F1 >= 80% es alcanzable y demostrable.

**Consecuencias:**
- Positivas: Entrenamiento rápido, inferencia en milisegundos, fácil de debuggear.
- Negativas: No es el modelo más preciso para datos complejos, pero suficiente para el alcance del MVP.

**Notas:** El modelo se entrena offline y se serializa como archivo .joblib. No se usa deep learning por restricciones del proyecto (ver AGENTS.md).