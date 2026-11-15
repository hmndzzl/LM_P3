# Contratos comunes entre miembros

## Estado

Documento inicial de coordinación asociado a [estructura.md](estructura.md). Las responsabilidades y dirección de dependencias están definidas. **M1 implementó el contrato Python mínimo descrito abajo para hacer verificable su motor**. Su revisión con M2/M3 y el esquema de transporte JSON siguen pendientes antes de integrar consumidores. No hay endpoints ni notación del curso confirmados por esta implementación.

## Contrato Python inicial implementado por M1

Referencia completa, ejemplos y límites: [semantica.md](semantica.md). Los módulos de modelos estaban vacíos; se añadieron como prerrequisito explícito del motor, sin implementar parser ni interfaz. M2 conserva responsabilidad de modelos de lenguaje/AST/errores y debe revisar esta base antes de producir un contrato distinto. No se considera aprobación del resto del equipo.

- `models.ast`: `Variable(name, span=None)`, `Function(name, arguments=(), span=None)`, `Predicate(name, arguments=(), span=None)`, `Not(operand, span=None)`, `Binary(operator, left, right, span=None)` y `Quantifier(operator, variable, body, span=None)`. Argumentos/hijos inmutables; posiciones `Span(start, end)` en puntos de código Unicode con intervalo [inicio, fin).
- `models.language`: `Language(functions, predicates)` con aridades; `Interpretation(domain, functions, relations)` con D como tupla ordenada de cadenas, funciones como mapas de tuplas a cadenas y relaciones como conjuntos de tuplas. Copias inmutables. El codec debe rechazar duplicados contradictorios antes de construir diccionarios.
- `semantics.inputs.prepare_input(language, interpretation, formula, environment=None, *, limits=None)` devuelve `ValidatedInput` o falla sin verdad. Certifica todos los nodos/tablas y conserva entorno inmutable y variables libres; no analiza texto ni JSON. M2 puede reutilizar esta frontera después de su validación externa.
- `semantics.evaluator.evaluate(request, *, cancelled=None)` devuelve `EvaluationResult(value, trace, steps)`. Los límites/cancelación lanzan excepciones sin resultado parcial.
- `models.trace.Trace`: identificadores estructural/de instancia, fórmula, span, entorno, verdad, motivo, términos/hijos, variable/elemento decisivo, elementos visitados/no visitados y cobertura. Las reglas precisas están en semantica.md.
- `semantics.comparison.compare(base, variant, *, cancelled=None)` devuelve resultados antes/después, un cambio y diferencias de evidencia. Misma fórmula/lenguaje/D; exactamente un dato válido cambiado. No muta entradas ni usa valores cacheados.
- `application.service.evaluate_formula(text, language, interpretation, environment, *, parse, validate=prepare_input, revision=0, limits=None, cancelled=None)` devuelve `EvaluationOutcome(revision, evaluation)`. `parse(text, language)` es obligatorio e inyectado; devuelve AST. `validate` tiene la firma de `prepare_input`. El servicio no permite sustituir contexto ni relajar límites silenciosamente.
- `SemanticInputError(code, message, field="")`, `EvaluationLimitError`, `EvaluationCancelledError`: fallos sin atributo de verdad; el servidor decide la traducción HTTP.

El motor soporta ¬, ∧, ∨, →, ↔, ∀ y ∃ y símbolos de aridad cero; esto declara capacidades implementadas, no el catálogo que el docente exige al parser. La igualdad no está implementada. Las convenciones de sintaxis textual, nombres y posiciones UTF-16 en navegador necesitan revisión por M2/M3.

## Fronteras y responsables

| Frontera | Proveedor | Consumidor | Qué acordar y probar |
| --- | --- | --- | --- |
| Lenguaje/interpretación | M2 en `models/language.py` | M1, M2, codec de M3 | Nombres y aridades, orden estable de D, tablas totales y relaciones no vacías |
| Análisis de fórmula | M2 en `syntax/` | Servicio/M1 y UI a través del servidor | AST, variables libres, posiciones, error sintáctico; preservar lexemas |
| Entrada validada | M2 en `validation/` | M1 en `semantics/` | Marca/tipo de entrada válida, entorno completo y ausencia de errores |
| Evaluación/traza | M1 en `semantics/` y `models/trace.py` | Servicio y codec/UI de M3 | Booleano, entorno, subfórmula, motivo, hijos, cobertura, visitado y evidencia decisiva |
| Caso de uso completo | M1 en `application/service.py`, junto a M2 | Servidor M3 | Analizar, validar y luego evaluar, sin valor de verdad en fallos |
| JSON/HTTP | M3 en `server/codec.py` y `server/http.py` | Frontend M3; pruebas cruzadas | Forma de petición, rutas, códigos de error y versión de contexto; sin modelos arbitrarios expuestos |
| Comparación P1 | M1 en `semantics/comparison.py` | Servicio y UI M3 | Base inmutable, variante de un cambio válido y evidencia de ambas |

## Reglas ya fijadas

1. La petición lleva lenguaje, interpretación, texto de fórmula, entorno y revisión del contexto; el servidor devuelve esa revisión para que la UI descarte respuestas obsoletas. No aceptar AST/traza aportados por el navegador como evidencia calculada.
2. El resultado válido contiene un booleano y una traza estructurada. Entradas inválidas, error interno y límites no incluyen un booleano que la UI pueda confundir con verdad. Un resultado Falso válido no es error HTTP.
3. Usar una estructura consistente de errores con código estable, mensaje en español y campo/rango cuando corresponda. La UI no deduce tipos de error analizando texto libre. Rechazar errores de JSON/tipos en frontera y errores lógicos mediante validación integral.
4. El análisis debe permitir pedir asignaciones de variables libres antes de evaluar. Acordar si hay una operación separada de análisis o respuesta intermedia; no exigir a M3 un parser completo en JavaScript.
5. Las funciones internas reciben modelos compartidos; el codec es el único traductor de JSON. El servidor no importa una interfaz CLI ni funciones de ejercicios previos. No devolver HTML desde el motor.
6. Para un existencial falso/universal verdadero, la evidencia debe conservar comprobación de cada elemento. Paginación/colapso de UI no reduce esa obligación. No presentar el orden de recorrido como razón lógica.
7. Versionar la edición no implica almacenar sesiones en el servidor: preferir peticiones autocontenidas y evitar estado global mutable. El entero de revisión no es control de seguridad ni un valor de verdad.

## Entregables de contrato de M1 cerrados a nivel de implementación

Las casillas de esta sección significan implementado y verificado por M1; **no significan revisión ni aprobación de M2/M3**. Las firmas Python son las de los módulos reales enumerados arriba. Cambios posteriores se coordinan con sus consumidores.

- [x] Firma del evaluador: `evaluate(request: ValidatedInput, *, cancelled=None) -> EvaluationResult`; errores de límite/cancelación sin verdad parcial.
- [x] Firma de la frontera normalizada: `prepare_input(language, interpretation, formula, environment=None, *, limits=None) -> ValidatedInput`; copia inmutable, variables libres y comprobación completa previa. No sustituye la validación externa de M2.
- [x] Firma de comparación: `compare(base: ValidatedInput, variant: ValidatedInput, *, cancelled=None) -> ComparisonResult`; exige un cambio válido, contexto fijo y vuelve a calcular ambos resultados.
- [x] Firma del servicio: `evaluate_formula(text, language, interpretation, environment, *, parse, validate=prepare_input, revision=0, limits=None, cancelled=None) -> EvaluationOutcome`; los protocolos `Parser` y `Validator` están definidos en `application/service.py`. El parser real todavía no existe.
- [x] Errores del motor definidos: `SemanticInputError(code, message, field)`, `EvaluationLimitError` y `EvaluationCancelledError`; no contienen resultado lógico. Los errores inesperados no se convierten en Falso.
- [x] Modelo de evidencia definido y probado: `TermTrace`, `Trace` y `EvaluationResult`; identificadores, entorno, motivos, cobertura y elementos no visitados descritos abajo.
- [x] Modelo de comparación definido y probado: `ScenarioChange`, `EvidenceChange` y `ComparisonResult`; se distingue cambio de testigo de cambio de verdad.
- [x] Ejemplos de salida ejecutados y serializables: [miembro-1-demo.json](evidencias/miembro-1-demo.json) contiene los cuatro casos cuantificados y una comparación funcional válida. No son peticiones HTTP ni casos del parser ausente.
- [x] Límites iniciales implementados: 100 000 visitas, 20 000 nodos de entrada y profundidad máxima 128; pruebas de presupuesto/cancelación y [mediciones registradas](evidencias/miembro-1.md).
- [x] Comandos de pruebas y demo comprobados con Python 3.11.12 y Python 3.14, sin dependencias externas. El mínimo declarado sigue siendo 3.10; se verificó su sintaxis, no su ejecución en un intérprete 3.10.

### Campos de salida precisos para los consumidores

| Tipo | Campos implementados |
| --- | --- |
| `TermTrace` | `term: str`, `value: str`, `reason: str`, `children: tuple[TermTrace, ...]` |
| `Trace` | `node_id: str`, `trace_id: str`, `formula: str`, `span: Span o None`, `environment: tuple de pares (nombre, valor)`, `value: bool`, `reason: str`, `children: tuple[Trace, ...]`, `terms: tuple[TermTrace, ...]`, `variable: str o None`, `decisive_element: str o None`, `checked_elements: tuple[str, ...]`, `unvisited_elements: tuple[str, ...]`, `domain_size: int o None`, `complete: bool` |
| `EvaluationResult` | `value: bool`, `trace: Trace`, `steps: int` |
| `EvaluationOutcome` | `revision: int`, `evaluation: EvaluationResult` |
| `ScenarioChange` | `kind: function/relation/assignment`, `symbol: str`, `arguments: tuple[str, ...]`, `before: str o bool`, `after: str o bool` |
| `EvidenceChange` | `trace_id: str`, `before: Trace o None`, `after: Trace o None` |
| `ComparisonResult` | `change: ScenarioChange`, `before: EvaluationResult`, `after: EvaluationResult`, `evidence_changes: tuple[EvidenceChange, ...]`; propiedad calculada `truth_changed: bool` |

`dataclasses.asdict(result)` convierte los campos de resultado a datos serializables, pero **no incluye propiedades calculadas**. Si M3 necesita `truth_changed` en JSON, debe añadirlo explícitamente, como hace el ejemplo ejecutable. El ejemplo convierte tuplas a arrays mediante JSON; el codec definitivo de transporte aún requiere acuerdo con M3. No serializar `ValidatedInput` de esa manera: sus mapas protegidos pertenecen al contrato interno.

`node_id` identifica una posición del AST (`0`, `.0`, `.1`); `trace_id` añade instancias de cuantificación (`@índice`). Solo los hijos realmente evaluados tienen `Trace`; los elementos pendientes se listan en `unvisited_elements` y nunca se etiquetan como falsos. Para ∀ verdadero/∃ falso, hay comprobación de todo D. Los conectivos binarios evalúan ambos operandos. `complete` se refiere a la cobertura de ese nodo, no al cumplimiento global de los requisitos.

Códigos de `Trace.reason`: `predicate_member`, `predicate_not_member`, `negation`, `conjunction`, `disjunction`, `implication`, `biconditional`, `universal_complete`, `universal_counterexample`, `existential_witness`, `existential_complete`. En términos: `variable_assignment` y `function_lookup`. M3 debe traducirlos a español con sus datos, sin usar esos códigos como texto final para el usuario.

## Pendientes compartidos de H0 e integración

Estos puntos siguen abiertos; no se cierran por tener el motor probado.

| Pendiente | Responsable de cierre | Qué falta concretamente |
| --- | --- | --- |
| Catálogo del curso y sintaxis textual | M2 con el equipo/docente | Conectivos exigidos, precedencia, asociatividad, alcance, igualdad, aridad cero y política de nombres; separar capacidades del motor de requisitos del curso |
| Revisión del AST/lenguaje/errores iniciales | M2 con M1 | Revisar los modelos ya implementados, conectar el parser y evitar representaciones incompatibles |
| Posiciones del editor | M2 y M3, consulta a M1 | Convertir puntos de código Unicode de `Span` a unidades UTF-16 cuando corresponda; probar caracteres fuera del plano básico |
| Entrada JSON completa | M3 con M2 | Forma de D, tablas y entorno, nombres de campos, tuplas n-arias y rechazo de duplicados antes de construir mapas |
| Parser, variables libres y validador externos | M2 con M1 | Implementar parser/análisis previo al entorno y adaptar el validador al protocolo; el cálculo defensivo interno no completa esos módulos |
| HTTP y errores de transporte | M3 con M1/M2 | Operaciones/rutas mínimas, códigos de estado, forma uniforme de respuesta, límites de petición/tiempo y serialización final; sin CRUD innecesario |
| Revisión de evidencia y codec final | M3 con M1 | Consumir el contrato de salida definido, comprobar explorador/comparación y acordar cualquier cambio antes de implementarlo |
| Casos JSON de entrada y fallos | M2 y M3; M1 verifica resultados | Peticiones reales de verdadero/falso, entorno pendiente, error sintáctico, interpretación inválida y comparación; convertirlos a fixtures de proveedor/consumidor |
| Entorno común y arranque de aplicación | Los tres; M3 integra arranque | Acordar versiones/navegadores y probar aplicación completa desde copia limpia; solo los comandos del motor están comprobados |

La revisión de estos acuerdos sigue siendo parte de H0, aunque M1 ya dispone de una entrega técnica verificable. Cada pendiente se cierra registrando decisión, ejemplo y evidencia real, no solo cambiando una casilla. Ningún agente debe introducir un contrato alternativo sin revisar sus consumidores.
