# M3 — Evaluador semántico

## Ejecución y primer recorrido

Desde la raíz, con Python 3.10 o posterior:

```sh
python3 -B -m lm_p3
```

Se abre una dirección de 127.0.0.1; Ctrl+C cierra el servidor. Para abrirla
manualmente: `python3 -B -m lm_p3 --no-browser --port 8765`.
No hay dependencias externas que instalar. Los lanzadores de scripts/ resuelven
la raíz aunque se ejecuten desde otro directorio: .sh para Linux, .command para
macOS y .bat para Windows. Su ejecución nativa en macOS/Windows debe revisarse.

Seleccionar P(x): pertenencia y asignación → Cargar ejemplo → Evaluar fórmula
da Verdadero con x: 1. Seleccionar 3 y reevaluar da Falso. Hay nueve ejemplos
seleccionables de las notas del curso, cada uno con explicación y práctica.
Las referencias al PDF se conservan en el catálogo y en esta guía, sin mostrarlas
en la ayuda de la interfaz.
Solo se cargan entradas; el resultado siempre se solicita al motor.
Limpiar todo borra fórmula, lenguaje, dominio, tablas, asignaciones, guía, errores,
resultado, evidencia y comparación. Pide confirmación si hay trabajo cargado;
una respuesta pendiente no restaura datos después de limpiar.
Para datos propios, abrir Lenguaje y Dominio y tablas. Plegar secciones conserva
el trabajo. El panel Interpretación distingue dominio del discurso, relaciones
y funciones/constantes. El dominio separa sus elementos; cada relación muestra una
tupla por fila y cada función separa Argumentos e Imagen. Se muestran hasta cuatro
elementos o filas inicialmente y un desplegable permite consultar los restantes.
Cada símbolo tiene su propia tabla; los argumentos siempre conservan paréntesis. Los errores abren la sección afectada.

## Ejemplos de las notas

Fuente: Lógica TEO 2.pdf, 299 páginas. Los números siguientes corresponden a
páginas del PDF, no a la numeración de las diapositivas. Se revisó el material
completo para ubicar los casos aplicables: lógica proposicional, lenguaje y
sintaxis de predicados, deducción, interpretaciones y entornos, metateoremas,
indecidibilidad, aritmética de Peano e incompletitud de Gödel. Los ejemplos que
encajan directamente con el evaluador están en interpretaciones y entornos.

| Selector / fórmula | Página y procedencia | Resultado inicial |
| --- | --- | --- |
| P(x), x: 1 | 179, fórmula abierta añadida a su interpretación | Verdadero |
| ∀x P(x) | 179, fórmula e interpretación originales | Falso; contraejemplo x: 3 |
| ∀x ∃y R(x,y) | 179, fórmula e interpretación originales | Verdadero |
| ∃x P(x) | 179, variante de práctica sobre la misma interpretación | Verdadero; testigo x: 1 |
| ∃x (P(x) ∧ ¬P(x)) | 179, variante de práctica sobre la misma interpretación | Falso; comprueba los tres elementos |
| ¬R(i) | 181, fórmula e interpretación originales | Verdadero; i produce a |
| ∃y Q(i,y) | 181, fórmula e interpretación originales | Verdadero; testigo y: a |
| P(x, f(x,y)), x: b, y: b | 187, ejemplo manuscrito y tabla completa | Falso; f(b,b) produce b y (b,b) no pertenece a P |
| (∀x (H(x) → M(x))) ∧ H(s) | 108–115, adaptación finita del ejemplo de Sócrates | Verdadero |

En el último se añade explícitamente D = {Sócrates, Platón}, con ambos en H y M;
las notas motivan el lenguaje, pero no fijan ese dominio finito. En el ejemplo
manuscrito solo se cargan las variables libres x e y: z aparece en su entorno,
pero no en la fórmula. La transcripción está en frontend/js/examples.js; se copia
antes de editar para que recargar un ejemplo restaure sus entradas originales.

Las notas también usan igualdad nativa y dominios infinitos (cadenas y naturales).
La gramática actual no incluye igualdad y el evaluador trabaja con dominios
finitos: esos ejercicios no se presentan como si fueran compatibles sin cambios.
El signo : identifica asignaciones en la interfaz; no se añade a la gramática de
fórmulas. Un resultado en una interpretación concreta tampoco demuestra validez
universal ni sustituye las demostraciones del curso.

## Editores

Los nombres y aridades son configurables, incluida aridad cero. Al confirmar una
aridad mayor se añaden argumentos vacíos a cada fila, conservando valores y salidas.
Reducir la aridad pide confirmación si se perderían argumentos ingresados; cancelar
restaura la aridad anterior. Las fórmulas se corrigen por separado y M2 comprueba
su coherencia con el lenguaje. La tabla conserva palabras y botones completos,
con desplazamiento local en pantallas pequeñas. D se introduce
con un elemento por línea. Argumentos, salidas y asignaciones usan selectores
con valores de D. Si cambia el dominio, las tablas conservan valores recuperables
como «fuera de D». En asignaciones, el valor anterior se muestra en un aviso
separado y el selector ofrece solo elementos actuales de D. Restaurar D permite
recuperar la asignación. No se inventan salidas funcionales. Las asignaciones se
escriben x: valor en controles, evidencia, testigos y comparación; las consultas
de funciones se muestran con →.
Cada fila relacional expresa pertenencia a la relación; eliminarla quita esa
pertenencia. Se muestran las salidas funcionales pendientes sin generar D^n.
La validación integral y los conflictos se comprueban en M2 antes de evaluar.

Los nueve botones insertan ¬ ∧ ∨ → ↔ ∀ ∃ ( ) en el cursor o selección y devuelven
el foco. La inserción nativa mediante execCommand conserva el deshacer/rehacer
del navegador (comprobado en Chromium). El teclado también acepta los alias de
sintaxis.md. Revisar variables libres prepara únicamente los selectores requeridos;
la misma operación se realiza antes de evaluar. No se analiza en cada pulsación.
Las asignaciones recuperables sobreviven a una fórmula temporalmente incompleta.

## Exploración y comparación

Cada paso expandible conserva subfórmula, entorno, resultado, motivo y términos
anidados. Los encabezados muestran las asignaciones y una numeración por niveles:
1.1 es una comprobación dentro de 1, no el orden cronológico del cálculo.
El identificador interno trace_id se conserva para comparar evidencias, pero no
se muestra al usuario. El paso seleccionado indica fórmula y valores concretos.
Los cuantificadores explican qué valores probaron, por qué basta un testigo o
contraejemplo y por qué no fue necesario recorrer los valores restantes.

Por ejemplo, en ∀x ∀y R(x,y), con la interpretación de la p. 179:

| Paso | Comprobación | Valores |
| --- | --- | --- |
| 1 | ∀x ∀y R(x,y) | Ninguno al entrar |
| 1.1 | ∀y R(x,y) | x: 1 |
| 1.1.1 | R(x,y) | x: 1, y: 1 |

(1,1) no pertenece a R, por lo que el paso 1.1.1 es falso. Ese caso refuta el
universal de y en 1.1; a su vez, x: 1 refuta el universal exterior. No se afirma
ningún valor de verdad de las combinaciones no recorridas.

Seleccionar un paso resalta su rango en la fórmula original; los rangos Python
se convierten por puntos de código, conservando Unicode. Los cuantificadores
muestran testigo, contraejemplo o todas las comprobaciones necesarias. Los
no visitados se identifican explícitamente: nunca se presentan como falsos.

Tras una evaluación válida, Comparar un cambio abre tres alternativas:

- Salida funcional: elegir una fila y una salida distinta.
- Pertenencia relacional: elegir predicado, componentes y pertenencia en la variante.
- Asignación libre: elegir variable y un valor distinto.

Evaluar variante vuelve a validar y calcular ambos escenarios mediante M1/M2.
Se muestran el cambio exacto, la verdad y la evidencia antes/después. Los pasos
con cambios de evidencia tienen etiqueta textual y borde. Si se vacía una relación,
no cambia nada o cambian varios datos, se rechaza sin modificar la base. El
comparador de M1 también rechaza fórmula/lenguaje/dominio diferentes.
Cambiar el formulario principal retira resultado y base de comparación. Respuestas
antiguas de evaluación o comparación no sobrescriben una edición posterior.

## Mapa del código para la defensa

| Archivo | Responsabilidad y función de entrada |
| --- | --- |
| frontend/js/app.js | Coordina analizar → asignar → evaluar; run(), invalidate() |
| frontend/js/editors.js | Formularios y sus datos; inputData(), renderEnvironment(), errorTarget() |
| frontend/js/examples.js | Catálogo de entradas y explicaciones de las notas; examples |
| frontend/js/formula.js | Barra de símbolos y selección; initializeFormulaEditor() |
| frontend/js/api.js | Petición JSON y errores de transporte; request() |
| lm_p3/server/http.py | Loopback, rutas, tamaños y respuestas; do_POST() |
| lm_p3/server/codec.py | JSON ↔ modelos y consumo de M1/M2; process_request() |
| frontend/js/errors.js | Resumen, foco, campo y rango; showErrors(), revealField() |
| frontend/js/evidence.js | Motivos, términos y resaltado; showResult(), createEvidence() |
| frontend/js/comparison.js | Copias de escenarios y controles; setComparisonBase(), runComparison() |
| frontend/js/background.js | Animación decorativa; initializeBackground() |

El frontend no calcula verdad ni implementa otro parser. El codec utiliza
build_language, build_interpretation y build_environment antes de perder filas
duplicadas. evaluate_formula integra el parser y validador de M2 con el motor de
M1. La comparación certifica ambos escenarios y llama a semantics.compare.
No se importan ejercicios de bases/ ni expectativas de tests/ en el producto.

Orden de estudio: seguir run() hasta process_request(), abrir las funciones de
M2 que este llama, regresar a showResult() y finalmente recorrer comparison.js.
Preguntas de código: ¿qué argumento se envía?, ¿qué objeto vuelve?, ¿dónde se
bloquea una entrada inválida?, ¿qué versión evita publicar una respuesta vieja?,
¿cómo se conserva la base cuando se cambia una tupla?

## Apariencia, animación y límites

Se conserva la distribución acordada con el usuario: trabajo principal a la
izquierda y configuración a la derecha; una columna bajo 1024 px. Tipografía
proporcional, tokens compartidos, controles nativos y fondo claro sin dependencias
visuales. La fuente matemática tiene alternativas locales.

El fondo solicitado usa 60 letras y símbolos decorativos, opacidad .14 y ciclos de 5–8
segundos. Está detrás de paneles opacos, no captura clics y queda fuera del árbol
accesible. Está activo por defecto, sin botón adicional; prefers-reduced-motion lo desactiva.
No representa datos ni resultados y no interviene en la lógica.

Transporte: 256 KB por petición, 5 segundos de lectura y 8 MB de respuesta.
Editor: aridad de 0 a 32 y hasta 2000 filas por símbolo; no materializa D^n.
M2 limita colecciones y AST; M1 limita visitas y profundidad. Ningún límite produce
verdad parcial. No se ofrece Cancelar porque no se conectó cancelación real.
Los límites son de recursos, no restricciones matemáticas ni garantía de tiempo.

## Verificación y aceptación

[Evidencia reproducible y capturas](evidencias/miembro-3.md): 149 pruebas Python,
135 comprobaciones de navegador y tres adicionales con movimiento reducido.
El registro distingue las verificaciones históricas de las del catálogo actual.
Se reprodujo el funcionamiento desde git archive, sin .git ni entorno virtual.
La comparación se revisó a 1440, 1024, 768 y 320 px, sin scroll horizontal global.

La implementación técnica cubre M3-01/02/03 y los entregables técnicos de M3-04.
No acredita revisión de compañeros, ensayo de defensa, lector de pantalla ni
pruebas nativas de otros sistemas/navegadores. Esas actividades humanas conservan
su estado pendiente y se coordinan entre los tres. Ver la matriz general.

## Guiones de demostración y práctica

**Primera ronda (ajustar duración al tiempo oficial):** M2 configura/explica el
interpretación de la p. 179; M1 evalúa ∃x P(x), ∀x P(x) y ∀x ∃y R(x,y); M3 abre un paso,
localiza la subfórmula y compara ∃x P(x) quitando 1 de P. La verdad
se mantiene y el testigo cambia a 2. Mostrar un error y su reparación.

**Defensa técnica:** recorrer una petición real desde app.js hasta el servicio,
explicar filas versus diccionarios, un rango Unicode y el control de versiones.
Cargar ¬R(i), de la p. 181, y comparar la salida de la constante i de a a b:
Verdadero → Falso. Mostrar que el original sigue igual y rechazar una variante
que deje una relación vacía. Resolver una fórmula nueva sin modificar código.

Los tres deben practicar preguntas fuera de su módulo y registrar la sesión real.
Las capturas son respaldo visual, no sustituyen el funcionamiento en vivo. No hay
ensayo ni observaciones de compañeros inventados en esta documentación.
