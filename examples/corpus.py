# Corpus didáctico ejecutado con los módulos reales
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path

from lm_p3.application.service import evaluate_formula
from lm_p3.models.errors import SemanticInputError
from lm_p3.models.language import Interpretation, Language
from lm_p3.models.trace import EvaluationResult
from lm_p3.semantics.comparison import ComparisonResult, compare
from lm_p3.semantics.inputs import ValidatedInput
from lm_p3.syntax.parser import analyze, parse
from lm_p3.validation.normalization import build_environment, build_interpretation, build_language
from lm_p3.validation.validator import validate_input


def load_corpus() -> dict:
    # El archivo se resuelve respecto al módulo, no al directorio desde donde se abre.
    return json.loads(Path(__file__).with_name('red_estaciones.json').read_text(encoding='utf-8'))


def _context(world: dict, assignments: list) -> tuple[Language, Interpretation, dict[str, str]]:
    language = build_language(world['functions'], world['predicates'])
    interpretation = build_interpretation(language, world['domain'], world['function_rows'], world['relations'])
    environment = build_environment(language, world['domain'], assignments)
    return language, interpretation, environment


def evaluate_scenario(world: dict, scenario: dict) -> EvaluationResult:
    # Solo se leen fórmula y datos de entrada; la solución manual no determina verdad.
    language, interpretation, environment = _context(world, scenario['assignments'])
    return evaluate_formula(scenario['formula'], language, interpretation, environment, parse=parse).evaluation


def _certify(world: dict, scenario: dict) -> ValidatedInput:
    language, interpretation, environment = _context(world, scenario['assignments'])
    return validate_input(language, interpretation, parse(scenario['formula'], language), environment)


def comparison_variant(world: dict, scenario: dict) -> tuple[dict, dict]:
    # Se copia el mundo completo y se verifica el dato previo antes de cambiarlo.
    variant = deepcopy(world)
    formula = {'formula': scenario['formula'], 'assignments': deepcopy(scenario['assignments'])}
    change = scenario['change']
    symbol, arguments = change['symbol'], change['arguments']
    if change['kind'] == 'function':
        rows = variant['function_rows'][symbol]
        matches = [row for row in rows if row[0] == arguments]
        if len(matches) != 1:
            raise ValueError('El ejemplo debe identificar una única fila funcional.')
        actual = matches[0][1]
        matches[0][1] = change['after']
    elif change['kind'] == 'relation':
        rows = variant['relations'][symbol]
        actual = arguments in rows
        if change['after'] is True and not actual:
            rows.append(list(arguments))
        elif change['after'] is False and actual:
            rows.remove(arguments)
    elif change['kind'] == 'assignment':
        matches = [row for row in formula['assignments'] if row[0] == symbol]
        if len(matches) != 1:
            raise ValueError('El ejemplo debe identificar una única asignación libre.')
        actual = matches[0][1]
        matches[0][1] = change['after']
    else:
        raise ValueError('Tipo de cambio no admitido por este corpus.')
    if actual != change['before']:
        raise ValueError('El dato previo del ejemplo no coincide con el mundo base.')
    return variant, formula


def compare_scenario(world: dict, scenario: dict) -> ComparisonResult:
    base = _certify(world, scenario)
    variant_world, variant_scenario = comparison_variant(world, scenario)
    variant = _certify(variant_world, variant_scenario)
    return compare(base, variant)


def invalid_scenario(world: dict, defaults: dict, case: dict, *, repaired: bool = False) -> tuple[dict, dict]:
    # Cada parche sustituye campos completos de entrada; conserva intacta la fuente.
    candidate_world, candidate = deepcopy(world), deepcopy(defaults)
    for patch in (case['overrides'], case['repair']) if repaired else (case['overrides'],):
        candidate_world.update(deepcopy(patch.get('world', {})))
        for key in ('formula', 'assignments'):
            if key in patch:
                candidate[key] = deepcopy(patch[key])
    return candidate_world, candidate


def _diagnostics(error: SemanticInputError) -> list[dict]:
    diagnostics = []
    for issue in getattr(error, 'errors', (error,)):
        span = getattr(issue, 'span', None)
        diagnostics.append({'code': issue.code, 'message': issue.message, 'field': issue.field,
                            'span': None if span is None else asdict(span),
                            'details': dict(getattr(issue, 'details', {}))})
    return diagnostics


def run_corpus(data: dict | None = None, *, case_id: str | None = None) -> dict:
    data = load_corpus() if data is None else data
    if data['version'] != 1:
        raise ValueError('Versión de corpus no admitida.')
    world = data['world']
    report = {'title': data['title'], 'world': deepcopy(world),
              'evaluations': [], 'comparisons': [], 'invalid_cases': []}
    available = {case['id'] for group in ('scenarios', 'comparisons', 'invalid_cases') for case in data[group]}
    if case_id is not None and case_id not in available:
        raise ValueError(f'Caso desconocido: {case_id}.')
    language = build_language(world['functions'], world['predicates'])
    for scenario in data['scenarios']:
        if case_id is not None and scenario['id'] != case_id:
            continue
        analysis = analyze(scenario['formula'], language)
        result = evaluate_scenario(world, scenario)
        report['evaluations'].append({'id': scenario['id'], 'formula': scenario['formula'],
                                      'free_variables': sorted(analysis.free_variables),
                                      'evaluation': asdict(result)})
    for scenario in data['comparisons']:
        if case_id is not None and scenario['id'] != case_id:
            continue
        comparison = compare_scenario(world, scenario)
        report['comparisons'].append({'id': scenario['id'], 'formula': scenario['formula'],
                                      'comparison': dict(asdict(comparison), truth_changed=comparison.truth_changed)})
    for case in data['invalid_cases']:
        if case_id is not None and case['id'] != case_id:
            continue
        failed_world, failed = invalid_scenario(world, data['invalid_base'], case)
        try:
            evaluate_scenario(failed_world, failed)
        except SemanticInputError as error:
            diagnostics = _diagnostics(error)
        else:
            raise RuntimeError(f'{case["id"]} no fue rechazado; revisa el ejemplo de error.')
        fixed_world, fixed = invalid_scenario(world, data['invalid_base'], case, repaired=True)
        corrected = evaluate_scenario(fixed_world, fixed)
        report['invalid_cases'].append({'id': case['id'], 'status': 'no_evaluado', 'errors': diagnostics,
                                        'repaired': {'formula': fixed['formula'], 'evaluation': asdict(corrected)}})
    return report


def _summary(trace: dict) -> str:
    # El resumen procede de la traza calculada, nunca de la solución manual esperada.
    reason = trace['reason']
    if reason in ('existential_witness', 'universal_counterexample'):
        label = 'Testigo' if reason == 'existential_witness' else 'Contraejemplo'
        return f'{label}: {trace["variable"]}={trace["decisive_element"]}'
    if reason == 'existential_complete':
        return f'Ningún elemento cumple; comprobados {len(trace["checked_elements"])} de {trace["domain_size"]}'
    if reason == 'universal_complete':
        return f'Comprobados {len(trace["checked_elements"])} de {trace["domain_size"]} elementos'
    return 'Detalle de subfórmulas y términos disponible con --json'


def main() -> None:
    data = load_corpus()
    parser = argparse.ArgumentParser(description='Corpus real de M2-04: Red de estaciones.')
    ids = [case['id'] for group in ('scenarios', 'comparisons', 'invalid_cases') for case in data[group]]
    parser.add_argument('--case', choices=ids, help='Ejecutar un caso y conservar su evidencia completa.')
    parser.add_argument('--json', action='store_true', help='Mostrar el informe calculado y sus trazas.')
    args = parser.parse_args()
    report = run_corpus(data, case_id=args.case)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    print(report['title'])
    for record in report['evaluations']:
        result = record['evaluation']
        print(f'{record["id"]} {record["formula"]}: {"Verdadero" if result["value"] else "Falso"}. '
              f'{_summary(result["trace"])}; variables libres={record["free_variables"]}')
    for record in report['comparisons']:
        result = record['comparison']
        old, new = result['before']['value'], result['after']['value']
        change = result['change']
        target = (change['symbol'] if change['kind'] == 'assignment' else
                  f'{change["symbol"]}({", ".join(change["arguments"])})')
        before, after = change['before'], change['after']
        if change['kind'] == 'relation':
            before = 'pertenece' if before else 'no pertenece'
            after = 'pertenece' if after else 'no pertenece'
        print(f'{record["id"]} {target}: {before} → {after}; '
              f'{"Verdadero" if old else "Falso"} → {"Verdadero" if new else "Falso"}; '
              f'{"cambia la verdad" if result["truth_changed"] else "la verdad se mantiene"}')
        if result['before']['trace']['reason'] == result['after']['trace']['reason'] == 'existential_witness':
            print(f'  Testigos calculados: {result["before"]["trace"]["decisive_element"]} → '
                  f'{result["after"]["trace"]["decisive_element"]}')
    for record in report['invalid_cases']:
        first = record['errors'][0]
        corrected = record['repaired']['evaluation']['value']
        print(f'{record["id"]} No evaluado: {first["code"]} en {first["field"]}. '
              f'Tras corregir: {"Verdadero" if corrected else "Falso"}.')


if __name__ == '__main__':
    main()
