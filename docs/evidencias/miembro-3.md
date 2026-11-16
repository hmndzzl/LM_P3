# Evidencia técnica — Miembro 3

## Alcance

Actualización del 16 de noviembre de 2026: el catálogo sustituye el ejemplo de
estaciones por nueve ejemplos seleccionables de Lógica TEO 2.pdf, con páginas,
explicación y práctica. Se distinguen transcripciones, variantes y la adaptación
finita de Sócrates. No se cambiaron motor, parser, validadores ni corpus de M2.

Verificación actual del catálogo:

| Comprobación | Resultado real |
| --- | --- |
| Suite Python | 149 pruebas aprobadas |
| tests/ui/smoke.js, con los ejemplos nuevos | 31 comprobaciones aprobadas |
| tests/ui/completion.js, con los ejemplos nuevos | 31 comprobaciones aprobadas |
| tests/ui/assignments.js | 6 comprobaciones aprobadas |
| tests/ui/examples.js | 33 comprobaciones aprobadas |
| tests/ui/editor-arity.js | 9 comprobaciones aprobadas |
| tests/ui/evidence.js | 16 comprobaciones aprobadas |
| tests/ui/interpretation-summary.js | 14 comprobaciones aprobadas |
| tests/ui/comparison-flow.js | 14 comprobaciones aprobadas |
| tests/ui/unified-configuration.js | 11 comprobaciones aprobadas |
| tests/ui/background.js | 3 normales y 3 con movimiento reducido |
| Anchos 1440/1024/768/320 con el selector nuevo | Sin scroll horizontal global |
| Axe-core 4.12.1, ejemplo a 320 px | 0 infracciones, 42 reglas aprobadas; contraste incompleto en ocho nodos por símbolos/solapamiento del fondo |

Se probaron los nueve resultados contra M1/M2, la independencia de las tablas al
recargar, cancelar carga/limpieza, comparar antes de limpiar y descartar una
respuesta pendiente después de limpiar. Los selectores de asignación contienen
solo elementos del dominio actual; los valores anteriores se explican aparte.
Controles, evidencia, testigos y comparación usan : para asignaciones.

Revisión posterior de la misma fecha: al aumentar aridad de 2 a 5, todas las filas
muestran cinco campos; los tres nuevos quedan vacíos. Se conservan valores/salidas,
y reducir aridad pide confirmación si se perderían componentes ingresados. El
texto de tipo y acción de la tabla no se divide dentro de las palabras. La traza
muestra números por niveles y valores, explica el corte de cuantificadores y oculta
identificadores internos. Se reproduce el caso ∀x ∀y R(x,y) de las capturas.
El selector se titula Probar Ejemplos y su ayuda ya no muestra la referencia al PDF.
El panel Interpretación separa elementos del dominio, tuplas y argumentos/imagen
de las funciones; permite desplegar las filas restantes en la misma tabla, sin
repetir título ni encabezados. Se comprueba plegar y desplegar sin duplicar filas. Las constantes se
identifican explícitamente. Los diez scripts pasan en conjunto: 168 comprobaciones
normales. La terminología visible se ajustó a las notas del curso.

El comparador ahora usa un selector directo, muestra Original y Cambio propuesto
y propone añadir o quitar una tupla según su pertenencia actual. No usa casilla
de pertenencia ni anuncia una modificación cuando se conserva una imagen o
asignación. Las pruebas incluyen añadir una tupla y descartar respuestas tardías.
La evidencia separa asignaciones/términos, comprobaciones y conclusión. Las
etiquetas de resultado usan valores de M1 (se reproduce ¬∀x P(x) con estados
verdadero/falso/verdadero/verdadero/falso). Se revisaron ambas vistas a 320 px, sin
desbordamiento horizontal, y capturas de escritorio. Axe sobre la comparación:
0 infracciones, 49 reglas aprobadas y una revisión de contraste incompleta.

Rediseño de configuración: cada ficha reúne declaración e interpretación de un
símbolo; solo hay un editor abierto. Añadir constante pide nombre y elemento de D,
sin filas vacías ni aridad visible. Se verificó crear c, configurar P y evaluar P(c)
con el motor real. La comparación se sitúa inmediatamente después del resultado en
la columna de trabajo; la configuración tiene desplazamiento propio en escritorio.
Se inspeccionaron ambas distribuciones y los anchos 1440/1024/768/320 sin scroll
horizontal global. La comparación muestra fórmula, asignaciones y resultado
original y propone hasta seis cambios tomados de pasos realmente evaluados.
Se comprobó la pertenencia de Q(a,c) de las notas y que editar la interpretación
retira el resultado y la comparación anteriores. Axe: 0 infracciones, 49 reglas
aprobadas y una revisión de contraste incompleta. Suite Python repetida: 149 OK.
Auditoría contra f772c92: sin cambios en modelos, semántica, sintaxis, validación
ni aplicación de M1/M2; solo cambios de M3.

Ajuste de continuidad: la cabecera del símbolo precede al resumen y permanece
en su posición al desplegar el editor. Declaración e interpretación forman un
único bloque sin repetir el título. Las consultas de función y las etiquetas de
comparación usan «Valor de ...: ...»; la flecha → se conserva como símbolo lógico
en las fórmulas y no se utiliza para representar sus resultados.

El fondo tiene 60 letras y símbolos; se retiró su botón de pausa por solicitud
del usuario. Conserva velocidad, opacidad y movimiento reducido. Se inspeccionaron
capturas nuevas de escritorio y móvil. El informe y las capturas siguientes
conservan la fecha y los ejemplos de la entrega del 15; no representan el catálogo
actual ni una nueva prueba desde git archive.

Verificación del 15 de noviembre de 2026 en Linux, Python 3.14.8 y Chromium
controlado con agent-browser. Se implementaron los recorridos gráficos de M3,
conservando motor/parser/validador y bases heredadas. El nombre visible es
Evaluador semántico. Los commits se hicieron por solicitud expresa del usuario.

## Resultados reproducidos

| Comprobación | Resultado real |
| --- | --- |
| `python3 -B -m unittest discover -s tests -t .` | 149 pruebas aprobadas, sin omisiones |
| `tests/ui/smoke.js` en navegador | 31 comprobaciones aprobadas |
| `tests/ui/completion.js` en navegador | 31 comprobaciones aprobadas |
| `tests/ui/background.js`, movimiento normal | 5 comprobaciones aprobadas |
| `tests/ui/background.js`, movimiento reducido | 3 comprobaciones aprobadas |
| Copia limpia con git archive | 149 pruebas y las 67 comprobaciones de navegador pasan también contra esa copia |
| Lanzador POSIX desde /tmp | Inicia la copia limpia y sirve los recursos desde su propia raíz |
| Anchos de comparación 1440/1024/768/320 | Sin scroll horizontal global; a 1024/768/320 el ancho del documento coincide con el viewport |
| Axe-core 4.12.1, resultado | 0 infracciones; 28 reglas aprobadas y 1 revisión incompleta de contraste sobre cinco glifos |
| Axe-core 4.12.1, comparación | 0 infracciones; 26 reglas aprobadas y la misma revisión incompleta de glifos |
| Contraste manual de botones señalados | Color efectivo rgb(23,43,58) sobre rgb(255,255,255): 14.55:1 |

Las pruebas Python incluyen los 130 casos anteriores y 19 de transporte/arranque.
No se alteraron ni eliminaron pruebas anteriores. El oráculo de 900 evaluaciones
sigue pasando dentro de la suite. Los scripts de navegador evalúan con M1/M2 reales;
los retrasos de respuesta se introducen solo para comprobar descarte de resultados
obsoletos. No sustituyen la semántica por resultados prefijados.

Para reproducir en una sesión de prueba con la aplicación abierta:

```sh
python3 -B -m lm_p3 --no-browser --port 8765
# En otra terminal, con agent-browser instalado como herramienta opcional:
agent-browser --session m3-revision open http://127.0.0.1:8765
agent-browser --session m3-revision eval --stdin < tests/ui/smoke.js
agent-browser --session m3-revision eval --stdin < tests/ui/completion.js
agent-browser --session m3-revision eval --stdin < tests/ui/assignments.js
agent-browser --session m3-revision eval --stdin < tests/ui/examples.js
agent-browser --session m3-revision eval --stdin < tests/ui/editor-arity.js
agent-browser --session m3-revision eval --stdin < tests/ui/evidence.js
agent-browser --session m3-revision eval --stdin < tests/ui/interpretation-summary.js
agent-browser --session m3-revision eval --stdin < tests/ui/comparison-flow.js
agent-browser --session m3-revision eval --stdin < tests/ui/unified-configuration.js
agent-browser --session m3-revision eval --stdin < tests/ui/background.js
agent-browser --session m3-revision set media light reduced-motion
agent-browser --session m3-revision eval --stdin < tests/ui/background.js
```

Estos scripts reemplazan datos de los formularios de esa sesión. No son necesarios
para usar la aplicación ni agregan dependencias al producto.

## Cobertura importante

- Botones de los nueve símbolos, inserción en selección, foco, deshacer/rehacer.
- Nombres propios, aridad cero, dominio editable y valores recuperables fuera de D.
- Conteo funcional y errores que enfocan la salida concreta; rechazo antes del motor.
- Variables libres, cuatro resultados cuantificados, toda la comprobación exigida,
  términos anidados y selección de subfórmula con caracteres fuera del plano básico.
- Función, pertenencia relacional y asignación libre comparadas sobre copias.
  Cambio de verdad y cambio de testigo sin nueva verdad; base conservada.
- Rechazo de relación vacía, cero/múltiples cambios y contextos diferentes.
- Respuestas viejas de evaluación y comparación descartadas tras editar.
- 36 símbolos de fondo sin eventos de ratón ni lectura accesible; pausa/reanudación
  y desactivación por prefers-reduced-motion.

## Respaldo visual inspeccionado

Las capturas proceden de ejecución real con datos del ejemplo y fueron abiertas
para revisión. Son respaldo; no sustituyen pruebas ni una demostración en vivo.

- [Escritorio](m3-escritorio.png): formulario, barra lógica, resultado y resumen.
- [Comparación](m3-comparacion.png): ∃x Activa(x), quitar norte conserva Verdadero
  y cambia el testigo de norte a centro.
- [Móvil](m3-movil.png): la misma aplicación y comparación a 320 px.

## Cierre de tickets y límites de esta evidencia

| Ticket | Implementación técnica | Aceptación humana |
| --- | --- | --- |
| M3-01 | Recorrido atómico, servidor, codec, formularios y estados comprobados | Otro integrante debe repetirlo con datos propios |
| M3-02 | Edición completa, símbolos, entorno, errores y contexto comprobados | M2 debe revisar mensajes y casos desde la UI |
| M3-03 | Evidencia navegable, resaltado y comparación real comprobados | M1 debe revisar fidelidad; compañero debe explicar evidencia y observar utilidad |
| M3-04 | Lanzadores, copia limpia Linux, guía, guiones y respaldo preparados | Falta ensayo de los tres, lector de pantalla y ejecución nativa en macOS/Windows |

No se afirma conformidad WCAG completa ni ejecución en otros navegadores/sistemas.
La fuente de las posiciones es Python; la conversión y el historial se comprobaron
en Chromium. No se ejecutó un lector de pantalla ni se inventó una sesión con
compañeros. Las actividades de enseñanza, exposición, coevaluación y revisión
siguen siendo humanas y no pueden darse por realizadas mediante pruebas técnicas.
