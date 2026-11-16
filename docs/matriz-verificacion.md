# Matriz requisito → prueba → demostración

## Alcance actual

Esta matriz distingue evidencia Python ejecutada de verificaciones de producto y actividades humanas pendientes. No declara listo el proyecto ni sustituye revisión por otro integrante. Para resultados/comandos reales consultar las evidencias de [M1](evidencias/miembro-1.md), [M2-03](evidencias/miembro-2-validacion.md) y [M2-04](evidencias/miembro-2-corpus.md).

| Requisito o criterio | Prueba reproducible actual | Caso de demostración | Falta para aceptación global |
| --- | --- | --- | --- |
| R1: nombres/aridades configurables | `tests.syntax.test_parser.LanguageValidationTests`, `tests.validation.test_normalization.NormalizationTests` y escenarios con nombres personalizados | Configurar relevo/Activa/Enlaza desde el mundo del corpus | Formularios reales y revisión humana |
| R2: interpretación finita válida | Pruebas de normalización: vacíos, pertenencia, totalidad, conflictos, aridad cero y los 16 subconjuntos de una tabla binaria | E01–E04, E07 y E11; Q04 muestra ∃ falso con relaciones no vacías | Recorrido gráfico y rechazo desde HTTP |
| R3: todos los conectivos confirmados | `tests.syntax.test_parser.ParserTests` cubre símbolos/alias, AST manual, precedencia y asociación; pruebas de tablas de verdad de M1 | Q01–Q04, S02–S06 contienen los siete símbolos y alias | Botones/notación de M3 y revisión cruzada |
| R4: fórmulas abiertas/cerradas y entorno | Pruebas de análisis y validación de variables libres, alcance/sombra y asignaciones; `DidacticCorpusTests` contrasta soluciones | S01–S04, E08/E09; C03 cambia solo una asignación libre | Selectores de entorno y conservación durante edición |
| R5: ingreso gráfico, botones y teclado | No hay pruebas ejecutadas de UI; carpetas de frontend aún preparadas | Ficha de editor en revision-m3.md | Implementación y revisión completa de M3 |
| R6: verdad y razones decisivas | Suite de semántica y pruebas de corpus: testigo, contraejemplo, cobertura completa, valores atómicos e instancias anidadas | Q01/Q02/Q03/Q04 | Visor accesible que conserve toda la evidencia |
| R7: errores sin verdad | `test_external_validation.py` y `test_didactic_corpus.py`: entradas inválidas no invocan al motor; reparaciones calculadas | E01–E11; matriz ampliada de M2-03 | Codec real, controles/servidor y foco/mensajes desde UI |
| Aporte creativo: navegación/comparación | Comparaciones M1 y corpus C01–C03 con parser/validación reales, cambios únicos y base intacta | C01 cambia verdad; C02 cambia testigo sin cambiar verdad; Q03 separa instancias | Navegación gráfica, revisión y observación real de utilidad |
| Defensa individual (30 puntos) | Banco de preguntas y guion preparados; no hay ensayo humano ejecutado | S02/S03, S04, Q03/Q04 y C02 | Enseñanza mutua y defensa aleatoria por los tres |
| Reproducción y entrega | Suite Python y demo del corpus ejecutadas localmente sin paquetes nuevos | `python -X utf8 -B -m examples.corpus` | Arranque gráfico, instalación limpia por el equipo y registro de entornos |
| Coevaluación | No se producen valoraciones de compañeros | Ficha de actividades en defensa-m2.md | Registro humano honesto de aportes, cumplimiento y colaboración |

## Comandos para comprobar la parte disponible

Desde la raíz y con el entorno seleccionado:

```powershell
python -X utf8 -B -m unittest discover -s tests -t . -v
python -X utf8 -B -m examples.corpus
python -X utf8 -B -m examples.corpus --case Q03 --json
python -X utf8 -B -m examples.corpus --case C02 --json
```

La matriz gráfica y sus estados pendientes están en [revision-m3.md](revision-m3.md). Para soluciones y datos exactos usar [casos-didacticos.md](casos-didacticos.md); para el ensayo humano usar [defensa-m2.md](defensa-m2.md). El ticket de competencia fija el techo de la nota y no demuestra cumplimiento de ninguno de estos criterios.
