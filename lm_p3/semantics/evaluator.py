# Semántica finita de primer orden; cada evidencia procede del recorrido real.
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from lm_p3.models.ast import Binary, Formula, Function, Not, Predicate, Quantifier, Term, Variable
from lm_p3.models.errors import EvaluationCancelledError, EvaluationLimitError
from lm_p3.models.trace import EvaluationResult, TermTrace, Trace
from lm_p3.semantics.inputs import ValidatedInput


def render_term(term: Term) -> str:
    if isinstance(term, Variable):
        return term.name
    arguments = ', '.join(render_term(arg) for arg in term.arguments)
    return f'{term.name}({arguments})'


def render_formula(formula: Formula) -> str:
    if isinstance(formula, Predicate):
        return f"{formula.name}({', '.join(render_term(arg) for arg in formula.arguments)})"
    if isinstance(formula, Not):
        return f'¬({render_formula(formula.operand)})'
    if isinstance(formula, Binary):
        return f'({render_formula(formula.left)} {formula.operator} {render_formula(formula.right)})'
    return f'{formula.operator}{formula.variable} ({render_formula(formula.body)})'


@dataclass
class _Traversal:
    request: ValidatedInput
    cancelled: Callable[[], bool] | None
    steps: int = 0

    def tick(self) -> None:
        if self.cancelled is not None and self.cancelled():
            raise EvaluationCancelledError('Evaluación cancelada; no se obtuvo un valor de verdad.')
        self.steps += 1
        if self.steps > self.request.limits.max_steps:
            raise EvaluationLimitError('Se superó el límite de pasos; no se obtuvo un valor de verdad.')

    def term(self, term: Term, environment: dict[str, str]) -> TermTrace:
        self.tick()
        if isinstance(term, Variable):
            return TermTrace(term.name, environment[term.name], 'variable_assignment')
        children = tuple(self.term(arg, environment) for arg in term.arguments)
        row = tuple(child.value for child in children)
        value = self.request.interpretation.functions[term.name][row]
        return TermTrace(render_term(term), value, 'function_lookup', children)

    def formula(self, formula: Formula, environment: dict[str, str],
                node_id: str = '0', trace_id: str = '0') -> Trace:
        self.tick()
        common = dict(node_id=node_id, trace_id=trace_id, formula=render_formula(formula),
                      span=formula.span, environment=tuple(sorted(environment.items())))
        if isinstance(formula, Predicate):
            terms = tuple(self.term(term, environment) for term in formula.arguments)
            row = tuple(term.value for term in terms)
            value = row in self.request.interpretation.relations[formula.name]
            return Trace(**common, value=value, terms=terms,
                         reason='predicate_member' if value else 'predicate_not_member')
        if isinstance(formula, Not):
            child = self.formula(formula.operand, environment, node_id + '.0', trace_id + '.0')
            return Trace(**common, value=not child.value, reason='negation', children=(child,))
        if isinstance(formula, Binary):
            # Se evalúan ambos operandos para que el explorador pueda consultar su evidencia.
            left = self.formula(formula.left, environment, node_id + '.0', trace_id + '.0')
            right = self.formula(formula.right, environment, node_id + '.1', trace_id + '.1')
            if formula.operator == '∧':
                value = left.value and right.value
                reason = 'conjunction'
            elif formula.operator == '∨':
                value = left.value or right.value
                reason = 'disjunction'
            elif formula.operator == '→':
                value = not left.value or right.value
                reason = 'implication'
            else:
                value = left.value == right.value
                reason = 'biconditional'
            return Trace(**common, value=value, reason=reason, children=(left, right))

        domain = self.request.interpretation.domain
        children = []
        checked = []
        decisive = None
        universal = formula.operator == '∀'
        value = universal
        for index, element in enumerate(domain):
            # Una copia del alcance conserva las asignaciones externas, incluso con sombra.
            local = dict(environment)
            local[formula.variable] = element
            child = self.formula(formula.body, local, node_id + '.0', f'{trace_id}@{index}.0')
            children.append(child)
            checked.append(element)
            if child.value != universal:
                value = child.value
                decisive = element
                break
        if universal:
            reason = 'universal_complete' if value else 'universal_counterexample'
        else:
            reason = 'existential_witness' if value else 'existential_complete'
        return Trace(**common, value=value, reason=reason, children=tuple(children),
                     variable=formula.variable, decisive_element=decisive,
                     checked_elements=tuple(checked), unvisited_elements=domain[len(checked):],
                     domain_size=len(domain),
                     complete=len(checked) == len(domain))


def evaluate(request: ValidatedInput, *,
             cancelled: Callable[[], bool] | None = None) -> EvaluationResult:
    # Evalúa copias certificadas; límites y cancelación lanzan errores, nunca Falso.
    # Los conectivos evalúan ambos operandos. Los cuantificadores solo se detienen
    # ante un testigo o contraejemplo; los otros casos conservan evidencia de todo D.
    if not isinstance(request, ValidatedInput):
        raise TypeError('evaluate requiere una entrada producida por prepare_input.')
    traversal = _Traversal(request, cancelled)
    try:
        trace = traversal.formula(request.formula, dict(request.environment))
    except RecursionError as error:
        raise EvaluationLimitError('La evaluación supera la profundidad disponible.') from error
    return EvaluationResult(trace.value, trace, traversal.steps)
