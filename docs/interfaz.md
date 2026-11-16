# M3 — Primer recorrido gráfico

## Qué está disponible

Ejecutar `python3 -B -m lm_p3` desde la raíz. El servidor elige un puerto libre y
abre el navegador; Ctrl+C lo cierra. `--no-browser --port 8765` permite abrirlo
manualmente. No necesita Internet, frameworks ni paquetes adicionales.

La pantalla empieza sin datos ni valor de verdad. Cargar ejemplo es explícito y
solicita confirmación si reemplaza trabajo. El ejemplo reducido Estaciones activas
deriva del mundo didáctico de M2; no incluye Enlaza ni carga el corpus completo.

### Recorrido principal y configuración

Por petición del usuario, se priorizó la evaluación frente a la edición de tablas:
en escritorio, fórmula/asignaciones/resultado quedan a la izquierda y el mundo a
la derecha; en móvil se apilan en ese mismo orden. Esta decisión sustituye el
orden de configuración primero de la propuesta visual inicial. Se mantienen los
colores, controles y significado lógico acordados.

El mundo muestra un resumen de los datos ingresados, no una certificación de
validez. Lenguaje y Dominio y tablas son secciones plegables nativas: cerrarlas
no borra datos. Los resúmenes muestran hasta cuatro elementos/filas por símbolo;
el resto se conserva y puede consultarse abriendo la configuración.

Para probar: Cargar ejemplo → Evaluar fórmula (Verdadero) → seleccionar sur para x
→ Evaluar fórmula (Falso). La guía aparece junto al ejemplo y se retira al cambiar
la fórmula o configuración, para no describir un contexto anterior. Cambiar solo
la asignación mantiene la guía. Tras evaluar, el resultado se desplaza a la vista
sin animación; el detalle de evidencia queda expandible.

Se añaden funciones/predicados con nombre y aridad, elementos de D por línea y
filas gráficas de argumentos/salidas. Cada fila relacional representa pertenencia.
No se genera D^n: el usuario introduce las filas y M2 comprueba totalidad. Las filas
se conservan al cambiar nombre/aridad; las incompatibles deben corregirse o quitarse.
Las asignaciones libres se presentan como selectores de D después del análisis.

## Recorrido para estudiar el código

1. `frontend/index.html` contiene los controles. El formulario llama a `run(true)`
   en `frontend/js/app.js` al enviar. `run(false)` solo analiza.
2. `inputData(revision)` en `editors.js` recoge el estado de las filas sin convertir
   declaraciones en mapas. Ese módulo también construye los controles y conserva
   las asignaciones recuperables. `api.js` hace fetch de JSON relativo al mismo servidor.
3. `LocalHandler.do_POST()` en `server/http.py` comprueba el origen y el tamaño,
   decodifica la petición y llama a `process_request()` en `server/codec.py`.
4. `process_request()` llama a los builders de M2. Para analizar usa `analyze`;
   para evaluar llama a `evaluate_formula(..., parse=parse)` de M1/M2. No calcula
   verdad ni duplica sus reglas lógicas.
5. `error_response()` convierte diagnósticos y posiciones a JSON. Un error de
   validación puede contener varios mensajes. La respuesta válida incluye la
   traza real del motor; no se reciben resultados calculados por el navegador.
6. Al volver, `run()` publica solo una respuesta cuya revisión coincida con la
   edición actual. `invalidate()` incrementa revisión y retira el resultado al editar.
7. En `evidence.js`, `showResult()` presenta el resultado, `reasonText()` traduce
   códigos de reglas a español y `evidenceNode()` crea
   detalles nativos expandibles al abrir cada instancia, conservando sus hijos,
   entorno y elementos no visitados. En `errors.js`, `showErrors()` enlaza mensajes a campos y
   convierte puntos de código Python a UTF-16 al seleccionar un error de fórmula.

`app.js` coordina estas funciones y conserva solo revisión, ejecución pendiente y
estado de edición. Los editores notifican altas/bajas mediante el evento input
del formulario, igual que una edición normal. `errorTarget()` pertenece a los
editores porque conoce los controles; se pasa a `showErrors()` para que el módulo
de errores no necesite acceder a su estado interno. No hay dependencias circulares.

`updateWorldSummary()` en `editors.js` actualiza el resumen al editar; no evalúa
verdad. `revealField()` en `errors.js` abre los detalles que contienen el campo
incorrecto, tanto al mostrar errores como al seguir su enlace. Así ningún error
obliga a buscar un control escondido en la configuración.

Orden de lectura recomendado: `app.js` → `api.js` → `editors.js` → `errors.js` →
`evidence.js`. El CSS usa una propiedad por línea y secciones comentadas por
propósito: base, distribución, controles, tablas, resultados y accesibilidad.

Preguntas de código para practicar:

- ¿Por qué se llama a analyze antes de evaluate y por qué no necesita entorno?
- ¿Dónde se conservarían o perderían dos filas contradictorias para la misma función?
- ¿Qué impide que una respuesta de fetch vieja sustituya la entrada actual?
- ¿Qué cambia en la respuesta entre Falso válido y una entrada rechazada?
- ¿Dónde se modifica el texto que explica un testigo, sin cambiar el evaluador?

## Errores y límites

El contrato y los ejemplos JSON están en [contratos.md](contratos.md#transporte-local-de-m3--primer-incremento).
Las condiciones de HTTP comprueban transporte (origen, ruta, formato y tamaño);
las reglas de nombres, aridades, tablas y asignaciones se delegan a M2.
El handler distingue entrada inválida, límite, timeout de lectura y fallo interno.
Los detalles del último se registran en consola y la pantalla recibe un mensaje
genérico. Ninguno recibe valor de verdad.

Límites del transporte: 256 KB de petición, 5 segundos para lectura y 8 MB de
respuesta. El editor permite añadir filas con aridad de 0 a 32 y hasta 200 filas
por símbolo. No son restricciones matemáticas ni garantías de tiempo total.
No se ofrece Cancelar porque todavía no se conectó una cancelación real.

## Verificación ejecutada

En Linux con Python 3.14.8:

```sh
python3 -B -m unittest discover -s tests -t .
```

143 pruebas pasan: las 130 anteriores y 13 de codec/HTTP. Cubren peticiones reales,
análisis, resultados verdaderos/falsos, errores sin llamar al motor, claves JSON
repetidas, origen, rutas, archivos estáticos, límites y errores internos.

Con la herramienta opcional agent-browser instalada y la aplicación abierta:

```sh
agent-browser --session lm-p3-m3 open http://127.0.0.1:8765
agent-browser --session lm-p3-m3 eval --stdin < tests/ui/smoke.js
```

La prueba modifica los formularios de esa sesión. Pasan 31 comprobaciones:
configuración desde cero, verdadero/falso, cuatro casos cuantificados, evidencia
completa, errores de dominio/relación/función/entorno, posiciones Unicode, nombres
personalizados y descarte de una respuesta real retrasada. También cubre la guía,
resumen, configuración plegada y apertura/foco de campos con errores. No se
reemplaza el motor.

Se inspeccionaron capturas temporales a 1440×1000 y 320×800; a 320 px el ancho del
documento es 320 y las tablas tienen desplazamiento local. Axe-core 4.12.1 no
reportó infracciones ni comprobaciones incompletas para wcag2a/wcag2aa en el estado
de resultado probado (27 comprobaciones aprobadas). Se verificó además Cargar
ejemplo → Enter → Verdadero, y cambiar el selector a sur → evaluar → Falso.
Al reevaluar a 320×800, el borde inferior del resultado queda dentro de la vista.
No acredita conformidad total ni sustituye pruebas con lector de pantalla.

## Pendiente de los próximos bloques

Botones lógicos con cursor/selección y undo/redo; ayudas y selectores de tuplas más
cómodos; localización más precisa de filas en errores; resaltado de subfórmulas y
detalle de términos anidados; comparación gráfica de un cambio; lanzadores;
verificación con teclado/lector de pantalla y otros navegadores; ensayo humano.
Las asignaciones recuperables se conservan mientras se edita, pero el análisis
previo se solicita con botón o al evaluar: no es automático en cada pulsación.
