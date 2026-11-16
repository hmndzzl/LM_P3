from dataclasses import replace
import unittest
from unittest.mock import patch

from lm_p3.application.service import evaluate_formula
from lm_p3.models.ast import Binary, Function, Not, Predicate, Quantifier, Span, Variable
from lm_p3.models.errors import EvaluationLimitError, InputValidationError
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import EvaluationLimits, ValidatedInput
from lm_p3.syntax.parser import parse
from lm_p3.validation.validator import collect_errors, validate_input


class IntegralValidationTests(unittest.TestCase):
    def setUp(self):
        self.language = Language({'f': 1}, {'P': 1})
        self.interpretation = Interpretation(('a', 'b'), {'f': {('a',): 'b', ('b',): 'a'}},
                                            {'P': {('a',)}})
        self.formula = parse('P(x)', self.language)

    def errors(self, formula=None, interpretation=None, environment=None, language=None, **kwargs):
        return collect_errors(self.language if language is None else language,
                              self.interpretation if interpretation is None else interpretation,
                              self.formula if formula is None else formula,
                              {'x': 'a'} if environment is None else environment, **kwargs)

    def test_valid_context_is_certified_without_changing_it(self):
        limits = EvaluationLimits(max_steps=12)
        request = validate_input(self.language, self.interpretation, self.formula, {'x': 'a'}, limits=limits)
        self.assertIsInstance(request, ValidatedInput)
        self.assertEqual(request.formula, self.formula)
        self.assertEqual(request.language, self.language)
        self.assertEqual(request.interpretation, self.interpretation)
        self.assertEqual(request.limits, limits)
        self.assertEqual(request.free_variables, {'x'})
        self.assertEqual(dict(request.environment), {'x': 'a'})
        self.assertTrue(evaluate(request).value)

    def test_all_interpretation_environment_and_ast_errors_are_collected(self):
        bad = Interpretation(('a', 'b'), {'f': {}}, {'P': set()})
        formula = Binary('∨', Predicate('Unknown', (Variable('z'),)), self.formula)
        errors = self.errors(formula, bad, {})
        self.assertEqual([issue.code for issue in errors],
                         ['empty_interpretation', 'empty_interpretation', 'unknown_symbol',
                          'missing_assignment', 'missing_assignment'])
        self.assertEqual([issue.field for issue in errors[-2:]], ['environment.x', 'environment.z'])

    def test_invalid_branch_of_decisive_existential_is_not_skipped(self):
        formula = Quantifier('∃', 'x', Binary('∨', self.formula, Predicate('Unknown', (Variable('x'),))))
        errors = self.errors(formula, environment={})
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, 'unknown_symbol')
        with patch('lm_p3.application.service.evaluate') as engine:
            with self.assertRaises(InputValidationError):
                evaluate_formula('ignored', self.language, self.interpretation, {},
                                 parse=lambda text, language: formula)
            engine.assert_not_called()

    def test_all_declared_tables_are_validated_when_formula_does_not_use_them(self):
        bad = Interpretation(('a', 'b'), {'f': {('a',): 'b'}}, self.interpretation.relations)
        self.assertIn('partial_function', [issue.code for issue in self.errors(interpretation=bad)])

    def test_environment_requires_all_free_variables_and_all_values_in_domain(self):
        formula = parse('P(x) & P(y)', self.language)
        errors = self.errors(formula, environment={'x': 'outside', 'extra': 'outside'})
        self.assertEqual([issue.code for issue in errors],
                         ['invalid_assignment', 'invalid_assignment', 'missing_assignment'])
        self.assertEqual(errors[-1].field, 'environment.y')

    def test_additional_valid_assignments_are_preserved_without_becoming_free(self):
        formula = parse('∀x P(x)', self.language)
        request = validate_input(self.language, self.interpretation, formula, {'x': 'b', 'extra': 'a'})
        self.assertEqual(request.free_variables, set())
        self.assertEqual(dict(request.environment), {'x': 'b', 'extra': 'a'})

    def test_scope_and_shadowing_determine_only_the_required_assignments(self):
        closed = parse('∀x (P(x) ∨ ∃x P(x))', self.language)
        self.assertEqual(self.errors(closed, environment={}), ())
        open_formula = parse('(∀x P(x)) ∨ P(x)', self.language)
        self.assertEqual([e.field for e in self.errors(open_formula, environment={})], ['environment.x'])

    def test_service_default_rejects_an_invalid_extra_variable_before_engine(self):
        with patch('lm_p3.application.service.evaluate') as engine:
            with self.assertRaises(InputValidationError) as caught:
                evaluate_formula('P(x)', self.language, self.interpretation,
                                 {'x': 'a', 'bad name': 'a'}, parse=parse)
            self.assertEqual(caught.exception.code, 'invalid_variable')
            engine.assert_not_called()

    def test_ast_names_arities_positions_and_node_classes_are_checked(self):
        cases = [(Variable('x'), 'invalid_ast'), (Not(Variable('x')), 'invalid_ast'),
                 (Predicate('P', (Predicate('P'),)), 'invalid_ast'),
                 (Predicate('P', (Function('f'),)), 'arity_mismatch'),
                 (Predicate('P', (Function('unknown'),)), 'unknown_symbol'),
                 (Predicate('P', (Variable('bad name'),)), 'invalid_variable'),
                 (Predicate('P', (Variable('f'),)), 'invalid_variable'),
                 (Quantifier('∀', 'P', self.formula), 'invalid_bound_variable'),
                 (Quantifier('∀', [], self.formula), 'invalid_bound_variable'),
                 (Quantifier('?', 'x', self.formula), 'unknown_quantifier'),
                 (Binary('?', self.formula, self.formula), 'unknown_connective'),
                 (replace(self.formula, span=Span(-1, 1)), 'invalid_span'),
                 (replace(self.formula, span='bad'), 'invalid_span')]
        for formula, code in cases:
            with self.subTest(code=code):
                self.assertIn(code, [issue.code for issue in self.errors(formula)])

    def test_ast_arity_error_exposes_original_position_and_parameters(self):
        formula = Predicate('P', (), Span(2, 5))
        issue = self.errors(formula)[0]
        self.assertEqual(issue.span, Span(2, 5))
        self.assertEqual(dict(issue.details), {'symbol': 'P', 'expected': 1, 'actual': 0})

    def test_malformed_model_values_fail_as_issues_instead_of_python_errors(self):
        cases = [(Interpretation(('a', []), self.interpretation.functions, self.interpretation.relations),
                  'invalid_domain'),
                 (Interpretation(('a', 'b'), {'f': {'a': 'b'}}, self.interpretation.relations),
                  'invalid_structure'),
                 (Interpretation(('a', 'b'), self.interpretation.functions, {'P': {1}}),
                  'invalid_structure')]
        for interpretation, code in cases:
            with self.subTest(code=code):
                self.assertIn(code, [issue.code for issue in self.errors(interpretation=interpretation)])
        self.assertEqual(collect_errors(None, None, None, [])[0].code, 'invalid_structure')
        self.assertIn('invalid_arity', [e.code for e in self.errors(language=Language({}, {'P': []}))])

    def test_limits_propagate_without_truth_and_the_next_request_is_valid(self):
        for limits in (EvaluationLimits(max_input_nodes=1), EvaluationLimits(max_depth=1)):
            with self.subTest(limits=limits), self.assertRaises(EvaluationLimitError) as caught:
                validate_input(self.language, self.interpretation, self.formula, {'x': 'a'}, limits=limits)
            self.assertFalse(hasattr(caught.exception, 'value'))
        self.assertEqual(self.errors(), ())
        with self.assertRaises(TypeError):
            self.errors(limits=False)

    def test_invalid_input_never_gets_a_certificate_or_truth(self):
        with self.assertRaises(InputValidationError) as caught:
            validate_input(self.language, self.interpretation, self.formula, {})
        self.assertFalse(hasattr(caught.exception, 'value'))
        self.assertFalse(hasattr(caught.exception, 'evaluation'))
        with self.assertRaises(ValueError):
            InputValidationError(())


if __name__ == '__main__':
    unittest.main()
