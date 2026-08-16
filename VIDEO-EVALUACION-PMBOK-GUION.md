# Guion y Guía de Producción — Video Evaluación PMBOK

**Principios a aplicar:** Administración (Stewardship) + Interesados (Stakeholder Engagement)
**Proyecto base:** ManttoAI — Plataforma de Monitoreo IoT por Rubro
**Entrega:** lunes 6 de julio de 2026, presencial, horario de clases. Video subido a YouTube.
**Duración máxima:** 10 minutos.

---

## 0. Leer esto primero

### Ficha de la evaluación
- **Marco de actuación:** el grupo habla como una consultora externa de dirección de proyectos que presenta hallazgos y una recomendación **a la gerencia** de ManttoAI (los 3 socios/directorio). No se habla como estudiantes ni se menciona "el profesor" o "la evaluación": se dice "la gerencia", "el directorio", "nuestro cliente".
- **Índice obligatorio:** Introducción → Objetivo General → Objetivos Específicos → Desarrollo (4.1 Administración, 4.2 Interesados) → Conclusiones y sugerencia a la gerencia.
- **Todos los integrantes deben hablar** en el video (exigido por pauta).
- **Puntaje conocido de la pauta:** contenido de fondo (40 pts), capas transversales SimulTrain + 7 C's (10 pts), formato institucional INACAP en diapositivas (5 pts). Si existen más criterios en la pauta oficial, revisen el documento del profesor antes de grabar.

### Dos advertencias importantes antes de grabar

1. **PMBOK 6ta vs 7ma edición.** Toda la documentación del repo (acta de constitución, informe final, planes de gestión) fue redactada bajo PMBOK **6ta edición** (procesos y áreas de conocimiento). Esta evaluación puntual pide específicamente los **12 Principios de la Dirección de Proyectos de PMBOK 7ma edición**, que son una capa distinta: valores y principios, no procesos. No es una contradicción, es una lente distinta sobre las mismas decisiones ya documentadas. En el video, al hablar de Administración e Interesados como **principios**, digan "Guía PMBOK, séptima edición". No digan "6ta edición" en ese contexto para evitar una confusión de conceptos frente a la gerencia.
2. **Versión de las 7 C's.** Existe más de una versión del marco de "7 C's del marketing de contenidos" (varía el autor/apunte). Este documento usa la versión más difundida: **Contenido, Contexto, Conexión, Comunidad, Conversación, Personalización (Customization), Conversión**. Confirmen con el material del profesor o el foro del curso si usó otra variante antes de grabar. Si la variante difiere, solo hay que renombrar 1 o 2 conceptos en la sección 3.2; el resto del guion no cambia.

---

## 1. Reparto de roles y timing

Basado en los roles reales del proyecto (acta de constitución, RACI, organigrama): Sebastián es Director de Proyecto (autoridad sobre presupuesto/arquitectura/control de cambios → encaja natural con Administración), Luis es Frontend y CEO/Comercial en el plan de negocios (cara visible ante interesados → encaja natural con Interesados), Ángel es Arquitecto/ML (visión técnica global → encaja natural cerrando con la recomendación).

| # | Bloque | Duración objetivo | Habla |
|---|--------|--------------------|-------|
| 1 | Apertura + Introducción | 0:45 | Sebastián |
| 2 | Objetivo General | 0:30 | Luis |
| 3 | Objetivos Específicos | 0:45 | Luis |
| 4 | Desarrollo 4.1 — Administración | 2:40 | Sebastián |
| 5 | Desarrollo 4.2 — Interesados | 2:40 | Luis |
| 6 | Conclusiones y sugerencia a la gerencia | 2:00 | Ángel |
| 7 | Cierre | 0:20 | Los tres |

**Total estimado: ~9:40.** El guion hablado (sección 2) suma aproximadamente 1.160 palabras a ritmo de presentación formal (~150 palabras/min), lo que da cerca de 2 minutos de margen para transiciones de diapositiva, pausas y respiración. No lean el guion palabra por palabra frente a cámara: memoricen la idea de cada párrafo y díganla con sus palabras, así suena a consultora y no a lectura.

---

## 2. Guion completo (hablado)

### 2.1 Apertura + Introducción — Sebastián (0:45)

> Buenas tardes. Somos el equipo consultor a cargo de la revisión de dirección de proyectos de ManttoAI, la plataforma de monitoreo IoT por rubro industrial, agrícola y comercial. Venimos ante la gerencia a presentar los resultados de esa revisión, en el marco del cierre de la versión uno cero. El análisis se centra en dos de los doce principios de la Guía PMBOK, séptima edición: Administración, la gestión responsable de los recursos, y Compromiso con los Interesados. A partir de esta revisión, entregaremos un diagnóstico y una recomendación concreta para los próximos pasos del proyecto.

### 2.2 Objetivo General — Luis (0:30)

> El objetivo general del proyecto que evaluamos es capturar telemetría IoT y predecir fallas mediante un modelo de machine learning, integrado en un dashboard web. Es decir, que empresas de los rubros industrial, agrícola y comercial puedan anticipar paradas no planificadas de sus equipos antes de que ocurran, en lugar de reaccionar cuando ya es tarde.

### 2.3 Objetivos Específicos — Luis (0:45)

> Para lograrlo, el equipo definió tres objetivos específicos. Primero, capturar lecturas de temperatura, humedad y vibración desde dispositivos ESP32 vía protocolo MQTT. Segundo, implementar un modelo Random Forest para evaluar el riesgo de falla de cada equipo. Y tercero, dejar preparado el despliegue del sistema completo en un servidor con alertas en tiempo real. Los tres objetivos técnicos se cumplieron en el prototipo verificable localmente: el modelo alcanzó 94,1% de accuracy y 93% de F1-score, muy por sobre el 80% mínimo exigido, y más de 300 pruebas automatizadas respaldan su estabilidad. La URL pública se anunciará solo después de verificar el proveedor externo.

### 2.4 Desarrollo 4.1 — Administración (Stewardship) — Sebastián (2:40)

> El primer principio que revisamos es Administración, lo que en inglés se conoce como Stewardship: ser un administrador responsable, cuidadoso e íntegro de los recursos del proyecto, ya sean financieros, humanos o técnicos. En ManttoAI esto se ve en tres decisiones concretas.
>
> Primero, en el gobierno del proyecto: el acta de constitución establece que el Director de Proyecto tiene autoridad para asignar tareas, aprobar pull requests y decidir la arquitectura base, pero siempre dentro de las restricciones de presupuesto y alcance acordadas con el patrocinador.
>
> Segundo, en el control de cambios: cada modificación de alcance, como la incorporación del simulador IoT como servicio permanente o el auto-refresh del frontend, fue evaluada por su impacto en tiempo y costo antes de aprobarse e integrarse al repositorio. La matriz RACI refuerza esto mismo, asignando de forma clara quién ejecuta, quién aprueba y a quién se consulta en cada actividad, evitando duplicar esfuerzo o dejar responsabilidades sin dueño.
>
> Y tercero, en la administración financiera: el capital de tres millones de pesos aportado por los tres socios se gestiona con seguimiento mensual de valor ganado, exigiendo un índice de desempeño de costos sobre 0,95, y cualquier desviación superior al diez por ciento requiere aprobación del directorio antes de ejecutarse. Más del ochenta por ciento de ese capital se mantiene como reserva de gestión, no como gasto inmediato. Esa misma disciplina se refleja en el prototipo técnico, construido con menos de cien dólares reales, evitando deliberadamente arquitecturas sobredimensionadas como microservicios o Kubernetes que no aportaban valor a esta escala.
>
> Esta lógica de trade-offs entre tiempo, costo, alcance y calidad es exactamente lo que trabajamos en el simulador SimulTrain durante el curso: cada decisión de recursos tiene un costo de oportunidad, y administrar bien un proyecto significa tomar esas decisiones de forma consciente, no reactiva. Eso es lo que aplicamos en ManttoAI.

### 2.5 Desarrollo 4.2 — Interesados (Stakeholder Engagement) — Luis (2:40)

> El segundo principio es Compromiso con los Interesados: identificar de forma proactiva a quienes influyen o son afectados por el proyecto, entender qué esperan, y ajustar cómo nos relacionamos con cada uno según su poder y su interés real.
>
> En ManttoAI identificamos siete interesados y los clasificamos en una matriz de poder e interés. Cuatro de ellos, el evaluador de INACAP y los tres integrantes del equipo en sus roles de dirección, frontend y arquitectura, tienen alto poder y alto interés, por lo que se gestionan de cerca, con comunicación diaria vía Discord y reuniones semanales presenciales. Un quinto interesado, el rol de QA y DevOps, tiene interés alto pero menor poder de decisión, así que se mantiene informado y se consulta puntualmente. Y dos interesados externos, el proveedor de VPS y el proveedor de hardware, tienen bajo poder e interés, por lo que solo se monitorean, asegurando pagos oportunos.
>
> Pero no nos quedamos en clasificar: para cada uno definimos un plan concreto para cerrar la brecha entre su estado actual y el estado deseado. Con el evaluador, pasamos de una postura expectante a una partidaria demostrando rigor técnico, entregando la documentación PMBOK completa y evidencia real de testing, con ochenta y dos por ciento de cobertura. Con el equipo, pasamos de estar simplemente involucrados a liderar el proyecto, sosteniendo la motivación con hitos cortos, code reviews colaborativos y una distribución equitativa de tareas. Y con los proveedores, mantuvimos una relación neutral pero confiable, con facturación automática.
>
> En el simulador SimulTrain vimos algo que se repite en la práctica: ignorar a un interesado de alto poder, aunque sea por poco tiempo, termina generando retrabajo o decisiones que hay que revertir. Por eso priorizamos la comunicación diaria con los interesados críticos desde la semana uno, no una vez que surgía un problema.

### 2.6 Conclusiones y sugerencia a la gerencia — Ángel (2:00)

> En síntesis, la combinación de una administración responsable de los recursos y un compromiso genuino con los interesados no fue un ejercicio aislado: fue lo que permitió cerrar la versión uno cero de ManttoAI cumpliendo todos los criterios de éxito, con un modelo de machine learning que superó el noventa y cuatro por ciento de accuracy y un sistema con más del ochenta por ciento de cobertura de pruebas.
>
> Esa misma disciplina de administración es la que hoy sostiene el plan de negocio: con tres millones de pesos de capital y control mensual de valor ganado, ManttoAI tiene autonomía financiera para validar su modelo comercial en los tres rubros sin depender de ingresos inmediatos.
>
> Nuestra recomendación a la gerencia es simple: no tratar estas dos prácticas como entregables de un curso, sino como procesos vivos de la empresa. Formalizar la matriz de interesados y el RACI como herramientas de gestión permanente, y mantener el mismo umbral de control de costos, ese cero coma noventa y cinco de índice de desempeño, también en la operación comercial, no solo en el prototipo. Si esta disciplina se sostiene al escalar, ManttoAI tiene una base sólida para crecer sin perder el control que la trajo hasta acá.

### 2.7 Cierre — Los tres (0:20)

> Muchas gracias por su tiempo. Quedamos atentos a cualquier pregunta de la gerencia.

*(Cada integrante puede decir su nombre y rol en una frase corta antes del agradecimiento conjunto, para reforzar que los tres participaron.)*

---

## 3. Capas transversales obligatorias

### 3.1 SimulTrain (conceptual)

Ya integrado directamente en el guion (secciones 2.4 y 2.5), con dos menciones distintas para que no suene repetitivo ni forzado:
- En Administración: el simulador como ejercicio de trade-offs entre tiempo, costo, alcance y calidad.
- En Interesados: el simulador como evidencia de que ignorar a un interesado de alto poder genera retrabajo.

**No se mencionan cifras ni resultados exactos de la simulación**, tal como exige la pauta. Si el profesor pregunta algo puntual sobre la simulación en vivo, respondan con la lección aprendida, no con números de la partida jugada.

### 3.2 Marketing de contenidos — 7 C's aplicadas al video

La pauta exige un mínimo de 5 de 7. Se aplican las siguientes 5, como decisiones de producción del propio video (no hace falta nombrarlas en voz alta, son la justificación de por qué el video está construido así):

| C | Cómo se aplica en este video |
|---|---|
| **Contenido** | El guion usa datos reales del proyecto (accuracy, cobertura, presupuesto), no relleno genérico. |
| **Contexto** | El mensaje se ubica en el momento exacto del proyecto: cierre de v1.0.0 y Evaluación 3 en curso. |
| **Conexión** | Se habla en el lenguaje de la gerencia (riesgo, autonomía financiera, control) en vez de jerga académica. |
| **Personalización (Customization)** | El propio Plan de Involucramiento de Interesados ya personaliza el mensaje según cada stakeholder; se referencia explícitamente en 2.5. |
| **Conversión** | El video cierra con una recomendación concreta y accionable a la gerencia (sección 2.6), no solo información. |

**Comunidad** y **Conversación** se dejan fuera deliberadamente: un video grabado de 10 minutos, sin interacción en vivo, no permite construir comunidad ni sostener una conversación real con la audiencia. Es preferible dejarlas fuera y no forzarlas, ya que la pauta penaliza la mención anecdótica o forzada.

---

## 4. Estructura de diapositivas (formato institucional INACAP, 5 pts)

Usar plantilla oficial INACAP (logo, colores institucionales, pie de página con asignatura e integrantes). Sugerencia de 11 diapositivas:

1. **Portada:** logo INACAP, "ManttoAI — Revisión de Dirección de Proyectos", integrantes, asignatura, fecha.
2. **Índice:** Introducción, Objetivo General, Objetivos Específicos, Desarrollo (4.1 / 4.2), Conclusiones.
3. **Introducción:** contexto del proyecto + marco de la consultoría ante la gerencia.
4. **Objetivo General.**
5. **Objetivos Específicos:** los 3 puntos + resultado logrado (94,1% accuracy, 82% cobertura).
6. **4.1 Administración:** los 3 sub-puntos (gobierno, control de cambios/RACI, gestión financiera).
7. **4.1 (dato visual):** reserva de gestión 83,6% del capital, umbral CPI ≥ 0,95.
8. **4.2 Interesados:** matriz poder/interés (reutilizar la tabla 2x2 de `docs/interesados/28-matriz-poder-interes.md`).
9. **4.2 (dato visual):** tabla estado actual → estado deseado del plan de involucramiento.
10. **Conclusiones y sugerencia a la gerencia.**
11. **Cierre:** agradecimiento, logos, enlace al repositorio.

---

## 5. Checklist antes de grabar

- [ ] Confirmar con el profesor/foro cuál versión de las 7 C's usó en clases (ver advertencia en sección 0).
- [ ] Revisar la pauta oficial completa por si hay criterios adicionales a los 3 puntajes ya conocidos.
- [ ] Diapositivas en plantilla INACAP, sin errores ortográficos, con el índice exigido visible.
- [ ] Ensayar una vez en voz alta con cronómetro; ajustar si algún bloque se pasa del timing.
- [ ] Fondo neutro/profesional y buena iluminación para los tres integrantes (aunque graben por separado).
- [ ] Acordar quién comparte pantalla y en qué momento se cambia de diapositiva.

## 6. Checklist de producción y entrega (hoy → mañana)

- [ ] **Hoy (contenido pesado):** guion y diapositivas listos, con datos verificados contra este documento.
- [ ] **Hoy en la noche:** grabar el video completo, verificar que no supere los 10 minutos.
- [ ] **Antes de dormir / mañana temprano:** editar (cortes, transiciones, audio parejo entre los tres).
- [ ] **Mañana temprano, con margen:** subir a YouTube, dejar tiempo de procesamiento, verificar que el enlace cargue y el video sea visible (público o no listado, según lo pida el profesor).
- [ ] Llevar el enlace probado y funcionando antes de la clase del lunes 6 de julio.

---

## 7. Fuentes internas usadas (trazabilidad)

Todo el contenido de este guion está anclado en documentación real del repositorio, no en datos genéricos:

- `docs/gestion-proyecto/01-acta-constitucion.md` — objetivos, criterios de éxito, nivel de autoridad, presupuesto.
- `docs/gestion-proyecto/02-plan-direccion-proyecto.md` — control de cambios.
- `docs/recursos/19-matriz-raci.md` y `docs/recursos/18-organigrama-proyecto.md` — gobierno y roles.
- `docs/costos/12-plan-gestion-costos.md` — EVM, capital, reserva de gestión, umbrales de control.
- `docs/interesados/27-registro-interesados.md`, `28-matriz-poder-interes.md`, `29-plan-involucramiento-interesados.md` — los 7 interesados, su clasificación y plan de cierre de brechas.
- `docs/informe-pmbok-final.md` — métricas de cierre (accuracy, cobertura, tests, contribución del equipo).

Si la gerencia (o el profesor) pregunta algo que no está en este guion, la respuesta está en uno de estos documentos.
