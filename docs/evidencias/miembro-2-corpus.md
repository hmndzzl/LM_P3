# Evidencia M2-04 — Corpus y preparación de revisión/defensa

## Entorno y alcance real

Fecha: 15 de noviembre de 2026. Rama existente `feature/sintaxis-validacion`, limpia al iniciar esta entrega. Intérprete del entorno `.venv`: Python 3.11.9 sobre Windows. La línea base fue de 118 pruebas pasando.

Se preparó el mundo propio Red de estaciones, con datos completos por filas, soluciones razonadas, ejecutable de casos, expectativas de prueba separadas y guías para el equipo. No se cambiaron el motor, parser, validador, servicio ni sus contratos de evaluación. La única ampliación de contratos documenta el formato de ejemplos antes de sus consumidores. No se modificaron `bases/`, frontend ni servidor.

La UI aún no existe: la inspección de `frontend/` encontró carpetas preparadas con `.gitkeep`; `lm_p3/server/` solo contiene `__init__.py`. No se ejecutaron pruebas gráficas ni se produjeron capturas o una aprobación visual ficticia.

## Comprobaciones ejecutadas

Desde `C:\UVG\logica\LM_P3`:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -t .
.\.venv\Scripts\python.exe -X utf8 -B -m examples.corpus
.\.venv\Scripts\python.exe -X utf8 -B -m examples.corpus --case C02
git diff --check
```

| Comprobación | Resultado observado |
| --- | --- |
| Suite completa | 130 pruebas pasan, sin omisiones: 118 previas y 12 nuevas |
| Datos válidos | Dominio ordenado norte/centro/sur, función total relevo y relaciones Activa/Enlaza no vacías pasan los builders y la validación reales |
| Soluciones de 10 fórmulas | Coinciden verdad, variables libres, motivo, elemento decisivo y cobertura con las expectativas razonadas |
| Cuatro resultados cuantificados | Q01 verdadero con testigo norte; Q02 falso con contraejemplo sur; Q03 verdadero con cobertura 3/3; Q04 falso con cobertura 3/3 |
| Evidencia anidada Q03 | Testigos interiores centro, sur, norte para x=norte,centro,sur; tres instancias distintas del mismo nodo sintáctico |
| Comprobación Q04 | Valores atómicos V,V,F; V,F,V; F,V,V, conservando los tres cuerpos falsos |
| Alcance/sombra | S02 verdadero con x libre=sur; S03 cerrado y falso; S04 conserva entorno externo tras cuantificadores que reutilizan x |
| Visitado frente a verdad | Q01 conserva centro/sur como no visitados; Q02 es falso aunque su nodo tenga complete=true |
| Comparación funcional C01 | Solo relevo(centro) cambia sur→norte; verdad Falso→Verdadero |
| Comparación relacional C02 | Solo se elimina (norte) de Activa; verdad Verdadero→Verdadero y testigo norte→centro; aparece nueva evidencia visitada |
| Comparación de entorno C03 | Solo x cambia centro→sur; verdad Verdadero→Falso |
| Base intacta | Ejecutar escenarios/comparaciones/informes no modifica los datos de fuente |
| Once errores y sus reparaciones | Cada caso E01–E11 falla con código/campo previsto y no invoca al motor. Tras aplicar su reparación específica, se ejecuta una evaluación verdadera real |
| Independencia de referencias | Alterar la prosa manual y añadir una expectativa falsa a un caso no cambia su resultado; las expectativas estructuradas están en tests/fixtures y no son importadas por el ejecutable |
| Salida JSON | Informe completo serializable con 10 evaluaciones, 3 comparaciones y 11 errores; los errores no tienen valor de verdad propio y el resultado reparado se presenta por separado |
| CLI seleccionada | Una prueba ejecuta `--case C02 --json` como subproceso con el intérprete real y contrasta los testigos del JSON calculado |

Los resultados proceden de builders, parser, validador, servicio y comparador reales. En las pruebas de errores, `patch(..., wraps=evaluate)` conserva la evaluación real para la reparación y permite comprobar que no se llamó al motor antes. No se simulan valores de verdad.

Esta entrega se ejecutó solamente en Python 3.11.9 sobre Windows. Las 44 pruebas iniciales de M1 y su oráculo de 900 evaluaciones siguen dentro de la suite; no se repitieron ni se atribuyeron como una revisión humana del corpus nuevo.

## Materiales preparados

- [Casos didácticos](../casos-didacticos.md): mundo, soluciones, testigos, contraejemplos, tablas de comprobación, comparación y correcciones.
- [Defensa](../defensa-m2.md): 24 preguntas con respuestas de referencia, guion de primera ronda/final y propuesta de enseñanza mutua.
- [Ficha de revisión M3](../revision-m3.md): matriz R7, editor, estados, Unicode, evidencia, accesibilidad y registro de observaciones; toda ejecución gráfica sigue pendiente.
- [Matriz de verificación](../matriz-verificacion.md): requisito → prueba Python → demostración → pendiente de producto/humano.
- Actualizados README, estructura y formato del corpus en contratos; también plan/backlog/guía individual en `C:\UVG\logica`, fuera del repositorio `LM_P3` en esta copia.

## Aceptación pendiente

M2-04 **no está globalmente cerrado**. Está preparada y comprobada la parte de corpus/integración Python, junto con materiales de revisión y defensa. Faltan:

1. M1 contrasta independientemente las soluciones y revisa la entrega de M2.
2. M3 ejecuta/importa los ejemplos mediante su pantalla real y M2 revisa los controles y errores de esa interfaz, registrando fallos y correcciones.
3. Los tres realizan enseñanza mutua, defensa aleatoria e instalación limpia de la aplicación completa.
4. Se observa el valor pedagógico con uso real y se registran aportes/revisiones humanos sin inventarlos.

No se instalaron dependencias ni se hicieron staging, commits, push o publicaciones remotas. Tampoco se enviaron mensajes externos. Los tickets del backlog conservan sus casillas de aceptación pendientes.
