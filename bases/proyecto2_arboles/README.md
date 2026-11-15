# Analizador CYK — Grupo 4

Aplicación gráfica para cargar gramáticas libres de contexto, convertirlas a
Forma Normal de Chomsky y decidir si una oración en inglés o una expresión
aritmética pertenece al lenguaje. La salida incluye la tabla CYK, el tiempo de
ejecución y, para cadenas aceptadas, el árbol sintáctico.

> Link del video: https://youtu.be/jR-_ONeF5gM 

## Inicio rápido

Requiere Python 3.10 o posterior con soporte para Tkinter.

### 1. Requisitos previos de Tkinter por sistema operativo

Tkinter suele estar incluido por defecto, pero en algunas distribuciones o gestores de paquetes se distribuye por separado. Puedes verificar si está disponible ejecutando:

```bash
python -m tkinter
```
*(Debe abrirse una pequeña ventana de demostración. Puedes cerrarla para continuar).*

Si no está instalado o arroja un error (`No module named '_tkinter'`), instálalo según tu sistema operativo:

- **Windows**:
  Viene incluido por defecto en el instalador oficial de [python.org](https://www.python.org/). Si falta, vuelve a ejecutar el instalador de Python, selecciona **Modify** y asegúrate de marcar la casilla **"tcl/tk and IDLE"**.

- **macOS**:
  - Si instalaste Python desde el instalador oficial de [python.org](https://www.python.org/), Tkinter ya viene incluido.
  - Si usas **Homebrew**, instala el paquete correspondiente a tu versión:
    ```bash
    brew install python-tk@3.14   # o python-tk@3.13 / python-tk@3.12 según corresponda
    ```

- **Linux**:
  - **Debian / Ubuntu**:
    ```bash
    sudo apt update && sudo apt install python3-tk
    ```
  - **Fedora / RHEL**:
    ```bash
    sudo dnf install python3-tkinter
    ```
  - **Arch Linux**:
    ```bash
    sudo pacman -S tk
    ```

### 2. Entorno virtual (.venv) e instalación

Se recomienda crear y activar un entorno virtual para aislar las dependencias:

**En macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**En Windows (Command Prompt o PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> **Nota sobre `.env` / variables de entorno:** Este proyecto **no requiere** un archivo `.env` ni configuración de claves o variables de entorno, ya que el analizador funciona 100% de manera local con las gramáticas en `data/grammars/`.

Una vez activado el entorno, inicia la aplicación:
```bash
python main.py
```

> **Nota de intérprete:** Si tienes múltiples versiones de Python, crea el entorno con la versión que tenga soporte para Tkinter (por ejemplo, `python3.14 -m venv .venv` o `py -3.14 -m venv .venv`).

### 3. Uso de la aplicación gráfica

La ventana permite elegir entre la gramática inglesa y la aritmética. Después de analizar una cadena:
- Se muestra el resultado (**ACEPTADA** o **RECHAZADA**), tokens normalizados y tiempo de ejecución.
- Se presenta la **Tabla CYK** y, en caso de aceptación, el **Árbol sintáctico** jerárquico. Ambas vistas cuentan con barras de desplazamiento para entradas largas.
- El botón **Exportar DOT** permite guardar el árbol en formato Graphviz (`.dot`).

### 4. Interfaz de consola alternativa (CLI)

Si prefieres trabajar directamente desde la terminal o estás en un entorno sin entorno gráfico:

```bash
python -m src.ui.cli
```

### 5. Exportación y visualización del árbol (formato DOT / Graphviz)

El formato **DOT** es un lenguaje estándar de texto plano creado por **Graphviz** para describir grafos y estructuras jerárquicas mediante nodos y aristas dirigidas.

Cuando una cadena es aceptada por la gramática, puedes exportar el árbol sintáctico a un archivo `.dot` (usando el botón **Exportar DOT** en la GUI o indicando una ruta en la CLI):

- **Generación nativa:** La aplicación genera el archivo `.dot` directamente sin requerir que tengas Graphviz o librerías de C++ instaladas en tu sistema.
- **Renderizar a imagen (PNG / SVG / PDF):** Si tienes [Graphviz](https://graphviz.org/) instalado en tu computadora, puedes convertir el archivo generado en una imagen con una sola línea de comando:
  ```bash
  # Generar imagen PNG:
  dot -Tpng arbol.dot -o arbol.png

  # Generar imagen vectorial SVG:
  dot -Tsvg arbol.dot -o arbol.svg
  ```
- **Visores web en línea (sin instalar nada):** Puedes abrir el archivo `.dot`, copiar su contenido y pegarlo en visores web interactivos como [Graphviz Online](https://dreampuf.github.io/GraphvizOnline/) o [Edotor](https://edotor.net/) para visualizar el árbol de derivación de inmediato.

Ejemplos:

- Inglés válido: `She eats a cake with a fork`
- Inglés inválido: `The cat eats a cake fork`
- Aritmética válida: `(left * right) + total`
- Aritmética inválida: `left + * right`

## Pruebas

```bash
python -m unittest discover -v
```

La suite cubre el lector y simplificador de gramáticas, tokenización, tabla CYK,
reconstrucción y renderizado del árbol, exportación DOT, presentación gráfica y
el flujo de la CLI alternativa.

## Arquitectura

- `src/grammar/`: modelos, lectura y conversión de gramáticas a CNF.
- `src/cyk/`: tokenización, algoritmo CYK y reconstrucción por backpointers.
- `src/ui/gui.py`: ventana Tkinter, tabla y árbol interactivos.
- `src/ui/cli.py`: integración compartida y menú de consola alternativo.
- `src/ui/tree_visualizer.py`: árbol jerárquico y exportación DOT.
- `data/grammars/`: gramáticas inglesa y aritmética.
- `tests/`: pruebas unitarias y de integración.
- `docs/informe_tecnico.md`: diseño, obstáculos y análisis de rendimiento.

## Integrantes — Grupo 4

- **Diego Calderón** — 241263
- **Pedro Caso** — 241286
- **Hugo Méndez** — 241265

