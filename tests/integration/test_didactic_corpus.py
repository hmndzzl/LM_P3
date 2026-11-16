from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from examples.corpus import (compare_scenario, comparison_variant, evaluate_scenario,
                             invalid_scenario, load_corpus, run_corpus)
from lm_p3.models.errors import SemanticInputError
from lm_p3.semantics.evaluator import evaluate
from lm_p3.syntax.parser import analyze
from lm_p3.validation.normalization import build_language


class DidacticCorpusTests(unittest.TestCase):
    def setUp(self):
        self.data = load_corpus()
        path = Path(__file__).resolve().parents[1] / 'fixtures' / 'corpus_expectations.json'
        self.expected = json.loads(path.read_text(encoding='utf-8'))
        self.scenarios = {case['id']: case for case in self.data['scenarios']}
        self.comparisons = {case['id']: case for case in self.data['comparisons']}
        self.language = build_language(self.data['world']['functions'], self.data['world']['predicates'])

    def result(self, case_id):
        return evaluate_scenario(self.data['world'], self.scenarios[case_id])

    def test_ten_manual_solutions_match_real_text_evaluations_and_free_variables(self):
        self.assertEqual(self.data['version'], self.expected['version'])
        self.assertEqual(set(self.scenarios), set(self.expected['scenarios']))
        for case_id, scenario in self.scenarios.items():
            with self.subTest(case_id=case_id):
                expected = self.expected['scenarios'][case_id]
                result = self.result(case_id)
                analysis = analyze(scenario['formula'], self.language)
                self.assertIs(result.value, expected['value'])
                self.assertEqual(sorted(analysis.free_variables), expected['free_variables'])
                self.assertEqual(result.trace.reason, expected['reason'])
                self.assertEqual(result.trace.decisive_element, expected['decisive_element'])
                self.assertEqual(list(result.trace.checked_elements), expected['checked_elements'])
                self.assertIs(result.trace.complete, expected['complete'])
                self.assertEqual(result.trace.span.start, 0)
                self.assertEqual(result.trace.span.end, len(scenario['formula']))

    def test_universal_complete_case_has_a_different_inner_witness_for_each_station(self):
        trace = self.result('Q03').trace
        self.assertEqual(trace.checked_elements, ('norte', 'centro', 'sur'))
        self.assertEqual([dict(child.environment)['x'] for child in trace.children], ['norte', 'centro', 'sur'])
        self.assertEqual([child.decisive_element for child in trace.children], ['centro', 'sur', 'norte'])
        self.assertEqual([child.checked_elements for child in trace.children],
                         [('norte', 'centro'), ('norte', 'centro', 'sur'), ('norte',)])
        self.assertTrue(all(child.reason == 'existential_witness' for child in trace.children))
        self.assertEqual(len({child.node_id for child in trace.children}), 1)
        self.assertEqual(len({child.trace_id for child in trace.children}), 3)

    def test_false_existential_has_all_three_manual_assignments_and_atomic_values(self):
        trace = self.result('Q04').trace
        self.assertEqual(trace.unvisited_elements, ())
        self.assertEqual([dict(child.environment)['x'] for child in trace.children], ['norte', 'centro', 'sur'])
        atom_values = [(child.children[0].children[0].value, child.children[0].children[1].value,
                        child.children[1].value) for child in trace.children]
        self.assertEqual(atom_values, [(True, True, False), (True, False, True), (False, True, True)])
        self.assertTrue(all(not child.value for child in trace.children))

    def test_unvisited_is_distinct_from_false_and_complete_is_not_a_truth_value(self):
        witness = self.result('Q01').trace
        self.assertEqual(witness.unvisited_elements, ('centro', 'sur'))
        self.assertEqual(len(witness.children), 1)
        self.assertFalse(witness.complete)
        counterexample = self.result('Q02').trace
        self.assertFalse(counterexample.value)
        self.assertTrue(counterexample.complete)
        self.assertEqual(counterexample.reason, 'universal_counterexample')

    def test_minimum_scope_and_shadowing_keep_the_external_assignment(self):
        self.assertTrue(self.result('S02').value)
        self.assertFalse(self.result('S03').value)
        before = deepcopy(self.scenarios['S04'])
        trace = self.result('S04').trace
        self.assertTrue(trace.value)
        self.assertEqual(dict(trace.children[1].environment)['x'], 'sur')
        universal = trace.children[0]
        self.assertEqual([dict(child.environment)['x'] for child in universal.children], ['norte', 'centro', 'sur'])
        inner = [child.children[1] for child in universal.children]
        self.assertEqual([child.decisive_element for child in inner], ['sur'] * 3)
        self.assertEqual(self.scenarios['S04'], before)

    def test_three_real_comparisons_match_manual_truth_and_changed_data(self):
        original = deepcopy(self.data)
        for case_id, scenario in self.comparisons.items():
            with self.subTest(case_id=case_id):
                expected = self.expected['comparisons'][case_id]
                result = compare_scenario(self.data['world'], scenario)
                self.assertIs(result.before.value, expected['before'])
                self.assertIs(result.after.value, expected['after'])
                self.assertIs(result.truth_changed, expected['truth_changed'])
                self.assertEqual(result.before.trace.decisive_element, expected['witness_before'])
                self.assertEqual(result.after.trace.decisive_element, expected['witness_after'])
                actual = asdict(result.change)
                actual['arguments'] = list(actual['arguments'])
                self.assertEqual(actual, scenario['change'])
                self.assertTrue(result.evidence_changes)
        self.assertEqual(self.data, original)

    def test_same_truth_comparison_changes_the_witness_and_exposes_new_visited_evidence(self):
        result = compare_scenario(self.data['world'], self.comparisons['C02'])
        self.assertTrue(result.before.value and result.after.value)
        self.assertFalse(result.truth_changed)
        self.assertEqual((result.before.trace.decisive_element, result.after.trace.decisive_element),
                         ('norte', 'centro'))
        self.assertTrue(any(change.before is None and change.after is not None for change in result.evidence_changes))
        variant, _ = comparison_variant(self.data['world'], self.comparisons['C02'])
        self.assertEqual(variant['relations']['Activa'], [['centro']])

    def test_each_invalid_case_blocks_engine_and_its_specific_repair_evaluates(self):
        self.assertEqual(len(self.data['invalid_cases']), 11)
        for case in self.data['invalid_cases']:
            with self.subTest(case_id=case['id']), patch('lm_p3.application.service.evaluate', wraps=evaluate) as engine:
                failed_world, failed = invalid_scenario(self.data['world'], self.data['invalid_base'], case)
                with self.assertRaises(SemanticInputError) as caught:
                    evaluate_scenario(failed_world, failed)
                error = caught.exception
                expected = self.expected['invalid_cases'][case['id']]
                self.assertEqual({'code': error.code, 'field': error.field}, expected['expected_error'])
                self.assertFalse(hasattr(error, 'value'))
                engine.assert_not_called()
                fixed_world, fixed = invalid_scenario(self.data['world'], self.data['invalid_base'], case, repaired=True)
                self.assertIs(evaluate_scenario(fixed_world, fixed).value, expected['fixed_value'])
                self.assertEqual(engine.call_count, 1)

    def test_full_report_is_serializable_observed_evidence_and_preserves_sources(self):
        original = deepcopy(self.data)
        report = run_corpus(self.data)
        self.assertEqual((len(report['evaluations']), len(report['comparisons']), len(report['invalid_cases'])), (10, 3, 11))
        self.assertEqual(len(json.loads(json.dumps(report))['evaluations']), 10)
        for record in report['invalid_cases']:
            self.assertEqual(record['status'], 'no_evaluado')
            self.assertNotIn('value', record)
            self.assertNotIn('evaluation', record)
            self.assertIn('evaluation', record['repaired'])
        self.assertEqual(self.data, original)

    def test_reference_prose_and_injected_expectations_do_not_determine_truth(self):
        scenario = deepcopy(self.scenarios['Q01'])
        scenario['manual_reason'] = 'Referencia deliberadamente incorrecta para comprobar independencia.'
        scenario['expected'] = {'value': False}
        self.assertTrue(evaluate_scenario(self.data['world'], scenario).value)
        self.assertNotIn('expected', self.scenarios['Q01'])

    def test_selection_and_unknown_case_or_version(self):
        report = run_corpus(self.data, case_id='C02')
        self.assertEqual(report['evaluations'], [])
        self.assertEqual(report['invalid_cases'], [])
        self.assertEqual([case['id'] for case in report['comparisons']], ['C02'])
        with self.assertRaises(ValueError):
            run_corpus(self.data, case_id='missing')
        data = deepcopy(self.data)
        data['version'] = 999
        with self.assertRaises(ValueError):
            run_corpus(data)
        comparison = deepcopy(self.comparisons['C01'])
        comparison['change']['before'] = 'norte'
        with self.assertRaises(ValueError):
            compare_scenario(self.data['world'], comparison)

    def test_cli_selected_comparison_outputs_real_json(self):
        root = Path(__file__).resolve().parents[2]
        process = subprocess.run([sys.executable, '-X', 'utf8', '-B', '-m', 'examples.corpus',
                                  '--case', 'C02', '--json'], cwd=root, capture_output=True, encoding='utf-8')
        self.assertEqual(process.returncode, 0, process.stderr)
        comparison = json.loads(process.stdout)['comparisons'][0]['comparison']
        self.assertFalse(comparison['truth_changed'])
        self.assertEqual(comparison['before']['trace']['decisive_element'], 'norte')
        self.assertEqual(comparison['after']['trace']['decisive_element'], 'centro')


if __name__ == '__main__':
    unittest.main()
