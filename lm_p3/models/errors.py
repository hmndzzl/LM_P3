# Los errores semánticos esperados nunca contienen un valor de verdad
from __future__ import annotations

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


class EvaluationLimitError(RuntimeError):
    code = 'evaluation_limit'


class EvaluationCancelledError(RuntimeError):
    code = 'evaluation_cancelled'
