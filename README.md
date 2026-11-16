# LM_P3 — Evaluador semántico

Proyecto de MM3032 Lógica Matemática: aplicación gráfica para evaluar fórmulas sobre interpretaciones finitas y explicar sus resultados.

## Estado actual

El motor de M1, la sintaxis/validación de M2 y la implementación técnica de M3 están conectados: editores gráficos, botones lógicos, resultados con evidencia navegable y comparación de un cambio. La aplicación se llama **Evaluador semántico**. Las revisiones humanas, el ensayo de defensa y la comprobación en otros sistemas siguen pendientes. Las copias de `bases/` siguen intactas.

## Ejecutar la aplicación

Desde la raíz, con Python 3.10 o posterior y sin paquetes adicionales:

```sh
python3 -B -m lm_p3
```

Se abre el navegador en la dirección local impresa en consola. Para cerrar el servidor,
presiona Ctrl+C. En Windows puede utilizarse `py -3 -B -m lm_p3`.
Para elegir puerto o abrir el navegador manualmente:

```sh
python3 -B -m lm_p3 --no-browser --port 8765
```

Elige uno de los nueve ejemplos de tus notas y pulsa **Cargar ejemplo**.
El primero, `P(x)` con x: 1, da Verdadero; con x: 3 da Falso. Cada ejemplo
indica su página del PDF y propone un cambio para probar. **Limpiar todo** borra
fórmula, lenguaje, dominio, tablas, asignaciones, resultados y comparación.
También puedes añadir tus propios símbolos y filas. El dominio se introduce
con un elemento por línea.
Puedes escribir con teclado o insertar símbolos desde la barra, conservando cursor,
selección y deshacer/rehacer. Las tuplas y salidas usan selectores del dominio.

La fórmula, las asignaciones y el resultado ocupan la zona principal. El resumen
del mundo permanece visible; para modificar sus datos abre **Lenguaje** o
**Dominio y tablas**. Un error abre automáticamente la sección correspondiente.

Después de evaluar, **Comparar un cambio** permite modificar una salida funcional,
la pertenencia de una tupla o una asignación libre sobre una copia. La base se
conserva y se recalculan ambos escenarios. El fondo matemático está activo por
defecto y respeta la preferencia de movimiento reducido del sistema.

Lanzadores alternativos: `scripts/abrir_interfaz.sh` en Linux,
`scripts/abrir_interfaz.command` en macOS y `scripts/abrir_interfaz.bat` en Windows.
Todos resuelven la raíz del proyecto. El arranque POSIX está probado en Linux;
la ejecución nativa en macOS/Windows necesita revisión del equipo.

Recorrido del código y límites de esta entrega: [interfaz y servidor](docs/interfaz.md).

## Documentos para comenzar

- [Estructura común](docs/estructura.md): rutas, responsabilidades, dependencias y comandos.
- [Contratos entre módulos](docs/contratos.md): contrato Python de M1 y revisión pendiente con M2/M3.
- [Motor semántico](docs/semantica.md): API, demostración ejecutable, límites y guía de defensa.
- [Interfaz de M3](docs/interfaz.md): ejecución, funciones principales, pruebas y pendientes.
- [Sintaxis de M2](docs/sintaxis.md): gramática, alias, alcance, nombres, errores y API para M1/M3.
- [Validación de M2](docs/validacion.md): builders por filas, totalidad, duplicados, entorno y errores agrupados.
- [Casos y defensa M2](docs/casos-didacticos.md): soluciones razonadas, 24 casos ejecutables y preparación de exposición.
- [Evidencia M2](docs/evidencias/miembro-2.md): resultados reproducibles de las cuatro entregas en un solo informe.
- [Matriz general de verificación](docs/matriz-verificacion.md): requisitos y revisión pendiente de M3.

- [Bases transferidas](bases/README.md) y [manifiesto de integridad](bases/MANIFEST.json).

## Base técnica elegida

Python con servidor HTTP local y HTML/CSS/JavaScript en el navegador, comunicados mediante JSON. Se reutiliza el patrón técnico de TDLC_LAB12; el diseño visual del producto seguirá DESIGN.md. Los fragmentos de proyectos anteriores sirven como referencias seleccionadas para sintaxis y árboles.

Cada miembro hará las adaptaciones de su parte en las rutas de `docs/estructura.md`, fuera de `bases/`, después de cerrar contratos en H0. La copia completa del laboratorio conserva su funcionamiento previo; consultar su inventario para distinguir pruebas/comandos del laboratorio de los futuros del evaluador.

## Comprobar la entrega de Miembro 1

Con Python 3.10 o posterior, desde la raíz y sin dependencias externas:

```sh
python -B -m unittest discover -s tests -t . -v
python -B -m examples.semantica
python -B -m examples.semantica --json
python -B -m examples.semantica --benchmark
```

El ejemplo construye AST directamente para estudiar M1; la aplicación gráfica usa
el parser real de M2. Los casos se calculan sin respuestas prefijadas.

## Comprobar texto real con la entrega de M2

Desde la raíz, usando el intérprete del entorno virtual:

```powershell
python -X utf8 -B -m unittest discover -s tests -t . -v
python -X utf8 -B -m examples.sintaxis
```

En Windows también se puede invocar `.\.venv\Scripts\python.exe` directamente. `-X utf8` permite imprimir símbolos lógicos en consolas cuyo valor predeterminado es CP1252. No hay dependencias externas que instalar ni se requiere `requirements.txt`.

Esta segunda demo analiza texto con `syntax.parser.parse`, proporciona un entorno explícito en el caso abierto y evalúa con el motor real. El servicio utiliza `validate_input` de M2 por defecto, que comprueba el contexto completo y certifica con `prepare_input` de M1.

Para comprobar filas externas y errores múltiples:

```powershell
python -X utf8 -B -m examples.validacion
```

Esta demo pasa por los builders de M2 antes de crear mapas/modelos, muestra una evaluación válida y rechaza tablas vacías/salidas contradictorias sin asignar verdad. No acredita integración HTTP ni pruebas de interfaz.

## Corpus, comparación y preparación de defensa

```powershell
python -X utf8 -B -m examples.corpus
python -X utf8 -B -m examples.corpus --case Q03 --json
python -X utf8 -B -m examples.corpus --case C02
python -X utf8 -B -m examples.corpus --case E03
```

El corpus contiene 10 fórmulas, 3 comparaciones de un cambio y 11 entradas inválidas con reparaciones comprobadas. Q01–Q04 cubren los cuatro resultados cuantificados; C02 conserva la verdad y cambia el testigo. Toda salida se calcula con el código real, sin leer las expectativas de pruebas. Los ejemplos no modifican su mundo base.

La preparación de defensa y el recorrido de código están en [la guía de M3](docs/interfaz.md).
Resultados y capturas: [evidencia M3](docs/evidencias/miembro-3.md).
Enseñanza mutua, revisión humana y aceptación global siguen pendientes.
