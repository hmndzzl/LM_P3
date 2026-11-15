# La evidencia es información inmutable, independiente de HTTP y de la interfaz.
from __future__ import annotations

from dataclasses import dataclass

from lm_p3.models.ast import Span


@dataclass(frozen=True, slots=True)
class TermTrace:
    term: str
    value: str
    reason: str
    children: tuple[TermTrace, ...] = ()


@dataclass(frozen=True, slots=True)
class Trace:
    node_id: str
    trace_id: str
    formula: str
    span: Span | None
    environment: tuple[tuple[str, str], ...]
    value: bool
    reason: str
    children: tuple[Trace, ...] = ()
    terms: tuple[TermTrace, ...] = ()
    variable: str | None = None
    decisive_element: str | None = None
    checked_elements: tuple[str, ...] = ()
    unvisited_elements: tuple[str, ...] = ()
    domain_size: int | None = None
    complete: bool = True


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    value: bool
    trace: Trace
    steps: int
