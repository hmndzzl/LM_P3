# Motor semántico — entrega de Miembro 1

## Alcance implementado

Evaluación sobre un AST normalizado de términos, predicados, negación, conjunción, disyunción, implicación, bicondicional y cuantificadores. Produce evidencias estructuradas, respeta el alcance de variables y compara dos escenarios válidos que cambian exactamente un dato. Incluye límites de trabajo y cancelación cooperativa sin devolver verdad parcial.

El servicio acepta un parser inyectado. M2 implementó el parser real descrito en [sintaxis.md](sintaxis.md) y la [validación integral/externa](validacion.md), con pruebas de integración; las pruebas originales de la frontera del servicio conservan sus adaptadores explícitos para verificar el protocolo. El codec y la interfaz de M3 ya están conectados; ver [interfaz.md](interfaz.md). No se implementó CYK ni se importan módulos de `bases/`. La semántica es nueva; los árboles heredados se consultaron como referencia conceptual de estructura jerárquica, sin trasladar sus algoritmos ni código al motor.

Se añadieron los modelos mínimos de AST/lenguaje/errores necesarios para ejecutar el motor porque esos módulos estaban vacíos. Son el contrato inicial compartido que M2 debe revisar y reutilizar; no son una implementación de sus tickets de parser o validación de entradas externas. Su procedencia y revisión pendiente constan en [contratos.md](contratos.md).

## Ejecutar y comprobar

Desde la raíz del repositorio con Python 3.10+:

```sh
python -B -m unittest discover -s tests -t . -v
python -B -m examples.semantica
python -B -m examples.semantica --json
python -B -m examples.semantica --benchmark
```

Usar el intérprete compatible del entorno; no confundir el Python 3.9 incluido en algunas instalaciones de macOS con el mínimo del proyecto. No se requieren paquetes externos, servidor ni Internet para estos comandos. La aplicación gráfica se ejecuta con `python -m lm_p3`.

El ejemplo construye un AST directamente y ejecuta el motor real. Los resultados esperados son, respectivamente, ∃ verdadero con testigo a; ∀ falso con contraejemplo b; ∀ de una tautología verdadero con comprobación completa; ∃ de una contradicción falso con comprobación completa. Después cambia f(a) de b a a y P(f(a)) pasa de Falso a Verdadero.

## API Python para M2 y M3

```python
from lm_p3.models.ast import Function, Predicate
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.inputs import prepare_input
from lm_p3.semantics.evaluator import evaluate

language = Language(functions={"a": 0}, predicates={"P": 1})
interpretation = Interpretation(
    domain=("a", "b"),
    functions={"a": {(): "a"}},
    relations={"P": {("a",)}},
)
formula = Predicate("P", (Function("a"),))
request = prepare_input(language, interpretation, formula, {})
result = evaluate(request)
assert result.value is True
```

Los nombres de dominio son cadenas opacas y distintas. Un elemento de D no es automáticamente un símbolo constante: `Function("a")` requiere declarar la función de aridad cero y su tabla. El usuario confirmó ↔ y aridad cero para el parser, junto con el resto de la notación descrita en sintaxis.md. No hay igualdad primitiva ni un nodo de igualdad implementado; se puede declarar un predicado binario con nombre.

### Datos y frontera certificada

- `Language(functions, predicates)` conserva mapas nombre → aridad.
- `Interpretation(domain, functions, relations)` conserva D ordenado, tablas tupla → elemento y conjuntos de tuplas. Copia y protege los mapas anidados/conjuntos.
- `Variable`, `Function`, `Predicate`, `Not`, `Binary`, `Quantifier` son nodos inmutables. `Span(start, end)` es un intervalo semiabierto en puntos de código Unicode de Python; no en bytes ni unidades UTF-16.
- `prepare_input(language, interpretation, formula, environment=None, *, limits=None)` comprueba todo el AST y las tablas antes de crear `ValidatedInput`. Calcula las variables libres necesarias para certificar el entorno. Se aceptan claves adicionales de entorno si sus valores pertenecen a D.
- `evaluate(request, *, cancelled=None)` solo admite `ValidatedInput`; devuelve `EvaluationResult(value, trace, steps)`. El contador mide visitas a nodos de fórmula y términos; no segundos.

La fábrica defensiva `semantics/inputs.py` conserva el sello y las copias inmutables. El validador integral de M2 la reutiliza después de sus comprobaciones; los builders externos detectan forma y duplicados antes de crear modelos. No duplicar estas reglas en handlers ni trasladar la fábrica o crear otra representación sin revisar consumidores.

**Responsabilidad de la frontera externa de M2/M3:** comprobar JSON, forma de colecciones, nombres según la gramática, asignaciones y duplicados contradictorios antes de convertir listas a diccionarios o conjuntos. Un diccionario ya construido no conserva el historial de dos salidas para una misma tupla; el motor no puede recuperar datos descartados por el codec. El soporte normalizado no acredita por sí solo R7 desde la UI.

### Servicio de aplicación

`lm_p3.application.service.evaluate_formula(text, language, interpretation, environment, *, parse, validate=validate_input, revision=0, limits=None, cancelled=None)` encadena parser → validación/certificación → evaluación. `parse(text, language)` debe devolver el AST, o lanzar un error; se inyecta explícitamente `syntax.parser.parse` de M2. Desde M2-03 el valor por defecto de `validate` es `validation.validator.validate_input`, con la firma de `prepare_input`; devuelve el mismo contexto y límites certificados, sin sustituirlos silenciosamente. La salida es `EvaluationOutcome(revision, evaluation)`.

M2 aporta parser, validador y builders reutilizables. M3 traduce los campos de entrada HTTP a esas funciones y la salida/errores a JSON. No usar `dataclasses.asdict()` sobre `ValidatedInput`: contiene mapas protegidos internos, no un contrato de transporte. El resultado/traza y la comparación sí pueden convertirse con `asdict` como demuestra el ejemplo; el codec final deberá acordarse y probarse por M3. El servicio no atrapa fallos inesperados para convertirlos en Falso.

`revision` debe ser un entero no negativo; se devuelve sin cambios. La interfaz es quien incrementa revisión al editar y descarta respuestas obsoletas. El motor no conserva sesiones ni resultados globales.

## Evidencia de evaluación

Cada `Trace` incluye:

| Campo | Significado |
| --- | --- |
| `node_id` | Ubicación estructural en AST: raíz `0`, hijos `.0`/`.1` |
| `trace_id` | Instancia de evaluación; añade `@índice` para cada asignación cuantificada |
| `formula`, `span` | Texto canónico de apoyo y rango original opcional |
| `environment` | Pares ordenados variable/valor de ese alcance; incluye asignaciones externas |
| `value`, `reason` | Verdad real y código estable de la regla aplicada |
| `children` | Evidencias de subfórmulas efectivamente evaluadas |
| `terms` | Valores de términos, origen de variable/función e hijos anidados |
| `variable`, `decisive_element` | Variable cuantificada y testigo/contraejemplo cuando existe |
| `checked_elements`, `unvisited_elements` | Elementos comprobados y pendientes, conservando el orden de D |
| `domain_size`, `complete` | Tamaño del dominio y si ese nodo completó su recorrido |

Los códigos `predicate_member`/`predicate_not_member`, `negation`, `conjunction`, `disjunction`, `implication`, `biconditional`, `existential_witness`, `universal_counterexample`, `universal_complete`, `existential_complete` no son textos finales de interfaz. M3 los convierte a explicaciones españolas usando los datos; no debe inventar un testigo a partir del color o del resultado global.

Una rama cuantificada no visitada no tiene una evidencia falsa: aparece en `unvisited_elements`. Las fórmulas binarias evalúan ambos lados, por lo que todos sus hijos contienen evidencia. Esto facilita inspección y evita representar un cortocircuito como falsedad.

Para ∀ verdadero y ∃ falso, `checked_elements` abarca D completo y hay un hijo por elemento. Para ∃ verdadero o ∀ falso, se detiene al primer elemento decisivo. Si está al final del dominio, `complete` también puede ser verdadero; el código `reason` sigue indicando testigo/contraejemplo.

En un cuantificador anidado, el mismo `node_id` puede aparecer con diferentes `trace_id` y entornos. El visor debe identificar instancias con `trace_id`. El orden de recorrido hace determinista el primer testigo, pero no determina la verdad matemática.

## Comparación de escenarios

`compare(base, variant, *, cancelled=None)` recibe dos `ValidatedInput` y devuelve `ComparisonResult(change, before, after, evidence_changes)`, con propiedad `truth_changed`. Evalúa ambos de nuevo: no recibe valores de verdad del navegador ni utiliza caché.

Las dos entradas deben conservar lenguaje, AST y D con el mismo orden. Exactamente una salida funcional, pertenencia de una tupla a una relación o valor de una variable libre debe cambiar. Las claves del entorno se conservan; cambiar una variable adicional o ligada no se presenta como comparación de variable libre. Cero cambios o varios cambios producen `SemanticInputError`.

`ScenarioChange` informa `kind`, `symbol`, `arguments`, `before`, `after`. `EvidenceChange` enlaza instancias por `trace_id` y conserva evidencia previa/nueva; una puede ser `None` si apareció o dejó de visitarse. Se reportan también ancestros cuyo detalle cambió. Si cambia solo un testigo pero ambos resultados siguen siendo verdaderos, `truth_changed` es falso. Las trazas afectadas describen diferencias observadas, no una prueba de causalidad general.

## Límites y fallos

Valores por defecto: 100 000 visitas de evaluación, 20 000 nodos de entrada y profundidad máxima 128. `EvaluationLimits` permite reducirlos; pasos/nodos pueden ampliarse bajo responsabilidad del llamador, pero la profundidad se limita a 128 para proteger la pila. No hay garantía de tiempo de pared ni límite de memoria total: entradas externas y tablas grandes requieren límites adicionales en servidor/validador.

- `SemanticInputError`: entrada o comparación inválida; ofrece `code`, `message`, `field`, sin verdad.
- `EvaluationLimitError`: tamaño, profundidad o pasos excedidos; sin resultado parcial.
- `EvaluationCancelledError`: el callback `cancelled()` devolvió verdadero en una visita; sin resultado parcial. M3 debe conectar una cancelación real si expone ese botón.
- `TypeError`/`ValueError` de construcción/contrato: uso incorrecto de la API Python; el codec debe rechazar entradas externas antes de construir modelos.

La cancelación es cooperativa durante evaluación, no un mecanismo de terminar hilos ni de interrumpir el parser futuro. El presupuesto no significa que una fórmula incompleta sea Falsa. Cada ejecución tiene estado propio; se verifica reutilización del mismo snapshot desde varios hilos.

## Guía para defensa individual

1. **¿Por qué la función debe ser total?** Cada término debe denotar un elemento de D para cualquier asignación. Tras comprobar que las claves son tuplas distintas de D^n, tener |D|^n entradas válidas prueba totalidad.
2. **¿Cómo funciona un término anidado?** Evaluar sus argumentos primero, formar su tupla y consultar la tabla funcional. La evidencia conserva argumentos y salida.
3. **¿Por qué ∃ verdadero puede parar?** Un elemento que satisface la subfórmula basta. En ∃ falso hay que comprobar todos, igual que para afirmar ∀ verdadero.
4. **¿Cómo se conserva el alcance?** Cada iteración copia el entorno y sustituye solo la variable ligada. Los hermanos y el contexto exterior mantienen su asignación previa.
5. **¿Qué pasa con la implicación?** Solo es falsa cuando el antecedente es verdadero y el consecuente falso; se prueba su tabla completa.
6. **¿Qué añade el aporte creativo?** El motor identifica las instancias de evidencia y permite comparar un cambio válido. La navegación y su diseño corresponden a M3; R6 ya exige la justificación básica.
7. **¿Qué complejidad tiene?** Con k cuantificadores anidados y dominio de n elementos, el peor caso incluye n^k asignaciones, además del trabajo de subfórmulas/términos y de almacenar evidencia. El presupuesto hace explícito el caso no evaluado.
8. **¿Puede una relación vacía ser lógica válida?** En general sí, pero el enunciado del proyecto la prohíbe. Para demostrar ∃ falso se usa una contradicción sobre una relación no vacía.

Practicar manualmente con D={a,b}, P={a}, f intercambiando a/b y R={(a,b)}: resolver ∀x∃y R(x,y); después explicar por qué `∃x P(x) ∧ ¬P(x)` puede ser verdadera con x libre=b bajo el alcance explícito del AST. M2 debe explicar cómo su gramática desambigua ese alcance.

## Pendientes que no se pueden declarar completados todavía

- Obtener revisión humana del contrato con M1/M2/M3 y conectar codec/formularios reales. Parser y validación de M2 ya tienen integración Python comprobada.
- Ejecutar los recorridos H1/H2 y comparación desde la interfaz propia de M3.
- Revisar humanamente el corpus de M2 y la fidelidad de las explicaciones de M3; sus pruebas técnicas no sustituyen esa revisión.
- Obtener revisión humana de otro miembro, enseñanza mutua, ensayo aleatorio y ejecución limpia de la aplicación completa por los tres.

La implementación verificable de M1 se entrega sin commits; la aceptación global de sus tickets conserva esos pendientes de coordinación. Consultar [evidencia ejecutada](evidencias/miembro-1.md).
