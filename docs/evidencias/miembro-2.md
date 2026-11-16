# Evidencia consolidada — Miembro 2

## Entorno y evolución de las entregas

Comprobaciones registradas el 15 de noviembre de 2026, con Python 3.11.9 del entorno `.venv`, sobre Windows y en la rama humana `feature/sintaxis-validacion`. Solo se ejecutó M2 en ese intérprete/sistema; la comprobación de sintaxis compatible con 3.10 no equivale a ejecutarlo en 3.10.

| Entrega | Suite completa registrada | Alcance |
| --- | ---: | --- |
| M2-01/02 | 79 pruebas, sin omisiones | Lexer/parser, variables libres e integración de texto con M1 |
| M2-03 | 118 pruebas, sin omisiones | 39 nuevas: normalización por filas, validación integral y bloqueo del motor |
| M2-04, parte ejecutable | 130 pruebas, sin omisiones | 12 nuevas: corpus, evidencia anidada, comparaciones, reparaciones y CLI |

Se conservan las 44 pruebas iniciales de M1 y su oráculo de 900 evaluaciones independientes. Estos resultados no acreditan revisión humana ni una interfaz. Este archivo unifica los tres informes anteriores; la reorganización documental no constituye una nueva ejecución de pruebas.

## Procedimiento reproducible

Desde la raíz de LM_P3:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -X utf8 -B -m examples.sintaxis
.\.venv\Scripts\python.exe -X utf8 -B -m examples.validacion
.\.venv\Scripts\python.exe -X utf8 -B -m examples.corpus
.\.venv\Scripts\python.exe -X utf8 -B -m examples.corpus --case C02 --json
git diff --check
```

Las entregas registraron `git diff --check` sin errores de whitespace y ninguna modificación de `bases/`. La consola requiere UTF-8 para imprimir símbolos lógicos. No se instalaron dependencias ni se hicieron staging, commits, push o cambios de rama por IA.

## Comprobaciones por ticket

| Ticket | Evidencia reproducible y resultado observado |
| --- | --- |
| M2-01 | AST contrastado con árboles manuales: átomos, funciones anidadas, argumentos múltiples, nombres personalizados/Unicode y aridad cero. Se rechazan nombres/aridades inválidos o ambiguos. Las posiciones conservan el texto original |
| M2-02 | Siete símbolos oficiales y alias canónicos, reconocimiento completo de `<->`, precedencia, asociación, alcance mínimo, sombra, variables libres y colisiones de alias. Se comprueban paréntesis, operandos/texto sobrante y posiciones multilínea, fin de entrada y 𝑥 fuera del plano básico |
| Integración de sintaxis | Parser real y servicio evalúan átomos abiertos, términos y cuantificadores. Seis fixtures coinciden con resultados razonados. También se verifican lenguaje personalizado sobre tres elementos y funciones/predicados cero-arios interpretados explícitamente |
| M2-03: interpretación | Dominio no vacío y único; tablas de todos los símbolos; aridad/pertenencia/salida correctas, funciones totales y relaciones no vacías. De los 16 subconjuntos de una tabla funcional binaria sobre dos elementos, solo el completo se acepta |
| M2-03: frontera | Conflictos funcionales/de asignación antes de crear mapas; duplicados idénticos consolidados sin completar entradas faltantes. Formas y elementos no hashables inválidos se diagnostican sin fugas de TypeError de conversión. Los modelos no cambian al editar la fuente |
| M2-03: AST y entorno | Todas las ramas y símbolos, incluso sin uso posterior; variables libres, extras válidos, nombres, alcance, rangos y clases de nodo. Errores independientes agrupados y compatibilidad de código/campo del primero |
| M2-03: bloqueo | Matriz de 18 casos: dos válidos calculados y 16 inválidos sin invocar al evaluador. El servicio usa validate_input y conserva revisión/límites, inyección compatible y certificación de M1 |
| Límites y recuperación | Excesos de texto/tokens, profundidad/nodos, colecciones o pasos fallan sin verdad. Aridad enorme rechazada sin construir D^n; la siguiente petición válida funciona |
| M2-04: corpus | Diez fórmulas coinciden en verdad, variables libres, motivo, elemento decisivo y cobertura. Q01/Q02: testigo norte/contraejemplo sur; Q03/Q04: cobertura 3/3 |
| M2-04: detalle | Q03 conserva testigos centro/sur/norte en distintas instancias del mismo nodo. Q04: V,V,F; V,F,V; F,V,V. S02/S03 distinguen alcance y S04 restaura entorno. Q01 distingue no visitado de falso y Q02 es falso con complete=true |
| M2-04: comparación | C01 cambia solo relevo(centro), Falso→Verdadero; C02 elimina (norte) de Activa y conserva Verdadero con nuevo testigo centro; C03 cambia solo x, Verdadero→Falso. El mundo base queda intacto |
| M2-04: errores y CLI | E01–E11 se rechazan sin motor y sus reparaciones se evalúan verdaderas. Informe JSON calculado y CLI C02 verificada como subproceso. Alterar referencias manuales no cambia la verdad |

Las pruebas de bloqueo con `patch(..., wraps=evaluate)` ejecutan el motor real para entradas válidas/reparadas y comprueban cero invocaciones para inválidas. Las expectativas están en `tests/fixtures/`; el ejecutable no las importa como respuestas. Las demos distinguen Falso válido de No evaluado y no convierten límites/cancelaciones en falsedad.

## Estado de aceptación

La parte Python de M2-01/02/03 y el corpus M2-04 tienen evidencia. Se reutilizan modelos/servicio de M1, sin otro evaluador ni otro tipo de entrada certificada. Contratos en [contratos.md](../contratos.md), gramática en [sintaxis.md](../sintaxis.md), validación en [validacion.md](../validacion.md) y soluciones en [casos-didacticos.md](../casos-didacticos.md).

La inspección registrada encontró solo carpetas preparadas en frontend y `__init__.py` en server. No hay comprobaciones gráficas, capturas, codec HTTP ni conformidad de accesibilidad demostrados. La [matriz general](../matriz-verificacion.md) conserva la revisión pendiente de M3 y su ficha de registro.

Para aceptación global faltan revisión humana M1/M3; contraste independiente de soluciones; codec que preserve filas/rechace claves JSON repetidas; formularios y visor reales; conversión UTF-16 y control de revisiones; enseñanza mutua, defensa, uso con compañeros e instalación limpia completa. No se inventan estas actividades ni aportes humanos. La preparación de defensa queda en la guía de casos.

Plan, backlog y guía individual permanecen fuera del repositorio LM_P3, en su directorio padre. No se movieron automáticamente ni se enviaron mensajes externos.
