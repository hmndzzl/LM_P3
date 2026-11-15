# Frontera defensiva de modelos normalizados, reutilizable por el validador de M2.
# Se comprueban todas las ramas antes de calcular verdad, sin analizar texto ni HTTP.
# La entrada certificada conserva copias inmutables del contexto y del entorno.
from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from types import MappingProxyType
from typing import Mapping

from lm_p3.models.ast import Binary, Formula, Function, Not, Predicate, Quantifier, Span, Variable
from lm_p3.models.errors import EvaluationLimitError, SemanticInputError
from lm_p3.models.language import Interpretation, Language


@dataclass(frozen=True, slots=True)
class EvaluationLimits:
    max_steps: int = 100_000
    max_depth: int = 128
    max_input_nodes: int = 20_000

    def __post_init__(self) -> None:
        for name in ('max_steps', 'max_depth', 'max_input_nodes'):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f'{name} debe ser un entero positivo.')
        # La evaluación recursiva debe permanecer bajo el límite de pila de Python.
        if self.max_depth > 128:
            raise ValueError('max_depth no puede superar 128.')


_SEAL = object()


@dataclass(frozen=True, slots=True)
class ValidatedInput:
    language: Language
    interpretation: Interpretation
    formula: Formula
    environment: Mapping[str, str]
    limits: EvaluationLimits
    free_variables: frozenset[str]
    _seal: InitVar[object] = field(repr=False, compare=False)

    def __post_init__(self, _seal: object) -> None:
        if _seal is not _SEAL:
            raise TypeError('Usa prepare_input para crear una entrada validada.')


def _error(code: str, message: str, field: str) -> None:
    raise SemanticInputError(code, message, field)


def _name(value: object, field: str) -> None:
    if not isinstance(value, str) or not value or value.strip() != value:
        _error('invalid_name', 'El nombre debe ser texto no vacío, sin espacios exteriores.', field)


def prepare_input(language: Language, interpretation: Interpretation, formula: Formula,
                  environment: Mapping[str, str] | None = None, *,
                  limits: EvaluationLimits | None = None) -> ValidatedInput:
    # Certifica modelos normalizados, incluyendo ramas no visitadas y todas las tablas.
    # Un fallo lanza SemanticInputError o EvaluationLimitError, sin verdad parcial.
    # Se aceptan asignaciones adicionales siempre que sus nombres y valores sean válidos.
    if not isinstance(language, Language) or not isinstance(interpretation, Interpretation):
        raise TypeError('Se requieren Language e Interpretation.')
    limits = EvaluationLimits() if limits is None else limits
    if not isinstance(limits, EvaluationLimits):
        raise TypeError('Se requiere EvaluationLimits.')
    domain = interpretation.domain
    if not domain or any(not isinstance(x, str) or not x for x in domain):
        _error('invalid_domain', 'D debe contener elementos de texto no vacíos.', 'domain')
    domain_set = set(domain)
    if len(domain_set) != len(domain):
        _error('duplicate_domain', 'D no puede repetir elementos.', 'domain')
    if set(language.functions) & set(language.predicates):
        _error('ambiguous_symbol', 'Un símbolo no puede ser función y predicado.', 'language')
    if set(language.functions) != set(interpretation.functions) or set(language.predicates) != set(interpretation.relations):
        _error('missing_interpretation', 'Interpreta exactamente todos los símbolos declarados.', 'interpretation')
    for kind, symbols, tables in (
        ('functions', language.functions, interpretation.functions),
        ('relations', language.predicates, interpretation.relations),
    ):
        for name, arity in symbols.items():
            path = f'{kind}.{name}'
            _name(name, path)
            if type(arity) is not int or arity < 0:
                _error('invalid_arity', 'La aridad debe ser un entero no negativo.', path)
            table = tables[name]
            if not table:
                _error('empty_interpretation', 'No se permiten funciones ni relaciones vacías.', path)
            for row in table:
                if not isinstance(row, tuple) or len(row) != arity:
                    _error('invalid_tuple_arity', 'La tupla no tiene la aridad declarada.', path)
                if any(not isinstance(x, str) or x not in domain_set for x in row):
                    _error('outside_domain', 'La tupla contiene elementos fuera de D.', path)
            if kind == 'functions':
                if any(not isinstance(value, str) or value not in domain_set for value in table.values()):
                    _error('outside_domain', 'La salida de una función debe pertenecer a D.', path)
                # Las claves son tuplas distintas de D^n: igual cardinalidad prueba totalidad.
                # Se evita calcular potencias enormes para descubrir una tabla incompleta.
                expected = 1
                if len(domain) > 1:
                    for _ in range(arity):
                        expected *= len(domain)
                        if expected > len(table):
                            break
                if expected != len(table):
                    _error('partial_function', 'Falta una salida para alguna tupla de D^n.', path)
    if environment is not None and not isinstance(environment, Mapping):
        raise TypeError('El entorno debe ser un Mapping.')
    env = dict(environment) if environment is not None else {}
    for name, value in env.items():
        _name(name, 'environment')
        if not isinstance(value, str) or value not in domain_set:
            _error('invalid_assignment', 'La asignación debe pertenecer a D.', f'environment.{name}')

    # Un recorrido iterativo limita el trabajo y detecta errores en todas las ramas.
    stack = [(formula, frozenset(), 1, False)]
    count = 0
    free = set()
    while stack:
        node, bound, depth, is_term = stack.pop()
        count += 1
        if count > limits.max_input_nodes or depth > limits.max_depth:
            raise EvaluationLimitError('La fórmula supera el límite de tamaño o profundidad.')
        span = getattr(node, 'span', None)
        if span is not None and (not isinstance(span, Span) or type(span.start) is not int
                                 or type(span.end) is not int or not 0 <= span.start <= span.end):
            _error('invalid_span', 'Rango de origen inválido.', 'formula')
        children = []
        if is_term and isinstance(node, Variable):
            _name(node.name, 'formula')
            if node.name not in bound:
                free.add(node.name)
                if node.name not in env:
                    _error('missing_assignment', f'Falta asignar {node.name}.', f'environment.{node.name}')
        elif (is_term and isinstance(node, Function)) or (not is_term and isinstance(node, Predicate)):
            _name(node.name, 'formula')
            symbols = language.functions if is_term else language.predicates
            if node.name not in symbols:
                _error('unknown_symbol', f'Símbolo no declarado: {node.name}.', 'formula')
            if len(node.arguments) != symbols[node.name]:
                _error('arity_mismatch', f'Aridad incorrecta para {node.name}.', 'formula')
            children = [(child, bound, depth + 1, True) for child in node.arguments]
        elif not is_term and isinstance(node, Not):
            children = [(node.operand, bound, depth + 1, False)]
        elif not is_term and isinstance(node, Binary):
            if node.operator not in ('∧', '∨', '→', '↔'):
                _error('unknown_connective', 'Conectivo no soportado por el motor.', 'formula')
            children = [(node.left, bound, depth + 1, False), (node.right, bound, depth + 1, False)]
        elif not is_term and isinstance(node, Quantifier):
            _name(node.variable, 'formula')
            if node.operator not in ('∀', '∃'):
                _error('unknown_quantifier', 'Cuantificador no soportado.', 'formula')
            children = [(node.body, bound | {node.variable}, depth + 1, False)]
        else:
            _error('invalid_ast', 'Nodo inválido en el AST.', 'formula')
        stack.extend(reversed(children))
    return ValidatedInput(language, interpretation, formula, MappingProxyType(env), limits, frozenset(free), _SEAL)
