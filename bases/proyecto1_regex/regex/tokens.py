"""
Definición de constantes, operadores y caracteres especiales utilizados en el
análisis léxico y sintáctico de expresiones regulares.
"""

# Operador binario soportado: unión. La concatenación se inserta internamente.
BINARY_OPS = {'|'}

# Operadores unarios postfijos soportados (Kleene, positiva, opcional)
POSTFIX_OPS = {'*', '+', '?'}

# Símbolo designado para representar la cadena vacía (épsilon)
EPSILON = 'ε'

# Carácter explícito utilizado internamente para representar la concatenación
CONCAT_DISPLAY = '.'
