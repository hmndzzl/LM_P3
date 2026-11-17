# Publicación del evaluador en GitHub Pages

## Arquitectura publicada

GitHub Pages aloja contenido estático. La edición publicada conserva el motor Python de `lm_p3/`, empaquetado en ZIP, y lo ejecuta con **Pyodide 314.0.8** en un worker de tipo módulo. Parser, validación, evaluación, evidencia y comparación usan las mismas funciones que la aplicación local. No se reimplementa la lógica en JavaScript y no se necesita un servidor Python remoto.

El modo local sigue usando HTTP y `/api/analyze`, `/api/evaluate`, `/api/compare`. El generador cambia `executionMode` a `browser` únicamente en la copia publicada de `runtime-config.js`; allí `api.js` delega en el worker. Las rutas de CSS/JS y del ZIP son relativas para admitir `/LM_P3/`.

En Pages se requiere conexión para descargar los archivos del proyecto y el intérprete desde jsDelivr al inicializar. La primera operación puede tardar; se muestra un aviso. Después de cargarlo, las entradas se procesan en el navegador, sin enviarse a una API remota. No se promete uso sin conexión de la edición publicada. La aplicación local mantiene su ejecución sin Internet.

## Qué se publica

`scripts/build_pages.py` genera `_site/` con:

- HTML, CSS, JavaScript y recursos admitidos de `frontend/`.
- `python/lm_p3.zip`: fuentes Python del paquete, excluyendo el arranque del servidor HTTP.
- `.nojekyll` y `build-info.json` con SHA-256 del paquete usado.

No se publican `bases/`, `tasks/`, documentos internos, `.git`, `.venv`, pruebas ni archivos de entorno. `_site/` está ignorado en Git y se genera durante Actions; no hay que subirlo manualmente ni habilitar Pages sobre la raíz del repositorio. El destino del generador debe estar vacío para no sobreescribir contenido ajeno.

## Preparar y comprobar localmente

Con Python 3.10+:

```sh
python -B -m unittest discover -s tests -t . -v
python -B scripts/build_pages.py
python -B -m http.server 8765 --bind 127.0.0.1 --directory _site
```

Abrir `http://127.0.0.1:8765/`. Ese servidor entrega exclusivamente archivos estáticos, sin endpoints Python; que una fórmula se evalúe allí comprueba que se usa el motor del navegador.

La carpeta `_site/` debe estar ausente o vacía antes de construir. Para una segunda construcción, usar otra carpeta vacía con `--output`. No modificar manualmente el ZIP: se genera desde el código del proyecto.

El transporte aplica un máximo de espera de 120 segundos. Si se excede o falla el worker, termina sus peticiones con error y permite reintentar con un worker nuevo. Los presupuestos y errores del motor siguen vigentes; ninguno de esos fallos recibe un valor de verdad. El adaptador conserva límites de 256 KB de petición y 8 MB de respuesta.

## Workflow y activación

Archivo: `.github/workflows/pages.yml`.

- En un PR a `main`: ejecuta pruebas Python, sintaxis JavaScript, pruebas de transporte, construcción y comprobación de los once ejemplos con Pyodide real. No publica el PR.
- En un push a `main` o ejecución manual desde `main`: hace esas mismas comprobaciones y publica solo `_site/` mediante las acciones oficiales de Pages.
- Permisos: lectura del repositorio para construcción; `pages: write` e `id-token: write` exclusivamente en el trabajo de despliegue.

En **Settings → Pages → Build and deployment → Source**, seleccionar **GitHub Actions**. Esta selección ya se guardó en el repositorio durante la preparación. No usar el botón de plantilla «Static HTML»: este proyecto requiere generar el paquete Python y verificarlo antes de subir el artefacto.

Los cambios de `feat/deploy` deben incorporarse a `main` para que se ejecute la publicación automática. Revisar el resultado en **Actions → Verificar y publicar en GitHub Pages** y esperar a que `deploy` termine correctamente. GitHub entrega el enlace de producción en ese trabajo.

URL prevista para este repositorio: **https://hmndzzl.github.io/LM_P3/**. No darla por publicada hasta verificar una ejecución de Actions completada y abrir el enlace público.

## Validación realizada antes de publicar

- 157 pruebas Python pasan con Python 3.11, incluyendo servidor local y nuevos casos del adaptador/generador.
- 3 pruebas Node del transporte: respuestas correlacionadas, recuperación tras error y ausencia de falsedad inventada ante un fallo del intérprete.
- Pyodide 314.0.8 real cargó el paquete generado y calculó los once ejemplos con sus expectativas, análisis de variables, comparación de asignación, error de sintaxis, entorno faltante y relación vacía.
- En navegador, sobre `http://127.0.0.1:8766/LM_P3/` servido sin API: carga desde CDN, P(x) verdadero con x=1, falso con x=3 y comparación añadiendo (3) a P para pasar a verdadero. Sin errores de consola en el recorrido observado.
- [Captura de comparación](evidencias/pages-preview.jpg). Es evidencia de previsualización estática local, no de un despliegue público ya completado.

Para repetir la comprobación del motor WebAssembly en CI/local con Node 24, instalar Pyodide en un directorio temporal y ejecutar:

```sh
npm install --prefix /tmp/lm-pages-runtime --no-audit --no-fund pyodide@314.0.8
PYODIDE_MODULE_PATH=/tmp/lm-pages-runtime/node_modules/pyodide/pyodide.mjs node tests/deploy/test_pyodide.mjs
node --test tests/deploy/test_browser_api.mjs
```

Es una dependencia de verificación/runtime web fijada por versión; no agrega dependencias Python al modo local ni crea `node_modules` en el repositorio.

## Comprobar producción y recuperar una publicación

Tras un despliegue correcto, abrir el enlace en una sesión nueva, cargar un ejemplo, evaluar, comprobar una fórmula inválida y comparar un cambio. Revisar que no haya 404 de CSS, módulos, ZIP ni peticiones a `/api/`. La carga inicial desde CDN debe completarse también en esa sesión.

Si falla Actions, corregir el paso concreto; no omitir pruebas para publicar. Para recuperar una versión anterior, una persona puede revertir el cambio responsable con un commit nuevo en `main` y dejar que el workflow vuelva a construir y desplegar. No reescribir el historial ni servir una captura como sustituto del evaluador.

## Fuentes oficiales

- [Naturaleza estática de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
- [Workflows de publicación en Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
- [Pyodide en workers de tipo módulo](https://pyodide.org/en/stable/usage/webworker.html).
- [Carga de código Python empaquetado](https://pyodide.org/en/stable/usage/loading-custom-python-code.html).
