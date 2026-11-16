from __future__ import annotations

from lm_p3.models.ast import Binary, Formula, Function, Not, Predicate, Quantifier, Variable
from lm_p3.models.errors import EvaluationLimitError


def free_variables(formula: Formula) -> frozenset[str]:
    # Los límites también protegen AST construidos directamente por un consumidor
    stack = [(formula, frozenset(), 1)]
    names = set()
    visited = 0
    while stack:
        node, bound, depth = stack.pop()
        visited += 1
        if visited > 20_000 or depth > 128:
            raise EvaluationLimitError('La fórmula supera el límite de tamaño o profundidad.')
        if isinstance(node, Variable):
            if node.name not in bound:
                names.add(node.name)
        elif isinstance(node, (Function, Predicate)):
            stack.extend((child, bound, depth + 1) for child in node.arguments)
        elif isinstance(node, Not):
            stack.append((node.operand, bound, depth + 1))
        elif isinstance(node, Binary):
            stack.extend(((node.left, bound, depth + 1), (node.right, bound, depth + 1)))
        elif isinstance(node, Quantifier):
            stack.append((node.body, bound | {node.variable}, depth + 1))
        else:
            raise TypeError('Se requiere un AST de términos y fórmulas compartidos.')
    return frozenset(names)
