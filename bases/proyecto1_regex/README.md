# Proyecto No. 1 — Teoría de la Computación (Grupo 4)

**Universidad del Valle de Guatemala**  
**Facultad de Ingeniería**  
**Departamento de Ciencias de la Computación**  
**Curso:** Teoría de la Computación

## Descripción

Este proyecto implementa un analizador de expresiones regulares:

1. **Generación de AFN (Algoritmo de Thompson):** El programa lee expresiones en notación *infix*, aplica el algoritmo Shunting Yard para obtener la notación *postfix*, construye el Árbol Sintáctico Abstracto (AST) y lo recorre para generar el AFN correspondiente.
2. **Generación de AFD (Construcción de Subconjuntos):** A partir del AFN generado, el programa aplica el algoritmo de subconjuntos para construir un Autómata Finito Determinista (AFD) equivalente.
3. **Minimización de AFD (Algoritmo de Particiones):** A partir del AFD, se utiliza el algoritmo de particiones (Hopcroft) para agrupar estados equivalentes, produciendo un AFD minimizado.
4. **Graficación y Simulación:** Se grafican los tres autómatas resultantes (AFN, AFD, AFD Minimizado) mediante Graphviz. Finalmente, simula los tres autómatas sobre una cadena `w` ingresada por el usuario para validar si `w ∈ L(r)`.

**Enlace al video de presentación:** https://youtu.be/OpOprGdOk6E

## Estructura del repositorio

```text
.
├── README.md
├── main.py                     # Script principal del programa
├── expresiones.txt             # Archivo de entrada con las expresiones regulares
├── automata/                   # Lógica de estados, AFN (Thompson), AFD (Subconjuntos) y Minimización
├── regex/                      # Lógica de Shunting Yard y Árbol Sintáctico Abstracto (AST)
├── visualization/              # Renderizado gráfico de autómatas mediante Graphviz
└── *.png                       # Autómatas generados (AFN, AFD, AFD Minimizado)
```

## Expresiones regulares de prueba

El programa procesa las expresiones del archivo `expresiones.txt`:

1. `(a*|b*)+`
2. `((ε|a)|b*)*`
3. `(a|b)*abb(a|b)*`
4. `0?(1?)?0*`

## Autómatas Generados

El programa genera tres imágenes PNG por cada expresión analizada, correspondientes a los diferentes algoritmos implementados.

| AFN (Thompson) | AFD (Subconjuntos) | AFD (Minimizado) |
|:---:|:---:|:---:|
| `afn_expresion_X.png` | `afd_subconjuntos_expresion_X.png` | `afd_minimizado_expresion_X.png` |

*(Las imágenes se guardan automáticamente en el directorio principal al ejecutar el programa)*

## Ejemplos de cadenas de prueba

Al ejecutar el programa, por cada expresión se solicita una cadena `w` en consola y se indica si `w ∈ L(r)` (`sí`/`no`) en el AFN, AFD y AFD Minimizado, comparando los tres resultados.

| Expresión | Cadena `w` | ¿Aceptada? | Motivo |
|:---:|:---:|:---:|---|
| `(a*\|b*)+` | `` (vacía) | sí | equivalente a `(a\|b)*`, acepta la cadena vacía |
| `(a*\|b*)+` | `aabb` | sí | cualquier combinación de `a` y `b` |
| `(a*\|b*)+` | `aabbc` | no | contiene `c`, símbolo fuera del alfabeto |
| `((ε\|a)\|b*)*` | `abab` | sí | equivalente a `(a\|b)*` |
| `((ε\|a)\|b*)*` | `bbba` | sí | cualquier combinación de `a` y `b` |
| `((ε\|a)\|b*)*` | `abc` | no | contiene `c`, símbolo fuera del alfabeto |
| `(a\|b)*abb(a\|b)*` | `abb` | sí | contiene la subcadena `abb` |
| `(a\|b)*abb(a\|b)*` | `ababbab` | sí | contiene `abb` en la posición 3-5 |
| `(a\|b)*abb(a\|b)*` | `aab` | no | no contiene la subcadena `abb` |
| `(a\|b)*abb(a\|b)*` | `` (vacía) | no | no contiene `abb` |
| `0?(1?)?0*` | `` (vacía) | sí | los tres bloques opcionales pueden ser vacíos |
| `0?(1?)?0*` | `0100` | sí | `0` (opcional) + `1` (opcional) + `00` (`0*`) |
| `0?(1?)?0*` | `10` | sí | `1` (opcional) + `0` (`0*`) |
| `0?(1?)?0*` | `001` | no | el `1` no puede ir precedido de dos `0` |
| `0?(1?)?0*` | `011` | no | solo se permite un `1` en toda la cadena |

## Sintaxis de expresiones regulares

El analizador admite los operadores de unión (`|`), concatenación implícita,
cerradura de Kleene (`*`), cerradura positiva (`+`), opcional (`?`) y
paréntesis para agrupación. El símbolo `ε` representa exclusivamente la cadena
vacía; por ello no forma parte del alfabeto ni puede consumirse como un carácter
de la cadena de entrada `w`.

Los caracteres que coinciden con operadores pueden utilizarse como literales
mediante una barra invertida. Por ejemplo, `\|`, `\*`, `\+`, `\?`, `\(`,
`\)`, `\\` y `\^` representan sus caracteres literales correspondientes. El
carácter `^` sin escapar no está soportado y el programa informa el error de
forma explícita.

## Requisitos

- Python 3.10 o superior
- Graphviz instalado en el sistema
- Dependencias de Python definidas en `requirements.txt`

### Instalación de Graphviz

En Ubuntu o Debian:
```bash
sudo apt-get update
sudo apt-get install graphviz
```

En macOS con Homebrew:
```bash
brew install graphviz
```

En Windows, descarga Graphviz desde su [sitio oficial](https://graphviz.org/download/) y agrega su carpeta `bin` al `PATH` durante la instalación.

## Preparación y ejecución

1. Clona el repositorio y entra en su directorio:

   ```bash
   git clone git@github.com:Pxdro-410/proy1Teoria---G4.git
   cd proy1Teoria---G4
   ```

2. Crea y activa un entorno virtual según tu sistema operativo:

   En macOS:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   En Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   En Windows (PowerShell):
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instala las dependencias de Python:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. Ejecuta el programa principal:
   ```bash
   python main.py
   ```

También se puede indicar otro archivo de entrada explícitamente:
```bash
python main.py expresiones.txt
```

## Pruebas automatizadas

La suite de pruebas utiliza la biblioteca estándar `unittest` y valida la
conversión de expresiones, la construcción de AFN y AFD, la minimización, la
simulación y la generación de los tres gráficos. Para ejecutarla:

```bash
python -m unittest discover -v
```

## Integrantes del Grupo 4

- Diego Calderón - 241263
- Pedro Caso - 241286
- Hugo Méndez - 241265
