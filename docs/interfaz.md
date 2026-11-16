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

Cargar ejemplo → Evaluar fórmula da Verdadero para Activa(x), x=centro.
Seleccionar sur y reevaluar da Falso. El ejemplo editable incluye el mundo de M2:
relevo, Activa y Enlaza sobre norte, centro, sur. No carga resultados prefijados.
Para datos propios, abrir Lenguaje y Dominio y tablas. Plegar secciones conserva
el trabajo; el resumen muestra hasta cuatro elementos/filas por símbolo y el
resto sigue disponible en sus tablas. Los errores abren la sección afectada.

## Editores

Los nombres y aridades son configurables, incluida aridad cero. D se introduce
con un elemento por línea. Argumentos, salidas y asignaciones usan selectores
con valores de D. Si cambia el dominio, se conservan valores recuperables como
«fuera de D» para poder corregirlos; no se inventan salidas funcionales.
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
anidados. Seleccionarlo resalta su rango en la fórmula original; los rangos Python
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

El fondo solicitado usa 36 símbolos decorativos, opacidad .14 y ciclos de 5–8
segundos. Está detrás de paneles opacos, no captura clics y queda fuera del árbol
accesible. Fondo animado permite pausarlo; prefers-reduced-motion lo desactiva.
No representa datos ni resultados y no interviene en la lógica.

Transporte: 256 KB por petición, 5 segundos de lectura y 8 MB de respuesta.
Editor: aridad de 0 a 32 y hasta 2000 filas por símbolo; no materializa D^n.
M2 limita colecciones y AST; M1 limita visitas y profundidad. Ningún límite produce
verdad parcial. No se ofrece Cancelar porque no se conectó cancelación real.
Los límites son de recursos, no restricciones matemáticas ni garantía de tiempo.

## Verificación y aceptación

[Evidencia reproducible y capturas](evidencias/miembro-3.md): 149 pruebas Python,
67 comprobaciones de navegador y tres adicionales con movimiento reducido.
Se reprodujo el funcionamiento desde git archive, sin .git ni entorno virtual.
La comparación se revisó a 1440, 1024, 768 y 320 px, sin scroll horizontal global.

La implementación técnica cubre M3-01/02/03 y los entregables técnicos de M3-04.
No acredita revisión de compañeros, ensayo de defensa, lector de pantalla ni
pruebas nativas de otros sistemas/navegadores. Esas actividades humanas conservan
su estado pendiente y se coordinan entre los tres. Ver la matriz general.

## Guiones de demostración y práctica

**Primera ronda (ajustar duración al tiempo oficial):** M2 configura/explica el
mundo; M1 evalúa ∃x Activa(x), ∀x Activa(x) y ∀x ∃y Enlaza(x,y); M3 abre un paso,
localiza la subfórmula y compara ∃x Activa(x) quitando norte de Activa. La verdad
se mantiene y el testigo cambia a centro. Mostrar un error y su reparación.

**Defensa técnica:** recorrer una petición real desde app.js hasta el servicio,
explicar filas versus diccionarios, un rango Unicode y el control de versiones.
Comparar Activa(relevo(x)), x=centro, cambiando relevo(centro) de sur a norte:
Falso → Verdadero. Mostrar que el original sigue igual y rechazar una variante
que deje una relación vacía. Resolver una fórmula nueva sin modificar código.

Los tres deben practicar preguntas fuera de su módulo y registrar la sesión real.
Las capturas son respaldo visual, no sustituyen el funcionamiento en vivo. No hay
ensayo ni observaciones de compañeros inventados en esta documentación.
