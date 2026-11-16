# Sintaxis textual — entrega de M2

## Acuerdos y alcance

Se confirmó el 15 de noviembre de 2026 los símbolos oficiales `¬ ∧ ∨ → ↔ ∀ ∃`, sus alias de teclado, precedencia, alcance mínimo y ausencia de igualdad primitiva. En una aclaración posterior se confirmó implicación asociativa a la derecha, los demás binarios a la izquierda y admisión de funciones/predicados de aridad cero. Esta procedencia no se sustituye por una afirmación de consulta independiente al docente.

M2-01/02 tienen implementación y pruebas Python; su aceptación global conserva revisión humana pendiente; la integración gráfica está documentada en interfaz.md. M2-03 también está implementado: ver [validacion.md](validacion.md). El servicio usa su validador integral y certifica con la fábrica defensiva de M1. Los modelos de lenguaje, interpretación y AST se conservan; no se implementó un segundo motor ni un codec HTTP.

## Operadores y gramática

| Símbolo almacenado en el AST | Alias de entrada | Precedencia (mayor primero) | Asociación |
| --- | --- | --- | --- |
| `¬` | `~` | 5 | Prefijo |
| `∀`, `∃` | `Ax`, `Ex` para variable x | 5 | Prefijo, alcance inmediato |
| `∧` | `&` | 4 | Izquierda |
| `∨` | `\|`, `v` en posición infija | 3 | Izquierda |
| `→` | `->` | 2 | Derecha |
| `↔` | `<->` | 1 | Izquierda |

Los alias se admiten al escribir; el AST contiene operadores Unicode. Los botones de M3 deben insertar los símbolos oficiales. No se aceptan comandos LaTeX como `\neg` o `\forall` como alias adicionales.

Gramática canónica; los alias se interpretan en las posiciones equivalentes:

```ebnf
formula       = biconditional ;
biconditional = implication, { "↔", implication } ;
implication   = disjunction, [ "→", implication ] ;
disjunction   = conjunction, { "∨", conjunction } ;
conjunction   = unary, { "∧", unary } ;
unary         = "¬", unary | quantifier, variable, unary
              | "(", formula, ")" | atom ;
quantifier    = "∀" | "∃" ;
atom          = predicate, [ "(", [ arguments ], ")" ] ;
term          = variable | function, [ "(", [ arguments ], ")" ] ;
arguments     = term, { ",", term } ;
```

Las producciones de argumentos se comprueban contra `Language`: omitir paréntesis solo es válido para símbolos de aridad cero. Tanto `P(c)` como `P(c())` son válidos si c es una función de aridad cero y P es un predicado unario. Un predicado cero-ario se escribe `T` o `T()`. No admite argumentos. La interpretación de cada símbolo debe cumplir las reglas del proyecto, también con aridad cero: una relación cero-aria no vacía contiene la tupla vacía.

`P(x) → Q(x) → R(x)` significa `P(x) → (Q(x) → R(x))`. En cambio, `P(x) ↔ Q(x) ↔ R(x)` agrupa primero los dos operandos de la izquierda.

`∀x P(x) ∧ Q(x)` produce `Binary('∧', Quantifier('∀','x',P(x)), Q(x))`: la x de Q sigue libre. `∀x (P(x) ∧ Q(x))` liga ambas ocurrencias. Un cuantificador puede preceder otro cuantificador o negación sin paréntesis adicionales; su cuerpo inmediato es esa subfórmula prefija.

## Nombres, variables y colisiones de alias

- Identificadores Unicode válidos según `str.isidentifier()`: letra o guion bajo inicial y continuaciones válidas, incluidos dígitos. No se admiten espacios, comas, paréntesis ni operadores dentro de nombres. Se conservan grafía, mayúsculas/minúsculas y posiciones originales; no se normaliza Unicode silenciosamente.
- `Language` determina cuáles nombres son funciones o predicados. No pueden ser ambos. Sus aridades son enteros no negativos; `True` no es una aridad.
- Un identificador no declarado es una variable en posición de término. `P(persona)` usa la variable persona si no está declarada. `P(noDeclarada(x))` falla: una variable no puede aplicarse como función. Una variable tampoco puede ocupar por sí sola el lugar de una fórmula.
- Los nombres declarados tienen prioridad sobre los alias alfabéticos. Si se declara `Ax` como predicado, `Ax(x)` lo invoca. Para cuantificar se usa `∀x P(x)` o un alias que no colisione. Los nombres de variables ligadas no pueden ser símbolos declarados.
- `v` es disyunción solamente entre fórmulas y si no es un símbolo declarado. En `P(v)` es una variable. Si se declara v, utilizar `∨` o `|` para disyunción.
- En posición inicial de subfórmula, un identificador no declarado formado por `A` o `E` seguido de otro identificador representa el cuantificador y esa variable completa: `Ax P(x)`, `Ex(P(x))`, `Apersona P(persona)`. Se necesita un límite de identificador antes del cuerpo: `AxP(x)` no significa `Ax P(x)`. Dentro de argumentos, el identificador `Ax` conserva su significado de nombre o variable.
- Un elemento `a` de D no se vuelve una constante automáticamente. `P(a)` usa la variable a si no hay una función cero-aria declarada con ese nombre; requerirá entorno. Para una constante hay que declarar e interpretar esa función.
- `=` se rechaza con código `unsupported_equality`. Una relación de igualdad se puede representar con un predicado binario con nombre, como `Igual(x,y)`. El programa no fuerza propiedades de igualdad sobre esa relación ni convierte la puntuación `=` en identificador.

## API, posiciones y errores

```python
from lm_p3.syntax.parser import analyze, parse
from lm_p3.application.service import evaluate_formula

analysis = analyze("∀x P(x) ∧ Q(x)", language)
# analysis.formula es el AST compartido; analysis.free_variables == frozenset({'x'}).
outcome = evaluate_formula(text, language, interpretation, environment, parse=parse)
```

`analyze` no necesita interpretación ni entorno. La UI puede ordenar `free_variables` para presentar selectores estables. No contiene ni anticipa valor de verdad. El ejemplo ejecutable completo está en `examples/sintaxis.py`.

Cada nodo analizado tiene `Span(start,end)` semiabierto en puntos de código del texto original. Una subfórmula entre paréntesis incluye los delimitadores en el rango de su nodo raíz. Los hijos conservan sus rangos propios. Los alias de varios caracteres ocupan su extensión original, aunque el operador del AST sea de un carácter.

M3 debe convertir a UTF-16 antes de seleccionar texto en el navegador; por ejemplo la variable matemática 𝑥 ocupa un punto de código Python y dos unidades UTF-16. La conversión no está implementada por este módulo. Un error al final del texto puede tener intervalo vacío `[len(text),len(text))`, adecuado para indicar dónde falta entrada.

`FormulaSyntaxError` conserva el contrato de `SemanticInputError` y añade `span` y `details`. Códigos: `invalid_character`, `unsupported_equality`, `empty_formula`, `expected_formula`, `expected_variable`, `invalid_bound_variable`, `expected_predicate`, `unknown_symbol`, `predicate_as_term`, `expected_term`, `arity_mismatch`, `missing_parenthesis` y `unexpected_token`. La validación de lenguaje usa `invalid_name`, `invalid_arity` y `ambiguous_symbol` con campo de lenguaje. No devuelven HTML ni valor de verdad.

## Límites y comprobación

Límites internos iniciales: 100 000 puntos de código de entrada, 20 000 tokens antes del token final, 128 niveles de análisis y 20 000 nodos/128 niveles de AST. Los paréntesis redundantes también consumen profundidad de análisis. Un exceso produce `EvaluationLimitError`, sin resultado lógico. Son límites técnicos del módulo, no requisitos del docente ni garantía de tiempo total. El servidor deberá limitar también cuerpos HTTP e interpretaciones.

Desde la raíz del repositorio, con el entorno de Python seleccionado:

```powershell
python -X utf8 -B -m unittest discover -s tests -t . -v
python -X utf8 -B -m examples.sintaxis
```

Las pruebas comparan AST con árboles manuales, cubren operadores/alias, precedencia/asociatividad, nombres propios, aridad cero, posiciones Unicode, alcance/sombra, errores y límites. La integración usa parser y motor reales, pasando por `validate_input` de M2 y la certificación de M1. Las pruebas de filas externas de M2-03 se describen en validacion.md; la UI está implementada y verificada por M3; su revisión humana sigue pendiente. Las fixtures se describen en [contratos.md](contratos.md).
