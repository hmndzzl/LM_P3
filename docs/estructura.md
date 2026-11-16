# Estructura común del proyecto

## Estado y convención

Esta es la estructura acordada para que los tres miembros trabajen en las mismas rutas. La estructura fue creada inicialmente con paquetes vacíos. **M1 implementó modelos, motor, frontera defensiva, comparación y servicio; M2 aporta lexer/parser, variables libres y validación integral/externa por filas**; ver [semantica.md](semantica.md), [sintaxis.md](sintaxis.md) y [validacion.md](validacion.md). Codec, servidor e interfaz siguen pendientes de M3, junto con las revisiones humanas. Los nombres de archivos detallados a continuación son destinos previstos: solo se crean cuando el ticket correspondiente los necesite. No crear funciones vacías que aparenten cumplimiento.

Python 3.10 o posterior como mínimo inicial, coherente con los proyectos de referencia; registrar la versión concreta usada por el equipo en H0. Frontend con HTML/CSS/JavaScript nativos, servido localmente por Python. No hay dependencias externas nuevas ni paso de compilación del frontend. El paquete está en la raíz para poder importarlo y ejecutar pruebas desde allí sin modificar `sys.path` ni exigir instalación editable.

## Mapa de carpetas

```text
LM_P3/

├── README.md                  Entrada al proyecto y comandos verificados
├── .gitignore
├── lm_p3/                     Código Python propio
│   ├── __init__.py
│   ├── models/                Tipos compartidos, sin evaluación ni HTTP
│   ├── syntax/                Lexer, parser y variables libres — M2
│   ├── validation/            Interpretación y entorno válidos — M2
│   ├── semantics/             Evaluación, trazas y comparación — M1
│   ├── application/           Orquestación del caso de uso — M1 + M2
│   └── server/                HTTP local y serialización JSON — M3
├── frontend/                  Interfaz propia — M3
│   ├── css/                   Tokens y estilos de DESIGN.md
│   ├── js/                    Interacción, estado, API y evidencia
│   └── assets/                Solo recursos locales realmente necesarios
├── tests/                     Pruebas nuevas de LM_P3
│   ├── syntax/                M2
│   ├── validation/            M2
│   ├── semantics/             M1
│   ├── application/           M1; revisión de M2
│   ├── server/                M3
│   ├── integration/           Flujos entre módulos — los tres
│   ├── ui/                    Casos y pruebas de navegador — M3
│   └── fixtures/              Datos de prueba compartidos
├── examples/                  Escenarios válidos/erróneos para enseñar y demostrar
├── scripts/                   Lanzadores propios macOS/Windows — M3
├── docs/
│   ├── estructura.md          Este mapa y sus límites
│   ├── contratos.md           Contratos entre miembros
│   └── evidencias/            Capturas y comprobaciones reales
└── bases/                     Copias originales intactas; fuera del producto
```

Los `__init__.py` vacíos identifican paquetes de Python y permiten descubrimiento estándar de pruebas. Los `.gitkeep` conservan carpetas vacías cuando una persona haga el commit; eliminarlos al añadir contenido real en su directorio. No contienen lógica ni son pruebas de funcionalidad.

## Archivos previstos y responsables

Crear únicamente los necesarios para el ticket actual; dividir un módulo cuando acumule responsabilidades, no preventivamente en decenas de archivos.

| Ruta prevista | Contenido | Autor principal y coordinación |
| --- | --- | --- |
| `lm_p3/models/language.py` | Símbolos, lenguaje e interpretación | M2; revisar con M1 |
| `lm_p3/models/ast.py` | Términos/fórmulas, alcance y posición | M2; revisar con M1 |
| `lm_p3/models/errors.py` | Errores estructurados y ubicaciones | M2; revisar con M3 |
| `lm_p3/models/trace.py` | Evidencias/resultados de evaluación | M1; revisar con M3 |
| `lm_p3/syntax/lexer.py` | Tokens preservando nombre y posición | M2 |
| `lm_p3/syntax/parser.py` | AST con gramática documentada | M2 |
| `lm_p3/syntax/free_variables.py` | Conjunto de variables libres por alcance | M2 |
| `lm_p3/validation/validator.py` | Validación integral y entrada validada | M2 |
| `lm_p3/validation/normalization.py` | Builders de declaraciones/tablas/entorno por filas; comprueban conflictos antes de crear mapas | M2; codec M3 los consume |
| `lm_p3/semantics/evaluator.py` | Términos, conectivos, cuantificadores y traza | M1 |
| `lm_p3/semantics/comparison.py` | Comparar base y variante válidas | M1 |
| `lm_p3/application/service.py` | Analizar → validar → evaluar; sin HTTP | M1 integra; M2 aporta funciones de análisis/validación |
| `lm_p3/server/http.py` | Servidor loopback, rutas y protección de frontera | M3 |
| `lm_p3/server/codec.py` | JSON ↔ modelos; errores de forma/tipo | M3 con contrato de M2/M1 |
| `lm_p3/__main__.py` | Punto único de arranque; delega en servidor | M3, durante M3-01 |
| `frontend/index.html` | Estructura semántica y editor gráfico | M3 |
| `frontend/css/tokens.css` | Valores únicos del sistema visual | M3 |
| `frontend/css/styles.css` | Componentes y layout responsive | M3 |
| `frontend/js/app.js` | Inicialización y eventos de pantalla | M3 |
| `frontend/js/api.js` | Peticiones JSON y manejo de transporte | M3 |
| `frontend/js/state.js` | Estado de edición y revisiones | M3 |
| `frontend/js/evidence.js` | Presentación/navegación de trazas | M3 |
| `scripts/abrir_interfaz.command`, `scripts/abrir_interfaz.bat` | Lanzadores adaptados a la raíz y punto de entrada | M3 |

Los modelos compartidos no son una cuarta tarea sin dueño. Cada archivo tiene el autor indicado, los otros consumen el contrato y proponen cambios mediante revisión. Evitar ediciones simultáneas del mismo archivo. Si un modelo puede permanecer pequeño dentro de uno de estos módulos, acordarlo antes de introducir otro archivo.

## Dirección de dependencias

```text
Navegador (frontend) ──JSON/HTTP──> server ──> application
                                               ├──> syntax
                                               ├──> validation
                                               └──> semantics
Todos los módulos Python anteriores ──> models
```

- `models` no importa módulos del servidor, sintaxis, validación ni evaluación. Solo representa datos e invariantes estructurales acordados.
- `syntax`, `validation` y `semantics` no importan UI/HTTP ni se llaman circularmente. El servicio encadena sus resultados; la validación puede recibir AST/variables libres ya calculados.
- `semantics` recibe una entrada validada y produce resultado/traza. No vuelve a analizar texto ni toma entradas de `input()`.
- `application` coordina y no contiene widgets, JSON de transporte ni algoritmos semánticos duplicados.
- `server` valida formato/tipos externos con `codec`, invoca el servicio y serializa la respuesta. La validez lógica integral es responsabilidad del módulo `validation`.
- El frontend usa API relativa del mismo origen; no duplica cálculo de verdad ni importa archivos Python. La validación inmediata de formularios es ayuda adicional.
- Ningún módulo del producto importa `bases/`, `tests/` o scripts de lanzadores. No añadir CYK ni autómatas para resolver imports heredados.
- Resolver archivos estáticos/ejemplos desde la ubicación del paquete/proyecto, nunca suponiendo un directorio de trabajo arbitrario. Servir solo archivos permitidos de `frontend/`; no exponer la raíz, `bases/` ni documentos por HTTP.

## Convenciones comunes

- Módulos/rutas Python en inglés `snake_case`; clases `PascalCase`, funciones/variables `snake_case`. JavaScript en `camelCase`; mensajes y documentación de usuario en español. Conservar los nombres que el usuario declara en su lenguaje sin traducirlos.
- No llamar archivos propios `ast.py` o `http.py` en la raíz: se confundirían con bibliotecas estándar. Los nombres dentro de paquetes, como `lm_p3.models.ast`, se usan con imports absolutos del paquete.
- Usar imports `from lm_p3...`; no manipular `sys.path`, no depender de importar desde la carpeta de otro miembro y no crear `utils.py` como contenedor de todo.
- Comentarios de código en español; usar `#` para comentarios de una línea, sin docstrings de una línea. Funciones públicas tipadas y contrato documentado. Sin estado global mutable de interpretación/entorno: cada solicitud tiene su contexto.
- HTML, CSS y JS en archivos separados. CSS consume tokens comunes; no copiar el estilo del laboratorio. En JS emplear módulos nativos cuando se creen los archivos y mantener compatibilidad con la política de contenido del servidor.
- Ejemplos en `examples/` describen escenarios completos; fixtures de resultados esperados y casos de borde van en `tests/fixtures/`. Documentar su formato en contratos antes de llenarlos. No compartir un archivo mutable como almacenamiento de sesión.
- Pruebas Python `test_*.py`, basadas inicialmente en `unittest`. No usar esos nombres para scripts de demo. Las pruebas de interfaz deben estar claramente diferenciadas de pruebas de datos/serialización.
- Evidencia en `docs/evidencias/` con ticket, procedimiento, resultado real y limitaciones; no incluir entornos virtuales, secretos ni archivos generados masivos. No afirmar que una captura es prueba de todo el flujo.

## Comandos y estado real

Desde la raíz, con Python 3.10+:

```sh
python3 -m venv .venv
# Activar según el sistema; usar después el intérprete del entorno.
python -m unittest discover -s tests -t . -v
```

El comando de pruebas apunta solo a `tests/`, por lo que no incorpora pruebas heredadas. La suite propia cubre motor, parser, validación externa/integral y su integración; no equivale a cobertura HTTP ni de interfaz. En Windows puede invocarse el intérprete `.venv/Scripts/python.exe` directamente. No se requiere instalar dependencias externas ahora.

Comando objetivo de aplicación, **todavía no disponible**: `python -m lm_p3`. M3 creará `lm_p3/__main__.py` en M3-01; hasta entonces no añadir un arranque que muestre resultados simulados. Los lanzadores propios se crean en `scripts/`, calculando la raíz como padre de esa carpeta. Los lanzadores guardados en `bases/` siguen abriendo el laboratorio original.

No agregar un `requirements.txt`, `package.json`, framework ni configuración de empaquetado vacío por apariencia: hacerlo solo si una necesidad real y acordada lo requiere. Si aparecen dependencias, fijar y documentar cómo instalarlas antes de pedir al grupo que las use.

## Encaje con los tickets y control de cambios

H0 fija este mapa, y [contratos.md](contratos.md) cierra modelos y fronteras antes de consumidores incompatibles. M2-01/02 construye `models`/`syntax`; M2-03 `validation`; M1-01/02 `semantics` y su frontera normalizada `semantics/inputs.py`; M1/M2 integran `application`; M3-01 crea `server`, frontend mínimo y entrada. M1-03 añade comparación; M3-02/03 completa interacción y evidencia. Cada uno agrega sus pruebas/documentación durante su ticket.

La entrega de implementación de M1 está descrita en semantica.md; la integración con M2/M3 y las revisiones humanas continúan pendientes. Mantener las 15 unidades estimadas por persona y recalibrar en H1 si integración/modelos modifican la carga real. Un cambio de ruta compartida requiere actualizar este mapa, contratos, imports, comandos y las guías afectadas en la misma entrega revisable. Los humanos gestionan ramas y commits según AGENTS.md.
