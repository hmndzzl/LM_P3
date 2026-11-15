# Copias inmutables de interpretaciones finitas; se comprueban en la frontera.
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

Element = str
TupleValue = tuple[Element, ...]


@dataclass(frozen=True, slots=True)
class Language:
    functions: Mapping[str, int]
    predicates: Mapping[str, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'functions', MappingProxyType(dict(self.functions)))
        object.__setattr__(self, 'predicates', MappingProxyType(dict(self.predicates)))


@dataclass(frozen=True, slots=True)
class Interpretation:
    domain: tuple[Element, ...]
    functions: Mapping[str, Mapping[TupleValue, Element]]
    relations: Mapping[str, frozenset[TupleValue]]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'domain', tuple(self.domain))
        object.__setattr__(self, 'functions', MappingProxyType({
            name: MappingProxyType(dict(table)) for name, table in self.functions.items()
        }))
        object.__setattr__(self, 'relations', MappingProxyType({
            name: frozenset(rows) for name, rows in self.relations.items()
        }))
