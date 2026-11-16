# Validación integral — M2-03

## Alcance y estado

La implementación Python comprueba lenguaje, interpretación, AST completo y entorno antes de evaluar. Las funciones públicas sirven también fuera de HTTP. No calculan verdad ni modifican el contexto. Los errores de entrada se agrupan en una lista de diagnósticos; los límites interrumpen sin resultado lógico.

La integración con el servicio de M1 y la ruta desde filas externas están probadas. La revisión humana de M1/M3, el codec JSON/HTTP y los formularios de M3 siguen pendientes. No se afirma haber probado R7 desde una interfaz aún inexistente. Consultar [evidencia de M2-03](evidencias/miembro-2.md).

## Recorrido que debe usar M3

1. El codec decodifica JSON y comprueba claves/tipos de la petición, revisión de contexto y límites de transporte. Debe detectar claves JSON repetidas durante la decodificación.
2. `build_language` valida declaraciones por filas; no convertirlas primero con `dict(...)`.
3. `build_interpretation` valida las filas funcionales y relaciones antes de construir sus mapas/conjuntos. No puede recuperar conflictos descartados previamente.
4. `build_environment` comprueba las asignaciones por filas antes de convertirlas a diccionario.
5. `evaluate_formula(..., parse=parse)` analiza texto e invoca `validate_input` por defecto. Este revisa todo el contexto y certifica con `prepare_input` de M1. Solo entonces se llama al evaluador real.

El codec puede reunir los errores de las distintas secciones independientes del formulario. Cada builder devuelve todos los diagnósticos de su sección, pero no construye un modelo parcial al fallar. La operación final `collect_errors` reúne errores del contexto completo cuando ya existen modelos normalizados. Una fórmula incompleta impide construir el AST; no se evalúa para poder continuar la validación.

El análisis previo `syntax.parser.analyze` sigue disponible sin interpretación ni entorno para solicitar asignaciones libres; no implica evaluación prematura.

## API y forma de las filas

```python
from lm_p3.application.service import evaluate_formula
from lm_p3.syntax.parser import parse
from lm_p3.validation.normalization import (
    build_environment, build_interpretation, build_language,
)

language = build_language([['f', 1]], [['P', 1]])
domain = ['a', 'b']
interpretation = build_interpretation(
    language, domain,
    function_rows={'f': [[['a'], 'b'], [['b'], 'a']]},
    relations={'P': [['a']]},
)
environment = build_environment(language, domain, [['x', 'a']])
outcome = evaluate_formula('P(f(x))', language, interpretation, environment, parse=parse)
# Resultado real: Falso, porque f(a)=b y (b,) no pertenece a P.
```

Los helpers aceptan listas o tuplas ordenadas de Python; rechazan cadenas, conjuntos y generadores como sustitutos de listas. Las tablas por nombre son `Mapping`. Esto es un contrato de funciones Python, no una decisión de endpoints ni del sobre JSON definitivo.

| Función | Resultado válido | Fallo |
| --- | --- | --- |
| `build_language(functions, predicates)` | `Language` inmutable | `InputValidationError` con todos los errores de declaraciones |
| `build_interpretation(language, domain, function_rows, relations)` | `Interpretation` inmutable | Errores de dominio, símbolos, forma, filas y totalidad |
| `build_environment(language, domain, assignments)` | Diccionario nuevo variable → elemento | Errores de forma, nombre, pertenencia y conflictos |
| `collect_errors(language, interpretation, formula, environment=None, *, limits=None)` | Tupla de `ValidationIssue`; vacía si no hay errores | `EvaluationLimitError` si no puede completar la comprobación |
| `validate_input(...)` | `ValidatedInput` de M1, con contexto/límites intactos | `InputValidationError` o límite; nunca booleano |

Un lenguaje inválido impide construir interpretación/entorno: se deben corregir sus declaraciones primero. Una declaración repetida se rechaza incluso si coincide; los mapas `Language` ya construidos no conservan ese historial.

## Reglas verificadas

- D es una lista/tupla finita ordenada, no vacía, de cadenas únicas y no vacías ni solo espacios. Sus elementos son opacos: no se recortan, normalizan ni convierten silenciosamente. El orden se conserva para trazas deterministas.
- Se interpretan exactamente todos los símbolos declarados, incluidos los que la fórmula no usa. Se rechazan tablas faltantes y tablas de símbolos desconocidos.
- Cada función tiene exactamente una salida en D para cada tupla de D^n. Las entradas tienen aridad correcta y componentes de D. Una función vacía es inválida.
- La totalidad se decide por cardinalidad de claves únicas válidas, sin materializar D^n. Al detectar una omisión se busca un ejemplo entre como máximo `filas+1` candidatos, solo para aridades de hasta 128. Para aridades mayores se emite el diagnóstico sin generar una tupla de ejemplo.
- Las relaciones son no vacías y todas sus tuplas tienen la aridad y pertenencia correctas. Para aridad cero una relación válida contiene `()`, representada como `[[]]` en las filas de Python/JSON.
- Dos filas funcionales con la misma entrada y salida se consolidan. Si difieren en salida se rechazan. Una fila repetida no completa una entrada faltante. Las tuplas relacionales repetidas se consolidan por semántica de conjunto.
- Las asignaciones repetidas con el mismo valor se consolidan; valores diferentes se rechazan. Una variable debe ser un identificador válido no declarado como función/predicado y su valor debe pertenecer a D.
- Todas las variables libres tienen asignación; no se solicita entorno para variables únicamente ligadas. Se conservan asignaciones adicionales válidas, incluso para un nombre ligado en la fórmula, sin contarlas como variables libres. Esto conserva la política de M1.
- Todo el AST se recorre por alcance: tipos de nodo, nombres, clase del símbolo, aridad, conectivos, cuantificadores, variables y rangos. Se visitan ambos operandos y los cuerpos cuantificados aunque luego un testigo o contraejemplo permita detener la evaluación.

## Diagnósticos para la interfaz

`ValidationIssue` es inmutable y contiene `code`, `message` en español, `field`, `span` opcional y `details` inmutables de valores simples. No incluye HTML, estilos ni verdad. `InputValidationError` hereda `SemanticInputError` y conserva la lista en `.errors`; sus atributos `code`, `message` y `field` corresponden al primer diagnóstico para compatibilidad.

`field` es una ruta lógica de la sección/campo. M3 debe mapearla a sus controles, no asumir que es un selector CSS. Índices de filas externas conservan el orden recibido; en modelos relacionales normalizados se usa orden estable de representación para los diagnósticos. Los errores de fórmula incluyen su rango original cuando está disponible y `details.node` para ubicar nodos estructurales; los de aridad incluyen símbolo y cantidades.

Ejemplo serializable por el codec:

```python
def issue_to_dict(issue):
    return {
        'code': issue.code,
        'message': issue.message,
        'field': issue.field,
        'span': None if issue.span is None else {
            'start': issue.span.start, 'end': issue.span.end,
        },
        'details': dict(issue.details),
    }
```

No usar `dataclasses.asdict` directamente sobre mapas protegidos de entrada o `details`. Los rangos son puntos de código Python; la conversión a UTF-16 sigue siendo responsabilidad de M3. Los mensajes se presentan como texto seguro y el resumen debe enlazar a cada campo siguiendo DESIGN.md.

| Código | Ejemplo de campo | Corrección esperada |
| --- | --- | --- |
| `invalid_structure`, `invalid_declaration`, `invalid_function_row` | `functions.f[0]` | Completar la forma de fila/campo indicada |
| `invalid_name`, `invalid_arity`, `duplicate_declaration`, `ambiguous_symbol` | `language.functions[1]` | Corregir nombre/aridad o eliminar una declaración repetida |
| `invalid_domain`, `duplicate_domain` | `domain[1]` | Añadir/corregir elementos distintos de D |
| `missing_interpretation`, `unknown_symbol` | `functions.f` | Interpretar un símbolo declarado o quitar una tabla sobrante |
| `empty_interpretation` | `relations.P` | Añadir al menos una tupla o definir salidas funcionales |
| `invalid_tuple_arity`, `outside_domain` | `functions.f[0].arguments[0]` | Corregir componentes o salida usando D |
| `partial_function`, `conflicting_function_row` | `functions.f[1].output` | Completar una entrada o conservar una sola salida |
| `invalid_variable`, `invalid_assignment`, `conflicting_assignment`, `missing_assignment` | `environment.x` | Corregir nombre/valor o asignar la variable libre |
| `invalid_ast`, `invalid_span`, `arity_mismatch`, `invalid_bound_variable`, `unknown_connective`, `unknown_quantifier` | `formula` | Corregir fórmula o el productor del AST si el fallo es de integración |

## Límites y reproducción

Por operación de validación/normalización se permiten hasta 20 000 entradas acumuladas de colecciones y componentes de tuplas: se cuentan declaraciones, elementos de D, tablas, filas y argumentos. El presupuesto no representa una cantidad de filas faltantes ni un valor de verdad. No se aceptan iterables sin longitud conocida como datos externos.

El AST respeta `EvaluationLimits.max_input_nodes` y `max_depth`; el evaluador conserva su presupuesto de pasos. Un límite produce `EvaluationLimitError`, sin certificado ni verdad parcial. Estos límites no garantizan tiempo máximo de pared ni memoria total: M3 debe limitar el cuerpo HTTP antes de decodificarlo. Un parámetro `limits` con tipo incorrecto es un `TypeError` de uso de la API, no un resultado lógico.

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -X utf8 -B -m examples.validacion
```

`tests/fixtures/validation_cases.json` contiene una base por filas y casos con reemplazos de campos completos (`overrides`), resultado manual esperado o código/campo de error esperado. El test usa builders, parser y servicio reales y comprueba que el evaluador no se invoque en los casos inválidos. Son fixtures de proveedor/consumidor para revisar con M3; no son un codec ni respuestas remotas.
