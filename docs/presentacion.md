# Presentación y defensa del evaluador semántico

La demo debe mostrar que los resultados dependen de datos editables, explicar la
evidencia y rechazar entradas incorrectas. El aporte creativo se defiende mejor
comparando dos ejecuciones que enseñarían la misma etiqueta final, pero distintos
testigos o términos evaluados.

Fuente oficial: **MM3032 - Proyecto.pdf**, revisado completo: requisitos en la
página 1; puntuación, presentación, coevaluación y competencia en la página 2.

## Qué permite aspirar al 100

| Componente de la rúbrica | Puntos | Evidencia que debe presentar el equipo |
| --- | ---: | --- |
| Evaluación semántica y justificación | 30 | Los cuatro casos cuantificados, valores de términos y razonamiento del caso integrado |
| Análisis sintáctico | 10 | Fórmulas nuevas, conectivos, variables libres, alcance, errores y reparación |
| Interfaz gráfica | 10 | Configuración completa sin tocar código, teclado, edición, resultados y errores claros |
| Defensa individual | 30 | Cada integrante puede explicar cualquier módulo y seguir una ejecución real |
| Creatividad y originalidad | 5 | Explicar la navegación enlazada y los cambios sugeridos desde la evidencia |
| Valor del aporte | 6 | Mostrar un cambio de testigo o de término que una etiqueta Verdadero/Falso no revela |
| Calidad de implementación | 6 | Comparación real, base conservada, validación y descarte de respuestas obsoletas |
| Justificación y defensa del aporte | 3 | Explicar su utilidad y los invariantes de una comparación de un solo dato |

La guía fija máximos de **80 sin ticket, 90 con plata y 100 con oro**. En la
primera ronda avanzan los cinco equipos más votados; la final reinicia el conteo
y los dos más votados reciben oro; los otros tres conservan plata. Cada estudiante
vota por otro equipo. Pesos del voto: estudiante 1, auxiliar 2 y
docente 3. El ticket establece un máximo: también deben cumplirse los criterios.
Las duraciones de los recorridos siguientes son ajustables; el PDF no fija un
tiempo de exposición.

## Recorrido principal

Antes de cada evaluación, decir qué resultado y evidencia se esperan. Después,
abrir los pasos que lo confirman. No recorrer los once ejemplos durante toda la
exposición: el catálogo también sirve para responder preguntas.

1. **Datos y fórmula abierta.** Cargar «P(x): pertenencia y asignación». Mostrar
   D y P en sus fichas. Evaluar con x: 1: Verdadero. Cambiar x: 3: desaparece el
   resultado anterior; reevaluar: Falso. La tupla (3) no pertenece a P.
2. **Las cuatro justificaciones obligatorias.** Usar los ejemplos de la tabla
   siguiente. En los casos completos, abrir las tres comprobaciones. Distinguir
   un resultado falso de un caso que no fue necesario visitar.
3. **Valor del aporte.** Cargar «∃x P(x): encontrar un testigo». Evaluar y abrir
   Comparar un cambio. Probar «Quitar (1) de P» y comparar. Ambas ejecuciones son
   verdaderas; el testigo pasa de 1 a 2. Abrir sus evidencias y mostrar los pasos
   afectados. La interpretación original continúa intacta.
4. **Validación.** Volver a cargar P(x), escribir `P(x` y evaluar. No aparece
   verdad; el mensaje lleva al campo. Corregir a `P(x)` y evaluar. Para preguntas
   adicionales, usar los errores de respaldo de esta guía.
5. **Implementación.** Explicar brevemente el recorrido de datos entre interfaz,
   servidor, M2 y M1. Cada integrante debe poder continuarlo si el docente cambia
   quién responde.

| Ejemplo seleccionable | Resultado esperado | Justificación que se debe abrir |
| --- | --- | --- |
| ∃x P(x) | Verdadero | Testigo x: 1; 2 y 3 no se visitaron |
| ∀x P(x) | Falso | Contraejemplo x: 3; 1 y 2 sí pertenecen a P |
| ∀x (P(x) ∨ ¬P(x)) | Verdadero | Tres comprobaciones verdaderas; comprobar solo una no basta |
| ∃x (P(x) ∧ ¬P(x)) | Falso | Tres comprobaciones falsas; no se utiliza una relación vacía |

P contiene 1 y 2 en D = {1, 2, 3}. Que el universal falso recorra los tres
elementos muestra que «recorrido completo» no significa «Verdadero».

## Caso integrado para la defensa o la final

Seleccionar **Caso integrado: cuantificadores, función y constante**.
Es una combinación didáctica de las interpretaciones de las pp. 181 y 187 de
Lógica TEO 2.pdf; la fórmula combinada es un ejemplo nuevo.

```text
(∀x ∃y (Q(x,y) ∧ R(f(x,y)))) ∧ ¬R(i)
```

D = {a, b, c}. La constante i designa a. R contiene b y c.
Q contiene (a,a), (a,b), (a,c), (b,c) y (c,c).

| Argumentos de f | Imagen | Argumentos de f | Imagen | Argumentos de f | Imagen |
| --- | --- | --- | --- | --- | --- |
| (a,a) | b | (a,b) | a | (a,c) | c |
| (b,a) | a | (b,b) | b | (b,c) | c |
| (c,a) | c | (c,b) | c | (c,c) | a |

La fórmula pregunta si cada x tiene alguna pareja y en Q cuyo valor f(x,y)
pertenezca a R, y además si el elemento designado por i no pertenece a R.

| x | Comprobación decisiva inicial | Resultado de ∃y |
| --- | --- | --- |
| a | y: a; Q(a,a) es verdadera y f(a,a) produce b, que pertenece a R | Verdadero |
| b | y: c; Q(b,c) es verdadera y f(b,c) produce c, que pertenece a R | Verdadero |
| c | y: a y y: b fallan en Q; con y: c, Q(c,c) es verdadera pero f(c,c) produce a, que no pertenece a R | Falso tras comprobar los tres y |

El universal es falso por x: c. Como i designa a, R(i) es falsa y su negación es
verdadera. La conjunción completa resulta **Falso**.

### Comparación que cambia la verdad

1. Abrir Comparar un cambio y confirmar la fórmula y el resultado originales.
2. Abrir Elegir otro dato manualmente.
3. Seleccionar **Valor de f(c, c): a** y elegir **b**.
4. Verificar que solo se propone esa imagen distinta y pulsar Comparar resultados.
5. En la variante, x: c tiene ahora testigo y: c: f(c,c) produce b y R(b) es
   verdadera. El universal es verdadero para los tres x y la conjunción resulta
   **Verdadero**. La constante y las relaciones no cambiaron.
6. Comprobar que el formulario y el resultado original siguen conservando f(c,c)
   con imagen a y resultado Falso.

### Comparación que conserva la verdad

Desde la misma base original, elegir **Valor de f(a, a): b** y cambiarlo a **c**.
El resultado continúa siendo Falso por x: c. Sin embargo, la consulta del término
f(a,a) cambia de b a c. Ambas imágenes pertenecen a R: cambia la evidencia sin
cambiar la verdad. Las dos variantes se comparan con el original, no se acumulan.

## Preguntas y casos de respaldo

### Alcance y variables libres

Con el ejemplo de P, escribir `∃x P(x) ∧ ¬P(x)`. Revisar variables libres y elegir
x: 3. Es verdadera: el existencial encuentra 1 y la negación exterior utiliza 3.
Escribir después `∃x (P(x) ∧ ¬P(x))`: es cerrada, no pide entorno y es falsa.
Son dos fórmulas diferentes; se evalúan por separado, no como un solo cambio del
comparador.

Para mostrar todos los conectivos desde el editor, también se puede evaluar:

```text
∀x ((P(x) → P(x)) ↔ (P(x) ∨ ¬P(x)))
```

Es verdadera para los tres elementos. La conjunción se demuestra en los casos
anteriores. Los alias de teclado y los botones se verifican en las pruebas de UI.

### Configuración con nombres nuevos

Para demostrar que las respuestas no dependen del catálogo: limpiar, introducir
D = {u, v}, añadir constante k con elemento u, función unaria g con imágenes
(u): v y (v): u, y predicado Elegido con la tupla (v). Evaluar `Elegido(g(k))`:
Verdadero. Cambiar solo el valor de g(u) a u en una copia produce Falso.

La función debe ser total, aunque la fórmula consulte solo una entrada. No
introducir «u» como término constante sin declararlo: los elementos de D y los
símbolos del lenguaje tienen funciones distintas.

### Errores y recuperación

Recargar el ejemplo indicado antes de cada caso permite conservar una referencia
válida. Tras el rechazo, recargar y evaluar demuestra la reparación.

| Caso | Preparación desde la UI | Qué debe ocurrir |
| --- | --- | --- |
| Dominio vacío | P(x): borrar D | Error de dominio, sin verdad |
| Sintaxis | P(x): escribir `P(x` | Error de paréntesis, sin verdad |
| Símbolo desconocido | P(x): escribir `Desconocido(x)` | Error de símbolo, sin verdad |
| Aridad incorrecta | P(x): escribir `P(x,x)` | Error de aridad, sin verdad |
| Entorno faltante | P(x): escribir `P(z)` sin asignar z | Solicitar z; no suponer un valor |
| Tupla fuera de D | P(x): reducir D a {1,2} conservando las filas de R | Rechazar las componentes 3 que quedaron fuera |
| Relación vacía | P(x): quitar las dos tuplas de P | Rechazo aunque una relación vacía tenga sentido en otras convenciones; la guía la prohíbe |
| Función parcial | Ejemplo de términos: quitar la fila f(c,c) | Rechazar la interpretación incompleta |
| Salidas incompatibles | Ejemplo de términos: añadir otra fila (a,a) con imagen c | Rechazar dos imágenes distintas para la misma entrada |

Los selectores previenen varios errores de entrada. La validación completa sigue
siendo necesaria porque editar D o la aridad puede dejar filas anteriores inválidas.

## Defensa del código

| Pregunta del docente | Qué explicar y dónde localizarlo |
| --- | --- |
| ¿De dónde sale el valor de verdad? | [app.js](../frontend/js/app.js), run(): analyze y evaluate; [codec.py](../lm_p3/server/codec.py), process_request(): constructores de M2 y servicio de evaluación; [evaluator.py](../lm_p3/semantics/evaluator.py), evaluate y formula |
| ¿Qué guarda un ejemplo? | [examples.js](../frontend/js/examples.js): lenguaje, dominio, tablas, fórmula y asignaciones. No contiene los booleanos que muestra el resultado |
| ¿Cómo se configura una constante? | [editors.js](../frontend/js/editors.js), isConstant y inputData: ficha propia; contrato existente con aridad cero y fila de argumentos vacía |
| ¿Por qué se conservan las filas como listas? | Para que M2 detecte duplicados y conflictos antes de normalizar a diccionarios o conjuntos |
| ¿Quién descubre las variables libres? | M2; la UI consume analyze y renderEnvironment solicita las necesarias. No usa una expresión regular propia |
| ¿Cómo se conserva el alcance? | El evaluador de M1 copia el entorno al entrar a cada cuantificador. La asignación exterior no se sobrescribe permanentemente |
| ¿Por qué una disyunción verdadera muestra ambos operandos? | M1 evalúa ambos operandos para conservar evidencia. Los cortes decisivos se aplican en cuantificadores |
| ¿Se ocultan comprobaciones al plegar pasos? | evidenceNode crea el detalle visual al abrirlo. La evidencia completa requerida ya fue calculada por M1 y está en la respuesta |
| ¿Qué significa Paso 1.1.2? | Es una dirección de navegación dentro del árbol mostrado, no un contador cronológico de instrucciones |
| ¿Por qué «no visitado» no es Falso? | El motor pudo decidir con otro testigo o contraejemplo; no atribuye verdad a lo que no comprobó |
| ¿Cómo se descartan respuestas antiguas? | app.js captura revision antes de esperar; publicar exige que siga coincidiendo. comparison.js mantiene su propia versión |
| ¿Qué hace Aceptar edición? | Vuelve al resumen. Los campos actualizan el estado al editar; la validación matemática completa se hace al evaluar |
| ¿Por qué no cambias la fórmula en la comparación? | El aporte compara un solo dato con lenguaje, D y fórmula fijos. M1 rechaza cambiar esa base |
| ¿Cómo eliges sugerencias? | comparison.js recorre la evidencia de M1, prioriza la rama decisiva y recoge datos consultados. Las sugerencias no predicen el nuevo resultado |
| ¿Qué aporta M3 respecto a M1/M2? | Transporte local, adaptación JSON, formularios, estado, navegación, foco, errores y comparación gráfica. M1 aporta motor/evidencia/comparador; M2 aporta parser/variables libres/validación |
| ¿Es una demostración de validez universal? | No: evalúa una interpretación finita concreta. Tampoco sustituye deducción natural ni prueba fórmulas para todos los dominios |

## Verificación antes de exponer

- Ejecutar desde una copia del repositorio sin entorno virtual ni acceso a Internet:
  `python3 -B -m lm_p3`. La aplicación utiliza Python estándar y recursos locales.
- Confirmar Python compatible, navegador, tamaño del proyector y zoom. No asumir
  que una ejecución en Linux acredita pruebas nativas en Windows o macOS.
- Repetir al menos una configuración desde cero y los dos cambios del caso integrado.
- Ensayar los cuatro casos cuantificados y un error con reparación.
- Distribuir la exposición entre los tres, pero practicar preguntas cruzadas sobre
  todo el código. La guía permite preguntar cualquier parte a cualquier integrante.
- Registrar el ensayo real y las observaciones de un compañero: fecha, participantes,
  caso, dificultad, corrección y repetición. No confundir el ensayo automático con
  una exposición realizada por el equipo.
- Conservar una copia local que funcione, las tablas de esta guía y una captura
  actual del resultado/comparación como respaldo para una incidencia durante la demo.
- Preparar la coevaluación individual con aportes y colaboración reales; es confidencial.

El guion es material de preparación. Los 30 puntos de defensa, la utilidad observada
por compañeros y los votos de la competencia requieren participación del equipo.

## Respaldo visual actual

Estas capturas proceden de la aplicación ejecutada con el caso integrado:

- [Resultado y comprobaciones exteriores](evidencias/m3-demo-integrada.png).
- [Comparación de f(c,c) con imágenes a y b](evidencias/m3-demo-comparacion.png).

Sirven de respaldo ante una incidencia. La demostración en vivo permite editar
datos, validar y recalcular; las capturas conservan una sola ejecución concreta.
