# TDLC_LAB12

Laboratorio 12 de Teoría de la Computación.

## Video de demostración

https://youtu.be/L5krAgzeaz4 

<!-- Reemplazar la línea anterior por: [Ver video de demostración](URL_DEL_VIDEO) -->

## Dos formas de usar el laboratorio

- **Interfaz visual:** abre `abrir_interfaz.command` con doble clic en macOS
  o `abrir_interfaz.bat` en Windows. Se crea `.venv` si todavía no existe y
  se abre el laboratorio en el navegador predeterminado. Debe haber Python 3
  instalado. Conserva abierta la ventana del lanzador mientras lo utilizas;
  para terminar, ciérrala o presiona Ctrl+C y cierra la pestaña del navegador.
- **Terminal:** activa `.venv` y ejecuta `python main.py`.

En la interfaz visual, selecciona el ejercicio en el menú lateral. Puedes
usar **Datos de ejemplo** o elegir **Mis datos** para editar las listas.
Indica la clave o el exponente cuando corresponda y pulsa **Calcular resultado**.
El resultado aparece a la derecha en pantallas grandes o debajo en pantallas
pequeñas. **Copiar** copia la lista y **Restablecer** recupera el ejemplo.
Al cambiar los datos se limpia el resultado anterior.

La interfaz conserva por separado tus datos propios y los de ejemplo al
alternar entre ellos o cambiar de ejercicio mientras la página está abierta.
**Restablecer ejemplo** permite recuperar las entradas anteriores con
**Deshacer**, incluso después de visitar otro ejercicio. Esta opción permanece
hasta usarla o editar los datos tras el restablecimiento.
Recargar o cerrar la página descarta las entradas. Puedes calcular con
Ctrl+Enter (Cmd+Enter en macOS); los errores indican el campo que debes
corregir y se pueden recorrer con el teclado.

También puedes abrir la interfaz visual con el entorno activado, en
macOS, Linux o Windows:

```bash
python interfaz.py
```

Se abre una dirección local `http://127.0.0.1:PUERTO` en el navegador. Si no
se abre automáticamente, utiliza la dirección que muestra el programa.
Funciona sin Internet y no guarda las entradas. No requiere paquetes
adicionales. Los archivos visuales están en la carpeta `interfaz/`;
los cálculos siguen usando las funciones de `ejercicio1.py` a `ejercicio4.py`.

## Preparar el entorno y ejecutar el laboratorio

Se necesita Python 3. Abrir una terminal en la carpeta del laboratorio y
seguir los pasos correspondientes al sistema operativo. El entorno `.venv`
debe crearse en cada equipo; no se copia entre macOS, Linux y Windows.

### macOS y Linux

Crear el entorno virtual (solo la primera vez):

```bash
python3 -m venv .venv
```

Activarlo cada vez que se abra una terminal nueva:

```bash
source .venv/bin/activate
```

### Windows

Crear el entorno virtual (solo la primera vez), desde PowerShell o CMD:

```powershell
py -3 -m venv .venv
```

Si el comando `py` no está disponible, usar `python -m venv .venv`,
comprobando antes con `python --version` que corresponde a Python 3.

Activar el entorno cada vez que se abra una terminal nueva.

En **PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

En **CMD**:

```bat
.venv\Scripts\activate.bat
```

Si PowerShell bloquea el script de activación, se puede usar CMD o ejecutar
el intérprete del entorno directamente, como se muestra más abajo.

### Ejecutar los ejercicios (todos los sistemas)

Con el entorno activado, abrir el menú principal con el mismo comando
en macOS, Linux o Windows:

```bash
python main.py
```

Seleccionar una opción del `1` al `4` para ejecutar un ejercicio, o `0`
para salir. Al terminar cada ejercicio se vuelve al menú principal.
Las opciones inválidas muestran un mensaje y permiten intentar de nuevo.

Cada archivo `ejercicioX.py` contiene únicamente la función del ejercicio.
El menú de terminal, las entradas y las salidas se manejan en `main.py`.
`interfaz.py` ofrece la alternativa visual con las mismas funciones de cálculo.

Después de elegir un ejercicio, seleccionar `1` para usar los datos de
ejemplo del enunciado o `2` para ingresar datos propios.

Escribir las listas con corchetes y los textos entre comillas. Por ejemplo:

| Ejercicio | Datos propios de ejemplo | Entrada adicional |
| --- | --- | --- |
| 1 | `[{"nombre": "Ana", "edad": 20}, {"nombre": "Luis", "edad": 18}]` | Clave: `edad` |
| 2 | `[-2, 0, 5]` | Exponente: `2` |
| 3 | `[[1, 2, 3], [4, 5, 6]]` | Ninguna |
| 4 | `['rojo', 'azul', 'rojo']` | Lista a borrar: `['rojo']` |

En el ejercicio 1, la clave debe existir en todos los diccionarios y sus
valores deben ser comparables. Enter sin escribir una clave usa `model`.
En el ejercicio 2, los elementos deben ser enteros y el exponente debe ser
un entero positivo; Enter usa `3`. En el ejercicio 3, todas las filas deben
ser listas de números y tener la misma longitud. Se aceptan listas vacías.

Las entradas se leen con `ast.literal_eval`, que interpreta datos sin
ejecutar código. Si una entrada es inválida, se muestra el motivo y se
regresa al menú principal.

Los cuatro ejercicios utilizan únicamente la biblioteca estándar de Python;
no es necesario instalar paquetes con `pip`. La carpeta `.venv/` está
excluida de Git mediante `.gitignore`.

Para salir del entorno:

```bash
deactivate
```

### Ejecutar sin activar el entorno

En macOS o Linux:

```bash
.venv/bin/python main.py
```

En Windows, desde PowerShell o CMD:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Ejercicio 1

Ordenar una lista de diccionarios por una clave indicada usando una función
`lambda`. La solución está en `ejercicio1.py` y usa `sorted()` para devolver
una nueva lista sin modificar la original.

### Requisitos y ejecución

Con el entorno `.venv` activado:

```bash
python main.py
```

Elegir la opción `1` del menú y luego el origen de los datos. Con los datos
de ejemplo se puede ordenar por `make`, `model` o `color`. Con datos propios
se puede indicar cualquier clave de texto presente en todos los diccionarios.
El orden es ascendente: numérico para números y alfabético para textos.

### Ejemplo

Al ingresar `model`, se obtiene:

```text
Lista ordenada por model:
{'make': 'Apple', 'model': 2, 'color': 'Silver'}
{'make': 'Samsung', 'model': 7, 'color': 'Blue'}
{'make': 'Huawei', 'model': 50, 'color': 'Gold'}
{'make': 'Nokia', 'model': 216, 'color': 'Black'}
```

La función `obtener_valor = lambda diccionario: diccionario[clave]` indica
qué valor debe comparar `sorted()` al ordenar los diccionarios. El resultado
se guarda en `lista_ordenada` antes de devolverlo.

## Ejercicio 2

Calcular la potencia n-ésima de cada elemento de una lista de enteros usando
una función `lambda`. La solución está en `ejercicio2.py` y recibe el
exponente como argumento de `calcular_potencias(lista, n)`.

### Ejecución

```bash
python main.py
```

Elegir la opción `2` del menú.

Se puede usar la lista de ejemplo del 1 al 10 o ingresar otra lista de
enteros. El programa solicita un exponente
entero positivo (`n > 0`). Si se ingresa un valor inválido, muestra un
mensaje de error. No requiere librerías externas.

### Ejemplo

Al ingresar `3`, la lista resultante es:

```text
[1, 8, 27, 64, 125, 216, 343, 512, 729, 1000]
```

La función `potencia = lambda numero: numero ** n` calcula la potencia de
un número. Un ciclo `for` recorre la lista, calcula cada valor y lo agrega
a `resultado` con `append()`, sin modificar la lista original.

## Ejercicio 3

Calcular la transpuesta de una matriz representada como lista de listas,
usando una función `lambda`. La solución está en `ejercicio3.py` y devuelve
también una lista de listas mediante `transponer_matriz(matriz)`.

### Ejecución

```bash
python main.py
```

Elegir la opción `3` del menú.

Se puede usar la matriz del enunciado o ingresar otra matriz. No requiere
librerías externas.
Todas las filas deben tener la misma longitud; de lo
contrario, la función lanza `ValueError`. Para una matriz vacía devuelve `[]`.

### Ejemplo

Para la matriz:

```text
[[1, 2, 3, 1], [4, 5, 6, 0], [7, 8, 9, -1]]
```

La transpuesta es:

```text
[[1, 4, 7], [2, 5, 8], [3, 6, 9], [1, 0, -1]]
```

La función `obtener_elemento = lambda fila, columna: matriz[fila][columna]`
lee una posición de la matriz. El ciclo exterior recorre las columnas y
el interior recorre las filas de la matriz original. Cada columna se
agrega como una nueva fila de la transpuesta mediante `append()`.
La matriz original se conserva.

## Ejercicio 4

Eliminar de una lista los elementos indicados en otra lista usando una
función `lambda`. La solución está en `ejercicio4.py` y devuelve los
elementos restantes mediante `eliminar_elementos(lista, elementos_a_borrar)`.

### Ejecución

```bash
python main.py
```

Elegir la opción `4` del menú.

Se pueden usar las dos listas del enunciado o ingresar una lista inicial
y otra con los elementos a borrar. Se admiten textos y números. No requiere
librerías externas.

### Ejemplo

Para la lista inicial:

```text
['rojo', 'verde', 'azul', 'amarillo', 'gris', 'blanco', 'negro']
```

Y la lista de elementos a borrar:

```text
['amarillo', 'café', 'blanco']
```

La salida es:

```text
['rojo', 'verde', 'azul', 'gris', 'negro']
```

La función `conservar = lambda elemento: elemento not in elementos_a_borrar`
indica si un elemento debe permanecer. Un ciclo `for` recorre la lista y
un `if` comprueba esa condición antes de agregarlo a `restantes` con
`append()`. Se eliminan todas las apariciones de los
valores indicados; los valores ausentes, como `café`, no afectan el resultado.
Las listas originales se conservan, al igual que el orden y las repeticiones
de los elementos restantes.

## Verificar la interfaz visual

Con `.venv` activado, ejecutar las pruebas del controlador con:

```bash
python -m unittest test_interfaz -v
```

Las pruebas cubren los cuatro ejemplos, datos propios, listas vacías y
entradas inválidas. Usan `unittest`, incluido en Python.

## Autor

- **Nombre:** Hugo Méndez
- **Carné:** 241265
