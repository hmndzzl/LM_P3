# Matriz requisito → prueba → demostración

## Alcance actual

Esta matriz compartida distingue evidencia Python ejecutada de verificaciones de producto y actividades humanas pendientes. No declara listo el proyecto ni sustituye revisión por otro integrante. Resultados/comandos en las evidencias de [M1](evidencias/miembro-1.md) y [M2](evidencias/miembro-2.md).

| Requisito o criterio | Prueba reproducible actual | Caso de demostración | Falta para aceptación global |
| --- | --- | --- | --- |
| R1: nombres/aridades configurables | `tests.syntax.test_parser.LanguageValidationTests`, `tests.validation.test_normalization.NormalizationTests` y escenarios con nombres personalizados | Configurar relevo/Activa/Enlaza desde el mundo del corpus | Formularios reales y revisión humana |
| R2: interpretación finita válida | Pruebas de normalización: vacíos, pertenencia, totalidad, conflictos, aridad cero y los 16 subconjuntos de una tabla binaria | E01–E04, E07 y E11; Q04 muestra ∃ falso con relaciones no vacías | Recorrido gráfico y rechazo desde HTTP |
| R3: todos los conectivos confirmados | `tests.syntax.test_parser.ParserTests` cubre símbolos/alias, AST manual, precedencia y asociación; pruebas de tablas de verdad de M1 | Q01–Q04, S02–S06 contienen los siete símbolos y alias | Botones/notación de M3 y revisión cruzada |
| R4: fórmulas abiertas/cerradas y entorno | Pruebas de análisis y validación de variables libres, alcance/sombra y asignaciones; `DidacticCorpusTests` contrasta soluciones | S01–S04, E08/E09; C03 cambia solo una asignación libre | Selectores de entorno y conservación durante edición |
| R5: ingreso gráfico, botones y teclado | No hay pruebas ejecutadas de UI; carpetas de frontend aún preparadas | Recorrido de revisión de interfaz, más abajo | Implementación y revisión completa de M3 |
| R6: verdad y razones decisivas | Suite de semántica y pruebas de corpus: testigo, contraejemplo, cobertura completa, valores atómicos e instancias anidadas | Q01/Q02/Q03/Q04 | Visor accesible que conserve toda la evidencia |
| R7: errores sin verdad | `test_external_validation.py` y `test_didactic_corpus.py`: entradas inválidas no invocan al motor; reparaciones calculadas | E01–E11; matriz ampliada de M2-03 | Codec real, controles/servidor y foco/mensajes desde UI |
| Aporte creativo: navegación/comparación | Comparaciones M1 y corpus C01–C03 con parser/validación reales, cambios únicos y base intacta | C01 cambia verdad; C02 cambia testigo sin cambiar verdad; Q03 separa instancias | Navegación gráfica, revisión y observación real de utilidad |
| Defensa individual (30 puntos) | Banco de preguntas y guion preparados; no hay ensayo humano ejecutado | S02/S03, S04, Q03/Q04 y C02 | Enseñanza mutua y defensa aleatoria por los tres |
| Reproducción y entrega | Suite Python y demo del corpus ejecutadas localmente sin paquetes nuevos | `python -X utf8 -B -m examples.corpus` | Arranque gráfico, instalación limpia por el equipo y registro de entornos |
| Coevaluación | No se producen valoraciones de compañeros | Registro de actividades humanas, por completar | Registro humano honesto de aportes, cumplimiento y colaboración |

## Comandos para comprobar la parte disponible

Desde la raíz y con el entorno seleccionado:

```powershell
python -X utf8 -B -m unittest discover -s tests -t . -v
python -X utf8 -B -m examples.corpus
python -X utf8 -B -m examples.corpus --case Q03 --json
python -X utf8 -B -m examples.corpus --case C02 --json
```

Para soluciones, datos y preparación de defensa usar [casos-didacticos.md](casos-didacticos.md). El ticket de competencia fija el techo de la nota y no demuestra cumplimiento de ninguno de estos criterios.

## Revisión de la interfaz pendiente

La inspección registrada del 15 de noviembre de 2026 encontró solo carpetas preparadas en frontend y `__init__.py` en server. Ninguna comprobación gráfica siguiente se ha ejecutado; no hay capturas ni aprobación de accesibilidad. Las pruebas Python están en la [evidencia consolidada de M2](evidencias/miembro-2.md).

Configurar Red de estaciones conservando el orden norte, centro, sur. La carga de ejemplo debe ser explícita, editable y conservar el trabajo existente. Ejecutar Q01–Q04 y C01–C03 desde el editor: comprobar testigos, contraejemplo, todas las asignaciones, instancias anidadas y base intacta.

Para R7, partir de Activa(x) con x=centro y aplicar por separado E01–E11 según [casos didácticos](casos-didacticos.md#errores-y-reparaciones-del-mismo-mundo). Evaluar, comprobar ausencia de verdad, resumen enfocable con enlace y mensaje local; reparar y reevaluar sin perder otros datos. Si un control previene un valor inválido, registrar esa prevención y probar además el rechazo mediante el servidor real cuando exista; no duplicar validación en handlers.

| Revisión | Procedimiento y resultado esperado | Estado |
| --- | --- | --- |
| Editor | Siete símbolos y paréntesis, cursor/selección, foco, teclado y undo/redo; alias equivalentes | Pendiente |
| Variables libres | S02 solicita x, S03 no; escritura incompleta conserva asignaciones recuperables | Pendiente |
| Unicode | `Activa(𝑥) ∧ Enlaza(x)` señala el error en Enlaza tras convertir puntos de código a UTF-16 | Pendiente |
| Contexto | Editar datos invalida resultado/traza; respuesta asíncrona vieja no sobrescribe la revisión nueva | Pendiente |
| Evidencia | Navegable con teclado por instancia; cobertura completa y diferencia entre No visitado y Falso | Pendiente |
| Estados | Q02 es Falso válido y E02 es entrada inválida; significado independiente del color | Pendiente |
| Accesibilidad | Etiquetas, orden de foco, lector y anuncio coherente de resumen/resultado | Pendiente |
| Adaptación | 320/768/1024/1440 px, zoom 200%, reflujo y scroll local; capturas y contraste reales | Pendiente |
| Recursos | Fuentes/símbolos sin Internet; límites con causa y No evaluado; Cancelar solo con soporte real | Pendiente |
| HTTP | Conservar filas/rechazar claves JSON repetidas; revisar tamaño, loopback y Host/Origin | Pendiente |

Ficha de ejecución: revisor, fecha real, navegador/sistema y versión; caso y pasos; esperado/observado; evidencia real; criterio incumplido; corrección, responsable y nueva verificación; estado y limitaciones. Todo está por registrar. La aceptación global exige revisión humana, resolver observaciones y completar enseñanza/defensa; esta ficha no certifica controles ausentes.
