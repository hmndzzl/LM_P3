# Demostración real del motor sobre AST; no sustituye al parser ni a la interfaz.
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from time import perf_counter

from lm_p3.models.ast import Binary, Function, Not, Predicate, Quantifier, Variable
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.comparison import compare
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import prepare_input


def sample_world() -> tuple[Language, Interpretation]:
    return (
        Language({'f': 1, 'a': 0}, {'P': 1, 'R': 2}),
        Interpretation(('a', 'b'), {'f': {('a',): 'b', ('b',): 'a'}, 'a': {(): 'a'}},
                       {'P': {('a',)}, 'R': {('a', 'b')}}),
    )


def demonstration() -> dict:
    language, interpretation = sample_world()
    p = Predicate('P', (Variable('x'),))
    formulas = [Quantifier('∃', 'x', p), Quantifier('∀', 'x', p),
                Quantifier('∀', 'x', Binary('∨', p, Not(p))),
                Quantifier('∃', 'x', Binary('∧', p, Not(p)))]
    results = [evaluate(prepare_input(language, interpretation, f)) for f in formulas]
    formula = Predicate('P', (Function('f', (Function('a'),)),))
    base = prepare_input(language, interpretation, formula)
    variant = prepare_input(language, Interpretation(
        interpretation.domain, {'f': {('a',): 'a', ('b',): 'a'}, 'a': {(): 'a'}},
        interpretation.relations), formula)
    comparison = compare(base, variant)
    return {'evaluations': [asdict(r) for r in results],
            'comparison': dict(asdict(comparison), truth_changed=comparison.truth_changed)}


def benchmark() -> list[dict]:
    records = []
    for size in (2, 30):
        domain = tuple(str(i) for i in range(size))
        language = Language({}, {'P': 1})
        interpretation = Interpretation(domain, {}, {'P': {(x,) for x in domain}})
        body = Predicate('P', (Variable('x'),))
        formula = Quantifier('∀', 'x', Quantifier('∀', 'y', Quantifier('∀', 'z', body)))
        started = perf_counter()
        result = evaluate(prepare_input(language, interpretation, formula))
        elapsed = perf_counter() - started
        records.append({'domain_size': size, 'value': result.value,
                        'steps': result.steps, 'seconds': round(elapsed, 6)})
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description='Demostración de la semántica de Miembro 1.')
    parser.add_argument('--json', action='store_true', help='Mostrar trazas estructuradas completas.')
    parser.add_argument('--benchmark', action='store_true', help='Medir dos dominios finitos.')
    args = parser.parse_args()
    if args.benchmark:
        print(json.dumps(benchmark(), ensure_ascii=False, indent=2))
        return
    data = demonstration()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    for result in data['evaluations']:
        trace = result['trace']
        value = 'Verdadero' if result['value'] else 'Falso'
        print(f"{trace['formula']}: {value}; razón={trace['reason']}; "
              f"elemento decisivo={trace['decisive_element']}; "
              f"comprobados={trace['checked_elements']}")
    comparison = data['comparison']
    print('Comparación f(a): b → a; verdad antes/después:',
          comparison['before']['value'], comparison['after']['value'])


if __name__ == '__main__':
    main()
