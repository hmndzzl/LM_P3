# Matriz requisito → implementación → verificación

## Estado

La implementación técnica de M3 está conectada a M1/M2. La aceptación global
conserva revisión humana y ensayo pendientes. La revisión del PDF completo y el
recorrido para exponer están en [presentacion.md](presentacion.md). Evidencia actual de M3 en
[evidencias/miembro-3.md](evidencias/miembro-3.md); los informes de M1/M2 conservan
su alcance histórico, anterior a la interfaz completa.

| Requisito | Implementación disponible | Verificación actual | Falta para aceptación global |
| --- | --- | --- | --- |
| R1: símbolos configurables | Fichas unificadas de constantes, funciones y predicados; nombres/aridades configurables | Suite de M2 y configuración propia desde la UI | Revisión humana con otros nombres |
| R2: interpretación | D y selectores gráficos; funciones totales y relaciones no vacías verificadas por M2 | Normalización, omisiones, conflictos, vacíos y valores fuera de D; HTTP real | Revisión cruzada del recorrido |
| R3: sintaxis | Parser de M2, alias y nueve botones con paréntesis | AST y tablas de verdad; inserción, selección y undo/redo en Chromium | Otro navegador y revisión de notación |
| R4: entorno | Análisis previo y selectores de variables libres | Fórmulas abiertas/cerradas, alcance/sombra y aridad cero | Ensayo con fórmula nueva |
| R5: interfaz | Formularios, barra lógica, teclado y estados en español | 208 comprobaciones UI en total; configuración propia, edición con lápiz y aceptación, foco y adaptación | Lector de pantalla y revisión humana completa |
| R6: evidencia | Testigo, contraejemplo, cobertura completa, términos y resaltado | Cuatro resultados cuantificados, caso integrado, rangos Unicode, valores de función y cobertura completa | M1 revisa explicaciones y compañeros recorren evidencia |
| R7: errores sin verdad | Builders y validación antes del motor; foco en campo/fila | Suite de errores/HTTP; nueve clases de error y reparación en el ensayo técnico de presentación | Revisión humana del catálogo completo |
| Aporte creativo | Comparación de un cambio, dos trazas y pasos afectados | Función/relación/asignación; cambio de verdad y de evidencia con la misma verdad; sugerencias desde la traza y base intacta | Observación real de utilidad y defensa del aporte |
| Reproducción | Arranque local, lanzadores, sin paquetes/red externa | Copia Linux sin .git ni entorno virtual: 149 pruebas Python; recorrido actual de 208 comprobaciones UI | Ejecución nativa macOS/Windows por el equipo |
| Defensa individual | Rúbrica, guion, caso integrado y preguntas de código en presentacion.md | Material preparado, no ensayo inventado | Los tres responden preguntas de todos los módulos |
| Coevaluación | Sin valoraciones generadas de compañeros | Registro de aportes humanos por completar | Cada integrante documenta su colaboración real |

## Revisión de la interfaz pendiente

La ficha siguiente se reserva para otro integrante: nombre/fecha, sistema/navegador,
caso y pasos, esperado/observado, evidencia real, corrección y nueva verificación.
Las pruebas automáticas no sustituyen esta revisión ni autorizan marcarla realizada.

1. Desde una sesión nueva, configurar un lenguaje propio sin ayuda del autor.
2. Probar todos los símbolos con teclado, selección, deshacer y rehacer.
3. Recorrer Q01–Q04, S02/S03 y S04 de casos-didacticos.md; explicar cada instancia.
4. Repetir E01–E11 y sus reparaciones, incluida la prevención de valores desde selectores.
5. Comparar C01/C02/C03, conservando la base y rechazando variantes inválidas.
6. Revisar lector de pantalla, zoom, foco, fuentes y plataformas del equipo.
7. Ejecutar una copia limpia y los guiones de presentacion.md.

La animación solicitada es decorativa y respeta movimiento reducido: no cuenta como
justificación semántica ni sustituye el aporte de navegación/comparación.

## Condiciones de puntuación de la guía oficial

La página 1 establece siete requisitos obligatorios. La página 2 asigna 30 puntos
a evaluación semántica y justificación, 10 a análisis sintáctico, 10 a interfaz y
30 a defensa individual. Los aportes creativos suman 20: originalidad 5, valor 6,
implementación 6 y justificación/defensa 3. Son criterios de evaluación del docente;
la verificación técnica no asigna esos puntos.

El máximo es 80 sin ticket, 90 con plata y 100 con oro. Para aspirar a 100 también
se necesita quedar entre los dos más votados en la final. El ticket no reemplaza
el cumplimiento de los criterios. Se mantienen pendientes el ensayo del equipo,
las observaciones humanas y la coevaluación individual real.
