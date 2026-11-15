"""
Módulo regex: procesador de expresiones regulares, tokenización,
algoritmo Shunting Yard y construcción de Árbol de Sintaxis Abstracta (AST).
"""
from .tokens import BINARY_OPS, POSTFIX_OPS, EPSILON, CONCAT_DISPLAY
from .shunting_yard import infix_to_postfix
from .ast import ASTNode, build_ast

__all__ = [
    'BINARY_OPS',
    'POSTFIX_OPS',
    'EPSILON',
    'CONCAT_DISPLAY',
    'infix_to_postfix',
    'ASTNode',
    'build_ast',
]
