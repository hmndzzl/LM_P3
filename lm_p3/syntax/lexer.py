from __future__ import annotations

from dataclasses import dataclass

from lm_p3.models.ast import Span
from lm_p3.models.errors import EvaluationLimitError, FormulaSyntaxError


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    value: str
    lexeme: str
    span: Span


def tokenize(text: str) -> tuple[Token, ...]:
    # Ax/Ex y v se resuelven en contexto sintáctico para conservar identificadores
    # Los límites iniciales son internos y no convierten un exceso en Falso
    if not isinstance(text, str):
        raise TypeError('La fórmula debe ser texto.')
    if len(text) > 100_000:
        raise EvaluationLimitError('La fórmula supera 100 000 caracteres.')
    tokens = []
    index = 0
    aliases = {'~': '¬', '&': '∧', '|': '∨', '->': '→', '<->': '↔'}
    while index < len(text):
        start = index
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if len(tokens) >= 20_000:
            raise EvaluationLimitError('La fórmula supera 20 000 tokens.')
        if text.startswith('<->', index):
            index += 3
        elif text.startswith('->', index):
            index += 2
        elif char in '¬∧∨→↔∀∃~&|(),':
            index += 1
        elif char.isidentifier():
            index += 1
            while index < len(text) and ('_' + text[index]).isidentifier():
                index += 1
            lexeme = text[start:index]
            tokens.append(Token('identifier', lexeme, lexeme, Span(start, index)))
            continue
        else:
            message = ('La igualdad no es primitiva; declara un predicado binario con nombre.'
                       if char == '=' else f'Carácter no admitido: {char}.')
            raise FormulaSyntaxError('unsupported_equality' if char == '=' else 'invalid_character',
                                     message, Span(start, start + 1))
        lexeme = text[start:index]
        canonical = aliases.get(lexeme, lexeme)
        tokens.append(Token(canonical, canonical, lexeme, Span(start, index)))
    tokens.append(Token('end', '', '', Span(len(text), len(text))))
    return tuple(tokens)
