from __future__ import annotations

from dataclasses import dataclass, replace

from lm_p3.models.ast import Binary, Formula, Function, Not, Predicate, Quantifier, Span, Term, Variable
from lm_p3.models.errors import EvaluationLimitError, FormulaSyntaxError
from lm_p3.models.language import Language
from lm_p3.syntax.free_variables import free_variables
from lm_p3.syntax.lexer import Token, tokenize
from lm_p3.validation.validator import validate_language


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    formula: Formula
    free_variables: frozenset[str]


class _Parser:
    def __init__(self, text: str, language: Language) -> None:
        self.tokens = tokenize(text)
        self.index = 0
        self.language = language

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def _take(self) -> Token:
        token = self.current
        if token.kind != 'end':
            self.index += 1
        return token

    def _error(self, code: str, message: str, token: Token | None = None) -> None:
        raise FormulaSyntaxError(code, message, (token or self.current).span)

    def _declared(self, name: str) -> bool:
        return name in self.language.functions or name in self.language.predicates

    def _depth(self, depth: int) -> None:
        if depth > 128:
            raise EvaluationLimitError('La fórmula supera 128 niveles de análisis.')

    def run(self) -> Formula:
        if self.current.kind == 'end':
            self._error('empty_formula', 'Escribe una fórmula.')
        formula = self._expression()
        if self.current.kind != 'end':
            self._error('unexpected_token', 'Sobra texto después de la fórmula.')
        # El bucle de operadores puede construir un AST profundo sin recursión
        free_variables(formula)
        return formula

    def _expression(self, minimum: int = 0, depth: int = 1) -> Formula:
        self._depth(depth)
        left = self._prefix(depth)
        precedence = {'↔': 1, '→': 2, '∨': 3, '∧': 4}
        while True:
            token = self.current
            operator = token.kind
            if token.kind == 'identifier' and token.value == 'v' and not self._declared('v'):
                operator = '∨'
            level = precedence.get(operator, -1)
            if level < minimum:
                break
            self._take()
            # Solo la implicación permite a su derecha otro operador de igual nivel
            right = self._expression(level if operator == '→' else level + 1, depth + 1)
            left = Binary(operator, left, right, Span(left.span.start, right.span.end))
        return left

    def _prefix(self, depth: int) -> Formula:
        self._depth(depth)
        token = self.current
        if token.kind == '¬':
            self._take()
            operand = self._prefix(depth + 1)
            return Not(operand, Span(token.span.start, operand.span.end))
        if token.kind in ('∀', '∃'):
            self._take()
            variable = self.current
            if variable.kind != 'identifier':
                self._error('expected_variable', 'Escribe una variable después del cuantificador.')
            self._take()
            return self._quantifier(token.value, variable.value, token.span.start, variable, depth)
        if token.kind == '(':
            self._take()
            formula = self._expression(depth=depth + 1)
            if self.current.kind != ')':
                self._error('missing_parenthesis', 'Falta cerrar un paréntesis en la fórmula.')
            closing = self._take()
            return replace(formula, span=Span(token.span.start, closing.span.end))
        if token.kind != 'identifier':
            self._error('expected_formula', 'Falta una fórmula: escribe un predicado o una subfórmula.')
        if not self._declared(token.value) and len(token.value) > 1 and token.value[0] in 'AE':
            name = token.value[1:]
            if name.isidentifier():
                self._take()
                variable = Token('identifier', name, name, Span(token.span.start + 1, token.span.end))
                return self._quantifier('∀' if token.value[0] == 'A' else '∃', name,
                                        token.span.start, variable, depth)
        self._take()
        if token.value not in self.language.predicates:
            self._error('expected_predicate' if token.value in self.language.functions else 'unknown_symbol',
                        f'{token.value} no es un predicado declarado.', token)
        arguments, end = self._arguments(depth, token)
        self._arity(token, self.language.predicates[token.value], len(arguments), end)
        return Predicate(token.value, arguments, Span(token.span.start, end))

    def _quantifier(self, operator: str, name: str, start: int,
                    variable: Token, depth: int) -> Formula:
        if self._declared(name):
            self._error('invalid_bound_variable',
                        f'{name} es un símbolo declarado; elige otro nombre de variable.', variable)
        # Un prefijo abarca solo la siguiente subfórmula inmediata, incluidos sus prefijos
        body = self._prefix(depth + 1)
        return Quantifier(operator, name, body, Span(start, body.span.end))

    def _arguments(self, depth: int, name: Token) -> tuple[tuple[Term, ...], int]:
        if self.current.kind != '(':
            return (), name.span.end
        self._take()
        arguments = []
        if self.current.kind != ')':
            arguments.append(self._term(depth + 1))
            while self.current.kind == ',':
                self._take()
                arguments.append(self._term(depth + 1))
        if self.current.kind != ')':
            self._error('missing_parenthesis', 'Falta una coma o cerrar un paréntesis en los argumentos.')
        return tuple(arguments), self._take().span.end

    def _term(self, depth: int) -> Term:
        self._depth(depth)
        token = self.current
        if token.kind != 'identifier':
            self._error('expected_term', 'Falta un término: escribe una variable o una función.')
        self._take()
        if token.value in self.language.functions:
            arguments, end = self._arguments(depth, token)
            self._arity(token, self.language.functions[token.value], len(arguments), end)
            return Function(token.value, arguments, Span(token.span.start, end))
        if token.value in self.language.predicates:
            self._error('predicate_as_term', f'{token.value} es un predicado y no puede ser un término.', token)
        if self.current.kind == '(':
            self._error('unknown_symbol', f'Función no declarada: {token.value}.', token)
        return Variable(token.value, token.span)

    def _arity(self, token: Token, expected: int, actual: int, end: int) -> None:
        if expected != actual:
            noun = 'argumento' if expected == 1 else 'argumentos'
            raise FormulaSyntaxError('arity_mismatch',
                                     f'{token.value} necesita {expected} {noun}; se encontraron {actual}.',
                                     Span(token.span.start, end),
                                     details={'symbol': token.value, 'expected': expected, 'actual': actual})


def parse(text: str, language: Language) -> Formula:
    # Firma del protocolo Parser de application.service no requiere interpretación
    validate_language(language)
    return _Parser(text, language).run()


def analyze(text: str, language: Language) -> AnalysisResult:
    # Permite solicitar asignaciones antes de llamar la evaluación
    formula = parse(text, language)
    return AnalysisResult(formula, free_variables(formula))
