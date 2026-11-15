# Contrato sintáctico inmutable que consume el motor; no implementa un parser.
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union


@dataclass(frozen=True, slots=True)
class Span:
    # Intervalo [inicio, fin) medido en puntos de código Unicode de Python.
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class Variable:
    name: str
    span: Span | None = None


@dataclass(frozen=True, slots=True)
class Function:
    name: str
    arguments: tuple[Term, ...] = ()
    span: Span | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'arguments', tuple(self.arguments))


Term = Union[Variable, Function]


@dataclass(frozen=True, slots=True)
class Predicate:
    name: str
    arguments: tuple[Term, ...] = ()
    span: Span | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'arguments', tuple(self.arguments))


@dataclass(frozen=True, slots=True)
class Not:
    operand: Formula
    span: Span | None = None


@dataclass(frozen=True, slots=True)
class Binary:
    operator: Literal['∧', '∨', '→', '↔']
    left: Formula
    right: Formula
    span: Span | None = None


@dataclass(frozen=True, slots=True)
class Quantifier:
    operator: Literal['∀', '∃']
    variable: str
    body: Formula
    span: Span | None = None


Formula = Union[Predicate, Not, Binary, Quantifier]
