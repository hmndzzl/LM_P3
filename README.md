# Evaluador semántico

Proyecto de MM3032 Lógica Matemática. Evalúa fórmulas de lógica de primer orden sobre un dominio finito y muestra si son verdaderas o falsas, junto con su explicación.

Diego Andre Calderón Salazar - 241263

Pedro Julio Caso - 241286

Hugo Roberto Méndez Lee - 241265

## Características

- Permite definir el dominio, las constantes, las funciones y los predicados.
- Admite fórmulas abiertas y cerradas, conectivos y cuantificadores.
- Incluye botones para escribir símbolos lógicos y edición con teclado.
- Muestra testigos, contraejemplos y el detalle de las comprobaciones.
- Detecta entradas incorrectas sin asignarles un valor de verdad.
- Incluye once ejemplos y permite comparar cómo afecta cambiar un dato.

## Requisitos

- **Python 3.10 o posterior** y **Git** instalados.
- Un navegador actualizado.
- macOS, Linux o Windows.

No requiere instalar paquetes adicionales. Después de descargar el proyecto, funciona sin conexión a Internet.

## Instalación y ejecución

Abrir la terminal indicada y copiar los comandos de su sistema, uno por uno. Los dos primeros descargan el proyecto y abren su carpeta; el tercero inicia la aplicación.

### macOS

Abrir **Terminal**:

```sh
git clone https://github.com/hmndzzl/LM_P3.git
cd LM_P3
python3 -B -m lm_p3
```

### Linux

Abrir la **terminal**:

```sh
git clone https://github.com/hmndzzl/LM_P3.git
cd LM_P3
python3 -B -m lm_p3
```

### Windows

Abrir **PowerShell** o **Símbolo del sistema**:

```powershell
git clone https://github.com/hmndzzl/LM_P3.git
cd LM_P3
py -3 -B -m lm_p3
```

Si Windows no reconoce `py`, utilizar `python -B -m lm_p3`.

El navegador se abre automáticamente. Si no ocurre, copiar en el navegador la dirección que aparece en la terminal. Mantener esa terminal abierta durante el uso y presionar **Ctrl+C** para cerrar la aplicación.

Para abrirla nuevamente, entrar en la carpeta `LM_P3` desde la terminal y ejecutar solo el último comando de su sistema.

## Cómo utilizarla

1. En **Probar Ejemplos**, seleccionar un caso y pulsar **Cargar ejemplo**.
2. Pulsar **Evaluar fórmula**.
3. Abrir los pasos del resultado para consultar la explicación.
4. Para probar otra situación, modificar la fórmula o los datos y volver a evaluar.

**Comparar un cambio** permite modificar un dato y consultar ambos resultados sin alterar el caso original. **Limpiar todo** borra los datos ingresados.

Para ingresar un caso propio, definir el dominio en **Editar dominio**, añadir los símbolos y completar sus tablas. Escribir la fórmula y usar **Revisar variables libres** para asignar los valores que falten. Los símbolos lógicos pueden insertarse con los botones del editor.

El dominio y las relaciones deben contener al menos un elemento o tupla, respectivamente. Cada función debe tener una salida para todas las combinaciones de entrada. Usar paréntesis para indicar el alcance de los cuantificadores, por ejemplo: `∀x (P(x) → Q(x))`.

## Ejemplos para probar

### Ejemplos incluidos

Seleccionar el ejemplo correspondiente, cargarlo y evaluar:

| Ejemplo | Resultado esperado |
| --- | --- |
| `P(x)`: pertenencia y asignación | Verdadero con `x: 1`; Falso al cambiar a `x: 3`. |
| `∀x P(x)`: buscar un contraejemplo | Falso; el contraejemplo es `3`. |
| `∀x (P(x) ∨ ¬P(x))`: comprobación completa | Verdadero; se revisan los tres elementos. |
| `∀x ∃y R(x,y)`: cuantificadores anidados | Verdadero; cada elemento tiene un testigo. |
| `∃x P(x)`: encontrar un testigo | Verdadero; el primer testigo es `1`. |
| `∃x (P(x) ∧ ¬P(x))`: revisar todo D | Falso; ningún elemento cumple. |
| `¬R(i)`: interpretar una constante | Verdadero; al cambiar `i` de `a` a `b`, pasa a Falso. |
| Caso integrado | Falso; al cambiar únicamente `f(c,c)` de `a` a `b`, pasa a Verdadero. |

La aplicación también incluye ejemplos de funciones, constantes con relaciones y el caso de Sócrates.

### Ejemplos adicionales

Cargar **Pertenencia y asignación** antes de cada prueba. Mantener sus datos y reemplazar la fórmula por una de las siguientes:

| Fórmula | Resultado esperado |
| --- | --- |
| `∀x ∃y R(y,x)` | Verdadero. |
| `∃y ∀x R(x,y)` | Falso. |
| `∀x (P(x) → ∃y R(x,y))` | Verdadero. |

Para comprobar la detección de errores, escribir `P(x` o `R(x)` sobre ese mismo ejemplo. La aplicación debe indicar, respectivamente, un paréntesis faltante o un número incorrecto de argumentos.

Los resultados corresponden únicamente al dominio y a la interpretación ingresados.
