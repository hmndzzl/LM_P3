# Validación integral reutilizable; ninguna comprobación calcula verdad.
from __future__ import annotations

from collections.abc import Mapping
from itertools import islice, product

from lm_p3.models.ast import Binary, Formula, Function, Not, Predicate, Quantifier, Span, Variable
from lm_p3.models.errors import EvaluationLimitError, InputValidationError, ValidationIssue
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.inputs import EvaluationLimits, ValidatedInput, prepare_input


class _Checks:
    def __init__(self) -> None:
        self.errors: list[ValidationIssue] = []
        self.items = 0

    def add(self, code: str, message: str, field: str, *, span: Span | None = None,
            **details: str | int) -> None:
        self.errors.append(ValidationIssue(code, message, field, span, details))

    def spend(self, count: int) -> None:
        self.items += count
        if self.items > 20_000:
            raise EvaluationLimitError('Los datos superan 20 000 entradas y componentes de tuplas.')

    def sequence(self, value: object, field: str) -> list | tuple | None:
        if not isinstance(value, (list, tuple)):
            self.add('invalid_structure', 'Introduce una lista ordenada de valores.', field)
            return None
        self.spend(len(value))
        return value

    def mapping(self, value: object, field: str) -> Mapping | None:
        if not isinstance(value, Mapping):
            self.add('invalid_structure', 'Se requiere una tabla por nombre de símbolo.', field)
            return None
        self.spend(len(value))
        return value

    def finish(self) -> None:
        if self.errors:
            raise InputValidationError(tuple(self.errors))


def _identifier(name: object) -> bool:
    return isinstance(name, str) and name.isidentifier()


def _language(language: Language, checks: _Checks) -> bool:
    if not isinstance(language, Language):
        checks.add('invalid_structure', 'Se requiere un lenguaje declarado.', 'language')
        return False
    start = len(checks.errors)
    checks.spend(len(language.functions) + len(language.predicates))
    for kind, symbols in (('functions', language.functions), ('predicates', language.predicates)):
        for name, arity in symbols.items():
            field = f'language.{kind}.{name}'
            if not _identifier(name):
                checks.add('invalid_name', 'Usa un identificador sin espacios ni operadores.', field)
            if type(arity) is not int or arity < 0:
                checks.add('invalid_arity', 'La aridad debe ser un entero no negativo.', field)
    for name in language.functions:
        if name in language.predicates:
            checks.add('ambiguous_symbol', 'Un símbolo no puede ser función y predicado.',
                       f'language.functions.{name}', symbol=str(name))
    return len(checks.errors) == start


def validate_language(language: Language) -> None:
    # Comparte las reglas del validador integral sin solicitar interpretación.
    checks = _Checks()
    _language(language, checks)
    checks.finish()


def _domain(value: object, checks: _Checks) -> tuple[str, ...]:
    values = checks.sequence(value, 'domain')
    if values is None:
        return ()
    if not values:
        checks.add('invalid_domain', 'D no puede estar vacío. Añade al menos un elemento.', 'domain')
    domain = []
    seen = set()
    for index, element in enumerate(values):
        field = f'domain[{index}]'
        if not isinstance(element, str) or not element.strip():
            checks.add('invalid_domain', 'Cada elemento de D debe ser texto no vacío.', field)
        elif element in seen:
            checks.add('duplicate_domain', f'El elemento {element} está repetido en D.', field)
        else:
            seen.add(element)
            domain.append(element)
    return tuple(domain)


def _tuple(value: object, arity: int, domain: set[str], field: str,
           checks: _Checks) -> tuple[str, ...] | None:
    values = checks.sequence(value, field)
    if values is None:
        return None
    start = len(checks.errors)
    if len(values) != arity:
        checks.add('invalid_tuple_arity',
                   f'La tupla necesita {arity} componentes; se encontraron {len(values)}.',
                   field, expected=arity, actual=len(values))
    for index, element in enumerate(values):
        if not isinstance(element, str) or element not in domain:
            checks.add('outside_domain', 'Elige un elemento de D para esta componente.', f'{field}[{index}]')
    return tuple(values) if len(checks.errors) == start else None


def _total(table: dict, domain: tuple[str, ...], arity: int) -> bool:
    # Claves distintas de D^n y cardinalidad suficiente prueban totalidad sin generar D^n.
    expected = 1
    if len(domain) > 1:
        for _ in range(arity):
            expected *= len(domain)
            if expected > len(table):
                return False
    return len(table) == expected


def _function(name: str, arity: int, rows: object, domain: tuple[str, ...], domain_set: set[str],
              checks: _Checks, raw: bool) -> dict[tuple[str, ...], str]:
    path = f'functions.{name}'
    values = checks.sequence(rows, path) if raw else checks.mapping(rows, path)
    if values is None:
        return {}
    if not values:
        checks.add('empty_interpretation', f'La función {name} está vacía. Define sus salidas.', path)
        return {}
    start = len(checks.errors)
    table = {}
    for index, row in enumerate(values if raw else values.items()):
        field = f'{path}[{index}]'
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            checks.add('invalid_function_row', 'Cada fila necesita argumentos y una salida.', field)
            continue
        arguments, output = row
        key = _tuple(arguments, arity, domain_set, f'{field}.arguments', checks)
        if not isinstance(output, str) or output not in domain_set:
            checks.add('outside_domain', 'Elige una salida de D para esta función.', f'{field}.output')
            continue
        if key is not None:
            if key in table and table[key] != output:
                checks.add('conflicting_function_row',
                           f'{name}{key} tiene dos salidas distintas. Conserva solo una.',
                           f'{field}.output', symbol=name, previous=table[key], actual=output)
            else:
                table[key] = output
    if domain and len(checks.errors) == start and not _total(table, domain, arity):
        details: dict[str, str | int] = {'symbol': name}
        # Se examinan como máximo filas+1 candidatos; tampoco se materializa D^n aquí.
        missing = None
        if arity <= 128:
            missing = next((key for key in islice(product(domain, repeat=arity), len(table) + 1)
                            if key not in table), None)
        label = f'{name}({", ".join(missing)})' if missing is not None else name
        if missing is not None:
            details['missing_tuple'] = repr(missing)
        checks.add('partial_function', f'Falta definir {label}. Elige una salida del dominio.', path, **details)
    return table


def _relation(name: str, arity: int, rows: object, domain: set[str],
              checks: _Checks, raw: bool) -> set[tuple[str, ...]]:
    path = f'relations.{name}'
    if not raw and isinstance(rows, (set, frozenset)):
        checks.spend(len(rows))
        # Orden estable para diagnósticos incluso cuando el modelo usa conjuntos.
        values = sorted(rows, key=repr)
    else:
        values = checks.sequence(rows, path)
    if values is None:
        return set()
    if not values:
        checks.add('empty_interpretation', f'La relación {name} está vacía. Añade al menos una tupla.', path)
    result = set()
    for index, row in enumerate(values):
        key = _tuple(row, arity, domain, f'{path}[{index}]', checks)
        if key is not None:
            result.add(key)
    return result


def _interpretation(language: Language, domain: object, functions: object, relations: object,
                    checks: _Checks, *, raw: bool) -> tuple[tuple, dict, dict]:
    ordered = _domain(domain, checks)
    members = set(ordered)
    tables = []
    for kind, supplied, declared in (('functions', functions, language.functions),
                                      ('relations', relations, language.predicates)):
        mapping = checks.mapping(supplied, kind)
        result = {}
        if mapping is not None:
            for name in declared:
                if name not in mapping:
                    checks.add('missing_interpretation', f'Falta interpretar {name}.', f'{kind}.{name}')
            for name in mapping:
                if name not in declared:
                    checks.add('unknown_symbol', f'No se declaró el símbolo {name}.', f'{kind}.{name}')
            for name, arity in declared.items():
                if name not in mapping or type(arity) is not int or arity < 0 or not _identifier(name):
                    continue
                result[name] = (_function(name, arity, mapping[name], ordered, members, checks, raw)
                                if kind == 'functions' else
                                _relation(name, arity, mapping[name], members, checks, raw))
        tables.append(result)
    return ordered, tables[0], tables[1]


def _environment(language: Language, domain: tuple[str, ...], assignments: object,
                 checks: _Checks, *, raw: bool) -> dict[str, str]:
    if assignments is None and not raw:
        return {}
    values = (checks.sequence(assignments, 'environment') if raw else
              checks.mapping(assignments, 'environment'))
    if values is None:
        return {}
    result = {}
    domain_set = set(domain)
    for index, row in enumerate(values if raw else values.items()):
        field = f'environment[{index}]' if raw else f'environment.{row[0]}'
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            checks.add('invalid_assignment', 'Cada asignación necesita variable y valor.', field)
            continue
        name, value = row
        if not _identifier(name) or name in language.functions or name in language.predicates:
            checks.add('invalid_variable', 'Elige un nombre de variable que no sea un símbolo declarado.', field)
            continue
        valid = isinstance(value, str) and value in domain_set
        if not valid:
            checks.add('invalid_assignment', f'Elige un elemento de D para {name}.', field, variable=name)
        elif name in result and result[name] != value:
            checks.add('conflicting_assignment', f'{name} tiene dos asignaciones distintas.', field,
                       variable=name, previous=result[name], actual=value)
        else:
            result[name] = value
    return result


def _ast(language: Language, formula: Formula, checks: _Checks, limits: EvaluationLimits) -> set[str]:
    free = set()
    stack = [(formula, frozenset(), 1, False, '0')]
    count = 0
    while stack:
        node, bound, depth, is_term, path = stack.pop()
        count += 1
        if count > limits.max_input_nodes or depth > limits.max_depth:
            raise EvaluationLimitError('La fórmula supera el límite de tamaño o profundidad.')
        span = getattr(node, 'span', None)
        if span is not None and (not isinstance(span, Span) or type(span.start) is not int
                                 or type(span.end) is not int or not 0 <= span.start <= span.end):
            checks.add('invalid_span', 'Rango de origen inválido.', 'formula', node=path)
            span = None
        children = []
        if is_term and isinstance(node, Variable):
            if not _identifier(node.name) or node.name in language.functions or node.name in language.predicates:
                checks.add('invalid_variable', 'El término necesita una variable no declarada como símbolo.',
                           'formula', span=span, node=path)
            elif node.name not in bound:
                free.add(node.name)
        elif (is_term and isinstance(node, Function)) or (not is_term and isinstance(node, Predicate)):
            symbols = language.functions if is_term else language.predicates
            if not _identifier(node.name) or node.name not in symbols:
                checks.add('unknown_symbol', 'Este símbolo no está declarado en la clase requerida.',
                           'formula', span=span, node=path)
            elif (type(symbols[node.name]) is int and symbols[node.name] >= 0
                  and len(node.arguments) != symbols[node.name]):
                checks.add('arity_mismatch', f'Aridad incorrecta para {node.name}.', 'formula',
                           span=span, symbol=node.name, expected=symbols[node.name], actual=len(node.arguments))
            children = [(child, bound, depth + 1, True, f'{path}.{index}')
                        for index, child in enumerate(node.arguments)]
        elif not is_term and isinstance(node, Not):
            children = [(node.operand, bound, depth + 1, False, f'{path}.0')]
        elif not is_term and isinstance(node, Binary):
            if node.operator not in ('∧', '∨', '→', '↔'):
                checks.add('unknown_connective', 'Conectivo no soportado.', 'formula', span=span, node=path)
            children = [(node.left, bound, depth + 1, False, f'{path}.0'),
                        (node.right, bound, depth + 1, False, f'{path}.1')]
        elif not is_term and isinstance(node, Quantifier):
            valid_name = (_identifier(node.variable) and node.variable not in language.functions
                          and node.variable not in language.predicates)
            if not valid_name:
                checks.add('invalid_bound_variable', 'El cuantificador necesita una variable válida.',
                           'formula', span=span, node=path)
            if node.operator not in ('∀', '∃'):
                checks.add('unknown_quantifier', 'Cuantificador no soportado.', 'formula', span=span, node=path)
            children = [(node.body, bound | {node.variable} if valid_name else bound,
                         depth + 1, False, f'{path}.0')]
        else:
            checks.add('invalid_ast', 'Nodo inválido en esta posición del AST.', 'formula', span=span, node=path)
        stack.extend(reversed(children))
    return free


def collect_errors(language: Language, interpretation: Interpretation, formula: Formula,
                   environment: Mapping[str, str] | None = None, *,
                   limits: EvaluationLimits | None = None) -> tuple[ValidationIssue, ...]:
    # Recoge todos los errores independientes; no omite ramas ni símbolos sin uso.
    limits = EvaluationLimits() if limits is None else limits
    if not isinstance(limits, EvaluationLimits):
        raise TypeError('Se requiere EvaluationLimits.')
    checks = _Checks()
    _language(language, checks)
    safe_language = language if isinstance(language, Language) else Language({}, {})
    if isinstance(interpretation, Interpretation):
        domain, _, _ = _interpretation(safe_language, interpretation.domain, interpretation.functions,
                                        interpretation.relations, checks, raw=False)
    else:
        checks.add('invalid_structure', 'Se requiere una interpretación.', 'interpretation')
        domain = ()
    _environment(safe_language, domain, environment, checks, raw=False)
    free = _ast(safe_language, formula, checks, limits)
    for name in sorted(free):
        if not isinstance(environment, Mapping) or name not in environment:
            checks.add('missing_assignment', f'Falta asignar {name}. Elige un elemento de D.',
                       f'environment.{name}', variable=name)
    return tuple(checks.errors)


def validate_input(language: Language, interpretation: Interpretation, formula: Formula,
                   environment: Mapping[str, str] | None = None, *,
                   limits: EvaluationLimits | None = None) -> ValidatedInput:
    # La fábrica de M1 conserva el sello, las copias inmutables y los límites solicitados.
    errors = collect_errors(language, interpretation, formula, environment, limits=limits)
    if errors:
        raise InputValidationError(errors)
    return prepare_input(language, interpretation, formula, environment, limits=limits)
