# Corpus M2-04 — Red de estaciones

## Propósito y reproducción

Este mundo propio permite explicar alcance, funciones, cuantificación y cambios controlados con los mismos datos. Las soluciones de esta guía se razonaron manualmente; las pruebas las contrastan con parser, validador y motor reales. La revisión independiente de esas soluciones por M1 sigue pendiente. No se presentan como observaciones de usuarios ni como pruebas de una interfaz todavía inexistente.

Desde la raíz del repositorio, con el entorno seleccionado:

```powershell
python -X utf8 -B -m examples.corpus
python -X utf8 -B -m examples.corpus --case Q03 --json
python -X utf8 -B -m examples.corpus --case C02
python -X utf8 -B -m examples.corpus --case E03
```

`--case` selecciona cualquiera de los 24 registros sin editar código. `--json` devuelve las evidencias calculadas completas. Los datos de entrada y soluciones en prosa están en [red_estaciones.json](../examples/red_estaciones.json); las expectativas estructuradas están en [la fixture de pruebas](../tests/fixtures/corpus_expectations.json). El ejecutable no importa esa fixture ni toma de ella respuestas.

M3 puede consultar/importar los datos como ejemplos editables mediante el contrato que acuerde para su interfaz; esa importación gráfica no está implementada en esta entrega. Cada carga debe ser explícita y respetar la conservación del trabajo que exige DESIGN.md.

## Mundo e interpretación

D, en orden: **norte, centro, sur**. Los nombres son elementos del dominio; no son constantes del lenguaje.

| Símbolo | Clase | Aridad | Significado didáctico |
| --- | --- | ---: | --- |
| `relevo` | Función | 1 | Estación que recibe el siguiente turno |
| `Activa` | Predicado | 1 | Estación activa |
| `Enlaza` | Predicado | 2 | Enlace dirigido entre estaciones |

| Entrada de relevo | Salida |
| --- | --- |
| norte | centro |
| centro | sur |
| sur | norte |

`Activa = {(norte), (centro)}`. `Enlaza = {(norte,centro), (centro,sur), (sur,norte)}`. La función es total y ambas relaciones son no vacías. La pertenencia de una tupla a Enlaza y el valor de relevo son datos independientes de la interpretación; el lenguaje no impone una equivalencia entre ambos.

## Los cuatro resultados de R6

| Caso | Fórmula | Solución manual y evidencia que se debe observar |
| --- | --- | --- |
| Q01 | `∃x Activa(x)` | Verdadero. Testigo norte; solo se visita norte. centro pertenece a Activa, pero no fue visitada en esta evaluación: «No visitado» no equivale a Falso |
| Q02 | `∀x Activa(x)` | Falso. norte y centro cumplen; sur es contraejemplo. Se recorren 3 de 3 elementos y `complete=true`, aunque la verdad es falsa |
| Q03 | `∀x ∃y Enlaza(x,y)` | Verdadero. Se comprueban las tres asignaciones exteriores con el testigo interior correspondiente |
| Q04 | `∃x (Activa(x) ∧ Activa(relevo(x)) ∧ Activa(relevo(relevo(x))))` | Falso. Ningún inicio del ciclo tiene tres estaciones activas consecutivas; se conservan las tres comprobaciones |

Q03 se resuelve así:

| x exterior | Primer testigo y | y visitados, en orden | Valor de `∃y Enlaza(x,y)` |
| --- | --- | --- | --- |
| norte | centro | norte, centro | Verdadero |
| centro | sur | norte, centro, sur | Verdadero |
| sur | norte | norte | Verdadero |

Esto justifica el universal porque se comprobó cada x. Un testigo interior aislado no basta como razón de toda la fórmula. No se afirma `∃y ∀x Enlaza(x,y)`: ninguna columna de esta relación recibe enlaces de las tres estaciones.

Q04 requiere tres comprobaciones distintas:

| x | x, relevo(x), relevo(relevo(x)) | Valores de Activa | Conjunción |
| --- | --- | --- | --- |
| norte | norte, centro, sur | V, V, F | Falso |
| centro | centro, sur, norte | V, F, V | Falso |
| sur | sur, norte, centro | F, V, V | Falso |

No se usa una relación vacía para obtener este existencial falso. La evidencia completa procede de evaluar cada asignación real.

## Variables, alcance y conectivos

| Caso | Fórmula y entorno | Solución manual |
| --- | --- | --- |
| S01 | `Activa(relevo(x))`, x=centro | Falso: relevo(centro)=sur y sur no está activa. Libre: x |
| S02 | `∃x Activa(x) ∧ ¬Activa(x)`, x=sur | Verdadero. El existencial tiene testigo norte y la negación exterior usa la x libre con valor sur |
| S03 | `∃x (Activa(x) ∧ ¬Activa(x))`, sin entorno | Falso para todos los elementos. Los paréntesis ligan ambas ocurrencias; no hay variables libres |
| S04 | `(∀x (Activa(x) ∨ ∃x ¬Activa(x))) ∧ ¬Activa(x)`, x=sur | Verdadero. Cada existencial interior tiene testigo sur. Al salir de los cuantificadores se conserva la x libre=sur de la negación final |
| S05 | `∀x (Activa(x) → Activa(relevo(x)))` | Falso: en centro aparece V→F. norte se comprueba antes y sur queda sin visitar |
| S06 | `Ax (Activa(x) <-> Activa(relevo(x)))` | Falso: el alias produce `∀x (... ↔ ...)`; en centro difieren V y F |

S02 produce `Binary('∧', Quantifier('∃','x',...), Not(...))`; S03 produce `Quantifier('∃','x',Binary('∧',...))`. Son fórmulas diferentes, por lo que **no** se usan como base/variante del comparador de un único dato. Sirven para enseñar sintaxis y alcance.

En S04, el motor actual evalúa ambos operandos de cada conectivo binario. Los tres existenciales interiores aparecen como instancias distintas de evidencia, aunque algunos operandos izquierdos de la disyunción ya sean verdaderos. La variable exterior no se sobrescribe permanentemente.

## Comparaciones controladas

| Caso | Fórmula y cambio único | Antes → después | Explicación manual |
| --- | --- | --- | --- |
| C01 | `Activa(relevo(x))`, x=centro; cambiar solo relevo(centro): sur→norte | Falso → Verdadero | Cambia el valor del término consultado; la función conserva una salida para cada entrada. Enlaza se conserva |
| C02 | `∃x Activa(x)`; quitar solo (norte) de Activa | Verdadero → Verdadero | La relación conserva (centro). El testigo calculado pasa de norte a centro; cambia la evidencia sin cambiar la verdad |
| C03 | `Activa(x)`; cambiar solo x: centro→sur | Verdadero → Falso | Es una variable libre; lenguaje, dominio y tablas se mantienen |

El comparador real vuelve a calcular ambos escenarios y comprueba que haya exactamente un dato cambiado. Se certifican las dos entradas y la variante no modifica el original. El informe identifica dato previo/nuevo, resultados y diferencias de evidencia. Estas observaciones describen los dos escenarios; no prueban causalidad general para otros cambios o interpretaciones.

C02 es un ejemplo útil del aporte creativo: una etiqueta final por sí sola no permite advertir el reemplazo del testigo. La navegación por subfórmulas y la comparación deben hacer visible qué asignación se consultó y qué evidencia apareció o cambió. La pantalla navegable sigue siendo trabajo de M3.

## Errores y reparaciones del mismo mundo

Todos parten de `Activa(x)` con x=centro, salvo el reemplazo de fórmula indicado. El comando de cada caso primero comprueba el rechazo y después evalúa su reparación. Una salida «Tras corregir: Verdadero» pertenece a la entrada reparada; la entrada inválida no contiene valor de verdad.

| Caso | Cambio que produce el error | Código/campo principal | Reparación comprobada |
| --- | --- | --- | --- |
| E01 | Vaciar D | `invalid_domain`, `domain` | Restaurar norte, centro, sur |
| E02 | Quitar todas las tuplas de Activa | `empty_interpretation`, `relations.Activa` | Restaurar norte y centro |
| E03 | Omitir relevo(sur) | `partial_function`, `functions.relevo` | Añadir salida norte, aunque la fórmula no use la función |
| E04 | Añadir una segunda salida para relevo(centro) | `conflicting_function_row`, `functions.relevo[3].output` | Conservar solo centro→sur |
| E05 | Escribir `Inactiva(x)` sin declarar el símbolo | `unknown_symbol`, `formula` | Usar `Activa(x)` |
| E06 | Escribir `Enlaza(x)` | `arity_mismatch`, `formula` | Usar `Enlaza(x,relevo(x))` |
| E07 | Introducir (norte,este) en Enlaza | `outside_domain`, `relations.Enlaza[0][1]` | Restaurar los enlaces con elementos de D |
| E08 | Quitar la asignación de x | `missing_assignment`, `environment.x` | Asignar centro |
| E09 | Asignar x=este | `invalid_assignment`, `environment[0]` | Elegir centro dentro de D |
| E10 | Escribir `Activa(x` | `missing_parenthesis`, `formula` | Cerrar el paréntesis |
| E11 | Quitar toda la tabla de relevo | `missing_interpretation`, `functions.relevo` | Restaurar la tabla total sin borrar la declaración |

El catálogo más amplio de formas, declaraciones, duplicados y límites está en [validacion.md](validacion.md) y sus pruebas. La revisión gráfica pendiente se registra en la [matriz general](matriz-verificacion.md#revisión-de-la-interfaz-pendiente).

## Preparación de defensa

Material para practicar; no acredita enseñanza ni ensayos humanos. Cada integrante debe explicar los tres módulos. Antes de ejecutar, predecir variables libres, verdad y evidencia y contrastarlas después con el informe calculado.

| Tema | Pregunta | Referencia para responder |
| --- | --- | --- |
| Sintaxis y alcance | ¿Por qué S02 es verdadero y S03 falso? | AST distinto por alcance mínimo; x libre=sur solo en S02. Explicar precedencia, asociación y alias con sintaxis.md |
| Variables y términos | ¿Qué conserva S04? ¿Un elemento de D es una constante? | Cada cuantificador conserva su alcance y se restaura la asignación exterior. Constante requiere función declarada de aridad cero |
| Validación | ¿Por qué E03 bloquea una fórmula sin relevo? | Toda la interpretación debe ser válida. Explicar totalidad por claves únicas de D^n y conflictos perdidos por un dict prematuro |
| Semántica | ¿Por qué Q03/Q04 recorren todo D y Q01 puede parar? | Universal verdadero/existencial falso requieren cobertura completa. Un testigo interior de Q03 no prueba todo el universal |
| Evidencia | ¿No visitado significa Falso? ¿complete significa Verdadero? | Q01 no visita centro aunque está activa; Q02 es falso con complete=true. Distinguir node_id de trace_id en Q03 |
| Aporte e interfaz | ¿Qué enseña C02? ¿Cómo evitar resultados obsoletos? | Cambia el testigo sin cambiar verdad; M3 debe mostrar ambas evidencias y usar revisión de contexto. Observar utilidad con uso real |

Guion: configurar el mundo → Q01/Q02 → abrir asignaciones de Q03 o Q04 → C01/C02 → E03 y reparación. Repartir sintaxis, semántica e interacción entre los tres y ajustar duración a lo confirmado por el docente. Para profundizar, usar S02/S03 y S04, explicar límites sin verdad parcial y distinguir justificación R6 de navegación/comparación creativa.

M1 debe contrastar soluciones, M2 revisar M3 y los tres realizar enseñanza, preguntas aleatorias e instalación limpia. Registrar participantes, fecha real, dudas, correcciones y evidencia después de la actividad. No atribuir sesiones, mejoras de aprendizaje ni aportes de coevaluación no realizados. La defensa vale 30 puntos; el ticket de competencia fija un techo y no garantiza nota.
