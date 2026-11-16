import json
from pathlib import Path
import unittest

from lm_p3.application.service import evaluate_formula
from lm_p3.models.errors import FormulaSyntaxError, SemanticInputError
from lm_p3.models.language import Interpretation, Language
from lm_p3.syntax.parser import analyze, parse


class TextEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.language = Language({'f': 1}, {'P': 1, 'Q': 1, 'R': 2})
        self.interpretation = Interpretation(('a', 'b'),
            {'f': {('a',): 'b', ('b',): 'a'}},
            {'P': {('a',)}, 'Q': {('b',)}, 'R': {('a', 'b')}})

    def evaluate(self, text, environment=None, interpretation=None):
        return evaluate_formula(text, self.language, interpretation or self.interpretation,
                                environment or {}, parse=parse, revision=7)

    def test_real_text_parser_and_engine_evaluate_nested_terms(self):
        self.assertTrue(self.evaluate('P(f(f(x)))', {'x': 'a'}).evaluation.value)
        self.assertFalse(self.evaluate('P(f(x))', {'x': 'a'}).evaluation.value)
        self.assertEqual(self.evaluate('P(x)', {'x': 'a'}).revision, 7)

    def test_zero_arity_symbols_and_named_equality_use_declared_interpretations(self):
        language = Language({'c': 0}, {'T': 0, 'P': 1, 'Igual': 2})
        interpretation = Interpretation(('a', 'b'), {'c': {(): 'a'}},
                                        {'T': {()}, 'P': {('a',)}, 'Igual': {('a', 'a'), ('b', 'b')}})
        for text in ('T() ↔ P(c)', '∀x Igual(x,x)', '∃x Igual(x,c())'):
            with self.subTest(text=text):
                outcome = evaluate_formula(text, language, interpretation, {}, parse=parse)
                self.assertTrue(outcome.evaluation.value)

    def test_custom_language_and_three_element_domain_are_not_precalculated_examples(self):
        language = Language({'siguiente': 1}, {'Listo': 1})
        interpretation = Interpretation(('uno', 'dos', 'tres'),
            {'siguiente': {('uno',): 'dos', ('dos',): 'tres', ('tres',): 'uno'}},
            {'Listo': {('tres',)}})
        outcome = evaluate_formula('Epersona Listo(siguiente(persona))', language,
                                   interpretation, {}, parse=parse)
        self.assertTrue(outcome.evaluation.value)
        self.assertEqual(outcome.evaluation.trace.decisive_element, 'dos')

    def test_four_quantified_outcomes_and_required_evidence(self):
        cases = [('Ex P(x)', True, 'existential_witness', 'a'),
                 ('Ax P(x)', False, 'universal_counterexample', 'b'),
                 ('∀x (P(x) ∨ ¬P(x))', True, 'universal_complete', None),
                 ('∃x (P(x) ∧ ¬P(x))', False, 'existential_complete', None)]
        for text, value, reason, decisive in cases:
            with self.subTest(text=text):
                result = self.evaluate(text).evaluation
                self.assertIs(result.value, value)
                self.assertEqual(result.trace.reason, reason)
                self.assertEqual(result.trace.decisive_element, decisive)
                self.assertEqual(result.trace.span.start, 0)
                self.assertEqual(result.trace.span.end, len(text))
                if decisive is None:
                    self.assertTrue(result.trace.complete)
                    self.assertEqual(result.trace.checked_elements, ('a', 'b'))
                    self.assertEqual(len(result.trace.children), 2)

    def test_open_formula_analysis_does_not_require_an_environment(self):
        self.assertEqual(analyze('∀x R(x,y) ∧ P(x)', self.language).free_variables, {'x', 'y'})
        for environment in ({}, {'x': 'fuera'}):
            with self.subTest(environment=environment), self.assertRaises(SemanticInputError) as caught:
                self.evaluate('P(x)', environment)
            self.assertFalse(hasattr(caught.exception, 'value'))
        self.assertTrue(self.evaluate('P(x)', {'x': 'a'}).evaluation.value)

    def test_minimal_scope_changes_truth_and_shadowing_restores_outer_assignment(self):
        self.assertTrue(self.evaluate('Ex P(x) & ~P(x)', {'x': 'b'}).evaluation.value)
        self.assertFalse(self.evaluate('Ex (P(x) & ~P(x))').evaluation.value)
        self.assertFalse(self.evaluate('(Ax (P(x) | Ex Q(x))) & P(x)', {'x': 'b'}).evaluation.value)
        self.assertFalse(self.evaluate('∀x ∃y R(x,y)').evaluation.value)

    def test_invalid_unvisited_body_and_unused_tables_never_receive_truth(self):
        with self.assertRaises(FormulaSyntaxError):
            self.evaluate('∃x (P(x) ∨ NoDeclarado(x))')
        invalid = Interpretation(('a', 'b'), {'f': {('a',): 'b'}}, self.interpretation.relations)
        with self.assertRaises(SemanticInputError) as caught:
            self.evaluate('∃x P(x)', interpretation=invalid)
        self.assertEqual(caught.exception.code, 'partial_function')
        self.assertFalse(hasattr(caught.exception, 'value'))

    def test_shared_fixtures_have_manual_outcomes_with_real_parser(self):
        path = Path(__file__).resolve().parents[1] / 'fixtures' / 'syntax_cases.json'
        fixture = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(fixture['version'], 1)
        language = Language(**fixture['language'])
        data = fixture['interpretation']
        interpretation = Interpretation(tuple(data['domain']),
            {name: {tuple(arguments): output for arguments, output in rows}
             for name, rows in data['function_rows'].items()},
            {name: {tuple(row) for row in rows} for name, rows in data['relations'].items()})
        for case in fixture['cases']:
            with self.subTest(text=case['text']):
                analysis = analyze(case['text'], language)
                self.assertEqual(analysis.free_variables, set(case['free_variables']))
                outcome = evaluate_formula(case['text'], language, interpretation,
                                           case['environment'], parse=parse)
                self.assertIs(outcome.evaluation.value, case['value'])
                self.assertEqual(outcome.evaluation.trace.reason, case['reason'])


if __name__ == '__main__':
    unittest.main()
