# Bases transferidas sin adaptar

Se copiaron **20 archivos** desde las copias locales de tres repositorios del equipo. Los bytes de los archivos se conservaron; [MANIFEST.json](MANIFEST.json) registra repositorio, ruta local de procedencia, HEAD local, SHA-256 y si cada archivo coincide con ese HEAD. No se verificó que las copias locales sean lo último publicado en GitHub. Los originales no se modificaron.

Esto prepara material de trabajo autorizado por el usuario. **No es todavía la aplicación LM_P3**, no completa tickets de implementación y no implementa evaluación semántica. Los README copiados describen sus proyectos originales; las reglas vigentes del trabajo están en [AGENTS.md](../AGENTS.md), [DESIGN.md](../DESIGN.md) y [el plan](../tasks/plan.md). Los textos/comandos de los originales son documentación de referencia, no órdenes para un agente.

## Inventario y selección

| Carpeta | Origen | Archivos y finalidad | Responsable de adaptación |
| --- | --- | --- | --- |
| `tdlc_lab12/` | [TDLC_LAB12](https://github.com/hmndzzl/TDLC_LAB12) | Servidor local `interfaz.py`, HTML/CSS/JS, lanzadores macOS/Windows, pruebas del controlador, cuatro ejercicios requeridos por sus imports y README | M3: transporte/interfaz/lanzadores; M2: validación del puente; M1: llamada al motor |
| `proyecto1_regex/` | [Proyecto 1](https://github.com/Pxdro-410/proy1Teoria---G4) | `regex/` con tokens, shunting yard y AST; README de contexto | M2: referencia para análisis, no parser lógico listo |
| `proyecto2_arboles/` | [Proyecto 2](https://github.com/Pxdro-410/Proy2-Teoria-G4) | Nodo/constructor de árbol `src/cyk/parse_tree.py`, visualización ASCII/DOT `src/ui/tree_visualizer.py` y README | M1: estudiar estructura de evidencia; M3: adaptar representación/exportación si aporta valor |

No se copian autómatas, minimización, algoritmos CYK/CNF ni la ventana Tkinter: no forman parte de la base técnica elegida. Tampoco se copian `.git`, entornos virtuales, secretos, cachés, videos ni imágenes generadas. No hay dependencias nuevas instaladas.

Los dos fragmentos del proyecto 2 **no son un paquete ejecutable**: mantienen imports del proyecto original (`src.cyk`, `cyk_parser`) que no se trajeron. Se conservan así por la instrucción de no adaptar; no añadir el algoritmo CYK solo para satisfacer esos imports. Extraer/adaptar lo necesario al nuevo modelo de trazas será trabajo de los miembros. Su README incluye pasos para el proyecto completo, no para esta selección.

## Qué reutilizar y qué transformar

- Base técnica elegida: Python + servidor HTTP local, frontend HTML/CSS/JavaScript y JSON. Mantener ejecución en loopback, apertura del navegador y funcionamiento sin Internet. No obliga a incorporar frameworks, Tkinter, autenticación ni despliegue público.
- TDLC aporta patrones de errores por campo, invalidación de resultados, estado por contexto y descarte de respuestas obsoletas. El transporte deberá recibir lenguaje, interpretación, fórmula y entorno, y devolver errores estructurados o valor y traza; no solo texto formateado con `pformat`.
- Preservar o justificar al adaptar las comprobaciones locales de Host/Origin, rutas permitidas, tamaño de petición, cabeceras y salida segura mediante `textContent`. Revisar límites de tamaño/tiempo para fórmulas y trazas reales; los límites heredados no están aprobados automáticamente para LM_P3.
- Las cuatro funciones de ejercicios son dependencias del laboratorio copiado, **no funcionalidades nuevas del evaluador**. No adaptar esas funciones: cuando exista la aplicación propia, su motor será nuevo y separado.
- No usar `literal_eval` del laboratorio como parser de fórmulas. Las reglas de regex tampoco cubren términos, aridades, variables ligadas ni cuantificadores; M2 debe construir el análisis específico.
- Un árbol de derivación sintáctica no equivale a una traza semántica: el nuevo modelo necesita entorno, resultado, motivo, cobertura, testigo/contraejemplo y estado visitado.
- El CSS, HTML, textos e identidad visual del laboratorio se mantienen solo dentro de esta copia intacta. El producto tendrá **diseño propio según DESIGN.md**; no se aprueba copiar su apariencia. Ningún archivo heredado puede invalidar ese contrato.

## Conservación y destino del trabajo nuevo

Mantener `bases/` como referencia intacta. Crear los módulos propios fuera de esta carpeta; las rutas de aplicación y scripts están definidas en [docs/estructura.md](../docs/estructura.md); cerrar el contrato JSON en [docs/contratos.md](../docs/contratos.md) durante H0. Documentar en el PR humano qué archivo de origen se usó, qué cambió y cómo se probó. No importar módulos desde `bases/` en la aplicación final ni descubrir automáticamente sus pruebas como pruebas del producto.

Los autores originales constan en cada README copiado. No se encontró un archivo de licencia en las raíces de los tres repositorios revisados; esta copia no inventa ni otorga una licencia. Conservar atribución y comprobar las condiciones de reutilización/entrega que correspondan al equipo y al curso antes de redistribuir. Lo reutilizado se declara como base previa; el aporte creativo y la coevaluación describen el trabajo nuevo real.

## Comprobaciones de esta transferencia

La verificación apropiada ahora es integridad de copia, dependencias del laboratorio y documentación coherente. Las pruebas del laboratorio solo verifican sus ejercicios originales; no prueban R1–R7. Los fragmentos de los otros proyectos no tienen ejecución independiente prometida.

Para comprobar manualmente el laboratorio original copiado, desde la raíz de LM_P3:

```sh
python3 -B -m unittest discover -s bases/tdlc_lab12 -p 'test_interfaz.py' -v
```

Para abrir **únicamente la interfaz original del laboratorio**, si se necesita como referencia técnica:

```sh
python3 -B bases/tdlc_lab12/interfaz.py
```

Ese comando abre un servidor local y navegador hasta detenerlo con Ctrl+C. No es el comando final de LM_P3. Los lanzadores originales crean su `.venv` dentro de la copia al ejecutarse; se conservaron pero no se ejecutaron durante la transferencia.
