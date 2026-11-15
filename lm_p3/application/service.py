# Orquestación independiente de HTTP, con parser y validador sustituibles por M2.
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from lm_p3.models.ast import Formula
from lm_p3.models.errors import SemanticInputError
from lm_p3.models.language import Interpretation, Language
from lm_p3.models.trace import EvaluationResult
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import EvaluationLimits, ValidatedInput, prepare_input


class Parser(Protocol):
    def __call__(self, text: str, language: Language) -> Formula: ...


class Validator(Protocol):
    def __call__(self, language: Language, interpretation: Interpretation,
                 formula: Formula, environment: Mapping[str, str], *,
                 limits: EvaluationLimits | None = None) -> ValidatedInput: ...


@dataclass(frozen=True, slots=True)
class EvaluationOutcome:
    revision: int
    evaluation: EvaluationResult


def evaluate_formula(text: str, language: Language, interpretation: Interpretation,
                     environment: Mapping[str, str], *, parse: Parser,
                     validate: Validator = prepare_input, revision: int = 0,
                     limits: EvaluationLimits | None = None,
                     cancelled: Callable[[], bool] | None = None) -> EvaluationOutcome:
    # El servidor de M3 traduce errores esperados a JSON; aquí no se decide HTTP.
    if not isinstance(text, str) or not text.strip():
        raise SemanticInputError('empty_formula', 'Escribe una fórmula.', 'formula')
    if type(revision) is not int or revision < 0:
        raise SemanticInputError('invalid_revision', 'La revisión debe ser un entero no negativo.')
    formula = parse(text, language)
    request = validate(language, interpretation, formula, environment, limits=limits)
    if not isinstance(request, ValidatedInput):
        raise TypeError('El validador debe devolver ValidatedInput.')
    expected_limits = EvaluationLimits() if limits is None else limits
    if request.limits != expected_limits:
        raise SemanticInputError('validation_limits_changed',
                                 'El validador cambió los límites solicitados.')
    if (request.language != language or request.interpretation != interpretation
            or request.formula != formula or dict(request.environment) != dict(environment)):
        raise SemanticInputError('validation_context_changed',
                                 'El validador devolvió datos de otro contexto.')
    return EvaluationOutcome(revision, evaluate(request, cancelled=cancelled))
