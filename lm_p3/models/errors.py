# Los errores semánticos esperados nunca contienen un valor de verdad
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from types import MappingProxyType
from typing import Mapping

from lm_p3.models.ast import Span


class SemanticInputError(ValueError):
    def __init__(self, code: str, message: str, field: str = '') -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field


class FormulaSyntaxError(SemanticInputError):
    # Compatible con el manejo de errores del servicio; no contiene HTML ni verdad.
    def __init__(self, code: str, message: str, span: Span, *,
                 details: Mapping[str, str | int] | None = None) -> None:
        super().__init__(code, message, 'formula')
        self.span = span
        self.details = MappingProxyType(dict(details or {}))


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str
    field: str
    span: Span | None = None
    details: Mapping[str, str | int] = dataclass_field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'details', MappingProxyType(dict(self.details)))


class InputValidationError(SemanticInputError):
    # El primer error conserva compatibilidad, errors contiene el diagnóstico completo
    def __init__(self, errors: tuple[ValidationIssue, ...]) -> None:
        if not errors:
            raise ValueError('Se requiere al menos un error de validación.')
        self.errors = tuple(errors)
        first = self.errors[0]
        super().__init__(first.code, first.message, first.field)


class EvaluationLimitError(RuntimeError):
    code = 'evaluation_limit'


class EvaluationCancelledError(RuntimeError):
    code = 'evaluation_cancelled'
