# Evidencia M2-03 — Validación integral

## Entorno y alcance

Fecha: 15 de noviembre de 2026. Rama humana existente `feature/sintaxis-validacion`; estado limpio al iniciar esta entrega. Python 3.11.9 desde `C:\UVG\logica\LM_P3\.venv\Scripts\python.exe`. Se conservaron las 79 pruebas anteriores. No se instalaron paquetes ni se hicieron staging, commits, push, cambios de rama o cambios en `bases/`.

Implementados `collect_errors`, `validate_input`, builders por filas para lenguaje/interpretación/entorno y diagnósticos inmutables. El servicio existente utiliza `validate_input` por defecto y conserva su protección frente a validadores que sustituyan contexto o límites. La certificación final sigue siendo la fábrica de M1; no se modificó el evaluador ni se creó un segundo tipo de entrada validada.

Contrato y uso para M1/M3: [validacion.md](../validacion.md) y [contratos.md](../contratos.md). La ampliación de contrato se registró antes de implementar los consumidores de esta entrega; no se afirma aprobación humana ni envío de mensajes externos a los compañeros.

## Comprobaciones ejecutadas

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -X utf8 -B -m examples.validacion
.\.venv\Scripts\python.exe -X utf8 -B -m examples.sintaxis
git diff --check
```

| Comprobación | Resultado real |
| --- | --- |
| Suite completa | 118 pruebas pasan, sin omisiones: 79 previas y 39 nuevas |
| Regresión de M1 | Conservadas sus 44 pruebas originales y el oráculo de 900 evaluaciones independientes |
| Dominio y declaraciones | Rechazo de vacíos, duplicados, formas incorrectas, valores no textuales, nombres ambiguos y aridades inválidas |
| Tablas funcionales | Forma/aridad/pertenencia/salida, tablas faltantes o vacías, conflictos antes de crear mapas y funciones parciales |
| Totalidad binaria | Los 16 subconjuntos posibles de las cuatro entradas de D² solo se aceptan cuando están completos |
| Duplicados redundantes | Se consolidan filas funcionales, relaciones y asignaciones idénticas; no completan entradas faltantes |
| Relaciones | No vacías, aridad y pertenencia correctas; soporte de relación cero-aria con tupla vacía |
| Entorno | Asignaciones libres faltantes o inválidas, nombres declarados usados como variables, extras válidos y duplicados contradictorios |
| AST completo | Recorrido de todas las ramas, símbolos, aridades, clases de nodo, rangos, conectivos, cuantificadores y alcance/sombra |
| Errores agrupados | Fallos independientes de tablas, AST y entorno aparecen juntos; se conserva código/campo del primer error para compatibilidad |
| Datos mal formados | Listas, cadenas y elementos no hashables inválidos producen diagnósticos de entrada, sin fugas de TypeError de conversión |
| Límites | Colecciones externas, profundidad/nodos y presupuesto de evaluación fallan sin verdad; aridad enorme rechazada sin generar D^n |
| Matriz externa R7 | Fixture de 18 casos: 2 válidos calculados con motor real y 16 inválidos; en todos los inválidos el motor no se invoca |
| Servicio | Parser real, validador M2 por defecto, certificación M1, revisión/límites preservados e inyección explícita compatible |
| Conservación | Los builders no modifican las filas originales; los modelos resultantes no cambian al editar la fuente |
| Demo de validación | Entrada válida Falso; dos tablas vacías → No evaluado con dos diagnósticos; conflicto funcional → No evaluado con un diagnóstico |
| Demo sintáctica previa | Mantiene cuatro casos cuantificados, átomo abierto y rechazo de aridad inválida |
| Diff | Sin errores de whitespace. Git anuncia conversión futura LF→CRLF en dos archivos según la configuración local; no se cambió esa configuración |

Las pruebas con `patch(..., wraps=evaluate)` ejecutan el evaluador real para entradas válidas y comprueban cero invocaciones para inválidas. Las pruebas específicas de bloqueo reemplazan el punto de llamada solo para afirmar que no se invoca; no presentan resultados simulados como evidencia de evaluación.

Las fixtures son expectativas manuales de prueba, no valores confiados al navegador. El fixture de filas no fija endpoints HTTP ni convierte al codec de M3 en implementación terminada. Esta entrega solo se ejecutó en Python 3.11.9 sobre Windows.

## Criterios y pendientes

La parte Python de M2-03 satisface sus comprobaciones reproducibles de interpretación total/no vacía, AST/entorno completo, errores accionables y bloqueo del motor. Su aceptación global permanece pendiente de revisión de otro integrante y pruebas desde los formularios reales.

M3 debe decodificar JSON rechazando claves repetidas, pasar filas a los builders antes de convertirlas a mapas, mapear los campos de error a controles, presentar el resumen accesible y convertir rangos Unicode a UTF-16. No se crearon servidor, codec ni interfaz en esta entrega. Los límites de cuerpo HTTP y tiempo total siguen siendo trabajo de integración de M3.

M2-04 sigue pendiente: corpus didáctico completo, revisión de UI, enseñanza entre integrantes y defensa conjunta. No se inventaron revisiones, aportes humanos ni resultados de navegador.
