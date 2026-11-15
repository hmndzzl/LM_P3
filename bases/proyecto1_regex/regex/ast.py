"""
Representación del Árbol de Sintaxis Abstracta (AST) para expresiones regulares en postfijo.
"""


class ASTNode:
    """Nodo individual de un Árbol de Sintaxis Abstracta (AST)."""
    def __init__(self, value, left=None, right=None, is_operator=False):
        self.value = value
        self.left = left
        self.right = right
        self.is_operator = is_operator
        self.id = id(self)


def build_ast(postfix):
    """
    Construye un Árbol de Sintaxis Abstracta (AST) a partir de una expresión en notación postfija.
    """
    stack = []
    tokens = []
    i = 0
    while i < len(postfix):
        if postfix[i] == '\\':
            if i + 1 >= len(postfix):
                raise ValueError("Caracter de escape '\\' al final de la expresion postfix.")
            tokens.append(('LIT', postfix[i + 1]))
            i += 2
        else:
            char = postfix[i]
            tokens.append(('OP', char) if char in ('.', '|', '*') else ('LIT', char))
            i += 1

    for kind, char in tokens:
        if kind == 'OP' and char in ('.', '|'):
            # Operadores binarios
            if len(stack) < 2:
                raise ValueError(f"Faltan operandos para el operador binario '{char}'")
            right = stack.pop()
            left = stack.pop()
            stack.append(ASTNode(char, left, right, is_operator=True))
        elif kind == 'OP' and char == '*':
            # Operador unario '*'
            if len(stack) < 1:
                raise ValueError(f"Faltan operandos para el operador unario '{char}'")
            child = stack.pop()
            stack.append(ASTNode(char, left=child, is_operator=True))
        else:
            # Literal
            stack.append(ASTNode(char))

    if len(stack) != 1:
        raise ValueError("La expresion postfix es invalida o quedaron demasiados elementos en la pila.")

    return stack.pop()
