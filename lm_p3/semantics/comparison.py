# Comparación de dos escenarios certificados que difieren en un único dato.
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from lm_p3.models.errors import SemanticInputError
from lm_p3.models.trace import EvaluationResult, Trace
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import ValidatedInput


@dataclass(frozen=True, slots=True)
class ScenarioChange:
    kind: Literal['function', 'relation', 'assignment']
    symbol: str
    arguments: tuple[str, ...]
    before: str | bool
    after: str | bool


@dataclass(frozen=True, slots=True)
class EvidenceChange:
    trace_id: str
    before: Trace | None
    after: Trace | None


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    change: ScenarioChange
    before: EvaluationResult
    after: EvaluationResult
    evidence_changes: tuple[EvidenceChange, ...]

    @property
    def truth_changed(self) -> bool:
        return self.before.value != self.after.value


def _index_trace(root: Trace) -> dict[str, Trace]:
    result = {}
    pending = [root]
    while pending:
        node = pending.pop()
        result[node.trace_id] = node
        pending.extend(reversed(node.children))
    return result


def compare(base: ValidatedInput, variant: ValidatedInput, *,
            cancelled: Callable[[], bool] | None = None) -> ComparisonResult:
    # Se recalculan ambos escenarios; jamás se reutiliza un resultado de otra revisión.
    if not isinstance(base, ValidatedInput) or not isinstance(variant, ValidatedInput):
        raise TypeError('compare requiere dos entradas producidas por prepare_input.')
    if (base.language != variant.language or base.formula != variant.formula
            or base.interpretation.domain != variant.interpretation.domain):
        raise SemanticInputError('new_comparison_base',
                                 'Cambió la fórmula, el lenguaje o D. Genera una nueva base.')
    changes = []
    for name, table in base.interpretation.functions.items():
        other = variant.interpretation.functions[name]
        for row, output in table.items():
            if output != other[row]:
                changes.append(ScenarioChange('function', name, row, output, other[row]))
    for name, relation in base.interpretation.relations.items():
        other = variant.interpretation.relations[name]
        for row in sorted(relation ^ other):
            changes.append(ScenarioChange('relation', name, row, row in relation, row in other))
    if set(base.environment) != set(variant.environment):
        raise SemanticInputError('assignment_keys_changed',
                                 'Conserva las mismas variables del entorno para comparar.')
    for name, value in base.environment.items():
        other = variant.environment[name]
        if value != other:
            if name not in base.free_variables:
                raise SemanticInputError('not_free_assignment',
                                         'Solo se comparan asignaciones de variables libres.')
            changes.append(ScenarioChange('assignment', name, (), value, other))
    if len(changes) != 1:
        raise SemanticInputError('single_change_required',
                                 'La comparación requiere exactamente un dato cambiado.')
    before = evaluate(base, cancelled=cancelled)
    after = evaluate(variant, cancelled=cancelled)
    old_nodes = _index_trace(before.trace)
    new_nodes = _index_trace(after.trace)
    changed_evidence = tuple(
        EvidenceChange(key, old_nodes.get(key), new_nodes.get(key))
        for key in sorted(old_nodes.keys() | new_nodes.keys())
        if old_nodes.get(key) != new_nodes.get(key)
    )
    return ComparisonResult(changes[0], before, after, changed_evidence)
