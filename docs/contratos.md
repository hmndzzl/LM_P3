# Contratos comunes entre miembros

## Estado

Documento de coordinación asociado a [estructura.md](estructura.md). **M1 implementó el motor y M2 implementó lexer/parser, variables libres y validación integral**, incluidos builders de filas externas que conservan evidencia de duplicados. El usuario confirmó la notación y la asociatividad el 15 de noviembre de 2026; ver [sintaxis.md](sintaxis.md). La integración Python está probada; ver [validacion.md](validacion.md). El esquema JSON/HTTP y las revisiones humanas siguen pendientes; no hay endpoints implementados.

## Contrato Python inicial implementado por M1

Referencia completa, ejemplos y límites: [semantica.md](semantica.md). Los módulos de modelos estaban vacíos; se añadieron como prerrequisito explícito del motor, sin implementar parser ni interfaz. M2 conserva responsabilidad de modelos de lenguaje/AST/errores y debe revisar esta base antes de producir un contrato distinto. No se considera aprobación del resto del equipo.

- `models.ast`: `Variable(name, span=None)`, `Function(name, arguments=(), span=None)`, `Predicate(name, arguments=(), span=None)`, `Not(operand, span=None)`, `Binary(operator, left, right, span=None)` y `Quantifier(operator, variable, body, span=None)`. Argumentos/hijos inmutables; posiciones `Span(start, end)` en puntos de código Unicode con intervalo [inicio, fin).
- `models.language`: `Language(functions, predicates)` con aridades; `Interpretation(domain, functions, relations)` con D como tupla ordenada de cadenas, funciones como mapas de tuplas a cadenas y relaciones como conjuntos de tuplas. Copias inmutables. El codec debe rechazar duplicados contradictorios antes de construir diccionarios.
- `semantics.inputs.prepare_input(language, interpretation, formula, environment=None, *, limits=None)` devuelve `ValidatedInput` o falla sin verdad. Certifica todos los nodos/tablas y conserva entorno inmutable y variables libres; no analiza texto ni JSON. M2 puede reutilizar esta frontera después de su validación externa.
- `semantics.evaluator.evaluate(request, *, cancelled=None)` devuelve `EvaluationResult(value, trace, steps)`. Los límites/cancelación lanzan excepciones sin resultado parcial.
- `models.trace.Trace`: identificadores estructural/de instancia, fórmula, span, entorno, verdad, motivo, términos/hijos, variable/elemento decisivo, elementos visitados/no visitados y cobertura. Las reglas precisas están en semantica.md.
- `semantics.comparison.compare(base, variant, *, cancelled=None)` devuelve resultados antes/después, un cambio y diferencias de evidencia. Misma fórmula/lenguaje/D; exactamente un dato válido cambiado. No muta entradas ni usa valores cacheados.
- `application.service.evaluate_formula(text, language, interpretation, environment, *, parse, validate=validate_input, revision=0, limits=None, cancelled=None)` devuelve `EvaluationOutcome(revision, evaluation)`. `parse(text, language)` es obligatorio e inyectado; devuelve AST. Desde M2-03 el validador predeterminado es `validation.validator.validate_input`, con la firma de `prepare_input`. El servicio no permite sustituir contexto ni relajar límites silenciosamente.
- `SemanticInputError(code, message, field="")`, `EvaluationLimitError`, `EvaluationCancelledError`: fallos sin atributo de verdad; el servidor decide la traducción HTTP.

Los símbolos ¬, ∧, ∨, →, ↔, ∀ y ∃ y la admisión de aridad cero fueron confirmados por el usuario para esta implementación. No hay igualdad primitiva ni nodo especial de igualdad: puede declararse un predicado binario con nombre, por ejemplo `Igual(x,y)`, cuya interpretación aporta el usuario. La conversión de posiciones a UTF-16 en el navegador sigue a cargo de M3.

## Contrato Python de análisis de M2

- `syntax.lexer.tokenize(text) -> tuple[Token, ...]`: conserva `lexeme` y `Span` originales; `~`, `&`, `|`, `->` y `<->` producen operadores canónicos. Los identificadores se conservan completos; el parser resuelve `v` y `Ax`/`Ex` según contexto y declaraciones.
- `syntax.parser.parse(text, language) -> Formula`: cumple el protocolo `Parser` existente de M1; devuelve exclusivamente el AST compartido. Puede inyectarse con `evaluate_formula(..., parse=parse)`. El servicio usa por defecto el validador integral de M2, que certifica mediante la fábrica defensiva de M1.
- `syntax.parser.analyze(text, language) -> AnalysisResult(formula, free_variables)`: no solicita interpretación ni entorno, no evalúa verdad y permite preparar los selectores de variables libres. M3 todavía debe elegir y construir la operación HTTP que lo exponga.
- `syntax.free_variables.free_variables(formula) -> frozenset[str]`: respeta alcance mínimo, anidamientos y sombra. No modifica el AST ni necesita asignaciones.
- `validation.validator.validate_language(language) -> None`: comprueba nombres identificables, aridades enteras no negativas y ausencia de colisiones función/predicado. No valida todavía tablas externas ni detecta duplicados ya descartados al construir mapas.
- `FormulaSyntaxError(SemanticInputError)`: conserva `code`, `message`, `field="formula"`; añade `span: Span` y `details` inmutables. Los errores de aridad incluyen `symbol`, `expected` y `actual`. El codec debe convertir explícitamente `span` y `dict(error.details)` a JSON; no deducir códigos desde el mensaje. No contiene `value` ni resultado lógico.

La gramática, precedencia, asociatividad, ejemplos y política de colisiones están en [sintaxis.md](sintaxis.md). No se cambiaron las firmas de M1 ni los campos de sus nodos. Esta es una entrega para revisión de los otros miembros, no una afirmación de aprobación por ellos.

### Fixtures de análisis e integración (no son peticiones HTTP)

`tests/fixtures/syntax_cases.json` usa `version: 1`, `language` con mapas `functions`/`predicates`, `interpretation` con `domain`, `function_rows` (listas de pares `[argumentos, salida]`) y `relations` (listas de tuplas), y `cases` con `text`, `environment`, `free_variables`, `value` y `reason` esperados. Son soluciones manuales para probar parser y motor; el test construye los modelos Python. No validan JSON externo ni fijan el futuro codec de M3. `value` es exclusivamente una expectativa de prueba, nunca evidencia confiada al navegador.

### Corpus didáctico M2-04 (formato de ejemplos, versión 1)

`examples/red_estaciones.json` contiene un `world` con `functions`/`predicates` por filas de declaración, `domain`, `function_rows` y `relations`, usando las entradas de los builders de M2. `scenarios` contiene `id`, `title`, `formula`, `assignments` y `manual_reason`. `comparisons` conserva fórmula/entorno base y describe un único `change(kind,symbol,arguments,before,after)`, con su solución manual en prosa. Las expectativas estructuradas de verdad, evidencia y errores se guardan por ID en `tests/fixtures/corpus_expectations.json`, fuera de los ejemplos ejecutables, siguiendo estructura.md. Nunca alimentan el evaluador.

`invalid_base` define fórmula/entorno iniciales; cada registro de `invalid_cases` incluye `overrides` para producir el error y `repair` para corregirlo y su explicación. Los reemplazos de `world` afectan campos completos, sin mezclar silenciosamente tablas parciales. La fixture guarda `expected_error(code,field)` y `fixed_value`; los tests contrastan tanto el rechazo como la reparación real.

`python -X utf8 -B -m examples.corpus` ejecuta los datos por builders, parser, servicio/validador y comparación reales; `--case ID` selecciona un registro y `--json` expone las evidencias calculadas. El informe observado no copia las expectativas manuales. Los consumidores pueden leer los datos con `load_corpus` y reutilizar los casos sin editar código; esto no define un codec HTTP ni afirma que M3 ya importe ejemplos desde la interfaz. La revisión humana de soluciones y UI permanece pendiente.

## Fronteras y responsables

### Entrega M2-03: validación reutilizable (15 de noviembre de 2026)

El contrato Python de validación se amplía sin cambiar `Language`, `Interpretation`, AST ni `ValidatedInput`:

- `validation.validator.collect_errors(language, interpretation, formula, environment=None, *, limits=None)` devuelve una tupla de `ValidationIssue(code, message, field, span=None, details={})`. Revisa declaraciones, todo el AST, todas las tablas y el entorno. No calcula verdad.
- `validation.validator.validate_input(...)` tiene la firma de `prepare_input`: lanza `InputValidationError` con `.errors` o devuelve `ValidatedInput` certificado por la fábrica de M1. El servicio `evaluate_formula` usa este validador por defecto, manteniendo la inyección opcional de un validador compatible y la protección de contexto/límites de M1.
- `validation.normalization.build_language(functions, predicates)` recibe secuencias de pares `[nombre, aridad]`, para detectar declaraciones duplicadas antes de crear mapas. Toda declaración repetida se rechaza, incluso si coincide.
- `build_interpretation(language, domain, function_rows, relations)` recibe D como lista/tupla ordenada, mapas de símbolo a listas de filas funcionales `[argumentos, salida]` o a listas de tuplas relacionales. Comprueba forma, pertenencia, totalidad y duplicados antes de crear `Interpretation`.
- `build_environment(language, domain, assignments)` recibe una lista/tupla de pares `[variable, valor]`. Rechaza valores contradictorios antes de crear el diccionario. La obligación de asignar todas las variables libres se comprueba en `validate_input`, cuando ya está disponible el AST.

Las filas funcionales y asignaciones repetidas con idéntico valor se consolidan; si difieren, se rechazan. Las tuplas relacionales repetidas se consolidan por semántica de conjunto. No cuentan duplicados para completar D^n. Las asignaciones adicionales se conservan si el nombre es una variable válida y su valor pertenece a D; un nombre declarado como función/predicado no es variable. Los elementos de D son cadenas opacas no vacías ni solo espacios; no se convierten ni recortan silenciosamente.

`InputValidationError` hereda `SemanticInputError`: `code`, `message` y `field` corresponden al primer error; `.errors` conserva todos. No contiene booleano. Los límites producen `EvaluationLimitError`, también sin verdad. El codec de M3 convertirá explícitamente campos/rangos/detalles a JSON y debe rechazar claves JSON repetidas durante la decodificación: ningún helper recupera duplicados previamente perdidos en un diccionario.

Estas funciones reciben valores Python y no analizan JSON ni fijan rutas HTTP. M3 deberá revisar la forma de transporte y llamar los helpers antes de construir mapas/modelos por su cuenta. No se afirma que esa revisión ya ocurrió. El detalle de campos, límites y ejemplos se publica en `validacion.md` con la entrega comprobada.

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
4. `analyze` permite pedir asignaciones de variables libres antes de evaluar. Acordar con M3 cómo exponer esta operación mediante HTTP; no exigir un parser en JavaScript.
5. Las funciones internas reciben modelos compartidos; el codec es el único traductor de JSON. El servidor no importa una interfaz CLI ni funciones de ejercicios previos. No devolver HTML desde el motor.
6. Para un existencial falso/universal verdadero, la evidencia debe conservar comprobación de cada elemento. Paginación/colapso de UI no reduce esa obligación. No presentar el orden de recorrido como razón lógica.
7. Versionar la edición no implica almacenar sesiones en el servidor: preferir peticiones autocontenidas y evitar estado global mutable. El entero de revisión no es control de seguridad ni un valor de verdad.

## Entregables de contrato de M1 cerrados a nivel de implementación

Las casillas de esta sección significan implementado y verificado por M1; **no significan revisión ni aprobación de M2/M3**. Las firmas Python son las de los módulos reales enumerados arriba. Cambios posteriores se coordinan con sus consumidores.

- [x] Firma del evaluador: `evaluate(request: ValidatedInput, *, cancelled=None) -> EvaluationResult`; errores de límite/cancelación sin verdad parcial.
- [x] Firma de la frontera normalizada: `prepare_input(language, interpretation, formula, environment=None, *, limits=None) -> ValidatedInput`; copia inmutable, variables libres y comprobación completa previa. No sustituye la validación externa de M2.
- [x] Firma de comparación: `compare(base: ValidatedInput, variant: ValidatedInput, *, cancelled=None) -> ComparisonResult`; exige un cambio válido, contexto fijo y vuelve a calcular ambos resultados.
- [x] Firma del servicio: `evaluate_formula(text, language, interpretation, environment, *, parse, validate=validate_input, revision=0, limits=None, cancelled=None) -> EvaluationOutcome`; los protocolos `Parser` y `Validator` están definidos en `application/service.py`. M2 aporta parser y validador integrales; se conserva la protección de contexto/límites de M1.
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
| Notación confirmada; revisión cruzada pendiente | M2 con el equipo | Confirmación del usuario registrada en sintaxis.md; M1/M3 deben revisar sus consumidores. No se presenta como una verificación independiente de apuntes del curso |
| AST/lenguaje/errores integrados en Python; revisión humana pendiente | M2 con M1 | Se reutilizan los modelos existentes y se añade FormulaSyntaxError compatible. M1 debe revisar el contrato y los ejemplos |
| Posiciones del editor | M2 y M3, consulta a M1 | Convertir puntos de código Unicode de `Span` a unidades UTF-16 cuando corresponda; probar caracteres fuera del plano básico |
| Entrada JSON completa | M3 con M2 | Builders por filas ya disponibles y probados. M3 debe revisar/definir el sobre JSON, mapear campos y detectar claves repetidas al decodificar |
| Revisión humana de M2-03 e integración gráfica | M2 con M1/M3 | Validación externa e integral implementadas y conectadas al protocolo; falta revisión de otro miembro y recorrido R7 desde formularios reales |
| HTTP y errores de transporte | M3 con M1/M2 | Operaciones/rutas mínimas, códigos de estado, forma uniforme de respuesta, límites de petición/tiempo y serialización final; sin CRUD innecesario |
| Revisión de evidencia y codec final | M3 con M1 | Consumir el contrato de salida definido, comprobar explorador/comparación y acordar cualquier cambio antes de implementarlo |
| Casos JSON de entrada y fallos | M2 y M3; M1 verifica resultados | Peticiones reales de verdadero/falso, entorno pendiente, error sintáctico, interpretación inválida y comparación; convertirlos a fixtures de proveedor/consumidor |
| Entorno común y arranque de aplicación | Los tres; M3 integra arranque | Acordar versiones/navegadores y probar aplicación completa desde copia limpia; solo los comandos del motor están comprobados |

La revisión de estos acuerdos sigue siendo parte de H0, aunque M1 ya dispone de una entrega técnica verificable. Cada pendiente se cierra registrando decisión, ejemplo y evidencia real, no solo cambiando una casilla. Ningún agente debe introducir un contrato alternativo sin revisar sus consumidores.
