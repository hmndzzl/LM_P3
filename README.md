# LM_P3 — Evaluador semántico

Proyecto de MM3032 Lógica Matemática: aplicación gráfica para evaluar fórmulas sobre interpretaciones finitas y explicar sus resultados.

## Estado actual

El motor de M1 y los módulos de sintaxis/validación integral de M2 están implementados, con integración Python real desde texto y filas externas. El parser acepta la notación y los alias confirmados por el usuario; ver [sintaxis](docs/sintaxis.md) y [validación](docs/validacion.md). El codec JSON/HTTP, servidor e interfaz propios siguen pendientes de M3, junto con las revisiones humanas. Aún no existe una aplicación gráfica ejecutable: `python -m lm_p3` depende de M3. Las copias de `bases/` siguen intactas y no equivalen a requisitos cumplidos.

## Documentos para comenzar

- [Estructura común](docs/estructura.md): rutas, responsabilidades, dependencias y comandos.
- [Contratos entre módulos](docs/contratos.md): contrato Python de M1 y revisión pendiente con M2/M3.
- [Motor semántico](docs/semantica.md): API, demostración ejecutable, límites y guía de defensa.
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

El ejemplo construye AST directamente; no sustituye la integración pendiente con el parser y la interfaz. Los casos se calculan con el motor real, sin respuestas prefijadas.

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

La preparación de defensa y la revisión de M3 se encuentran en la guía de casos y la matriz general. Enseñanza mutua, revisión humana, uso con compañeros y pruebas gráficas siguen pendientes. Esta entrega no marca los tickets globalmente aceptados.
