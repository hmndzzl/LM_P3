import unittest

from lm_p3.application.service import evaluate_formula
from lm_p3.models.ast import Function, Predicate
from lm_p3.models.errors import SemanticInputError
from lm_p3.semantics.inputs import EvaluationLimits
from tests.semantics.test_evaluator import world


class EvaluationServiceTests(unittest.TestCase):
    def test_injected_parser_and_real_guard_evaluate_with_revision(self):
        base = world(Predicate('P', (Function('a'),)))
        # Este adaptador mínimo solo permite probar la frontera; no es el parser de M2.
        def parser(text, language):
            self.assertEqual(text, 'P(a)')
            self.assertEqual(language, base.language)
            return base.formula
        outcome = evaluate_formula('P(a)', base.language, base.interpretation, {},
                                   parse=parser, revision=7)
        self.assertTrue(outcome.evaluation.value)
        self.assertEqual(outcome.revision, 7)

    def test_invalid_parser_result_is_rejected_before_truth(self):
        base = world(Predicate('P', (Function('a'),)))
        with self.assertRaises(SemanticInputError):
            evaluate_formula('?', base.language, base.interpretation, {}, parse=lambda text, language: None)

    def test_syntax_error_is_propagated_without_truth(self):
        base = world(Predicate('P', (Function('a'),)))
        def parser(text, language):
            raise SemanticInputError('syntax_error', 'Falta cerrar un paréntesis.', 'formula')
        with self.assertRaisesRegex(SemanticInputError, 'paréntesis'):
            evaluate_formula('P(', base.language, base.interpretation, {}, parse=parser)

    def test_validator_cannot_replace_formula_or_context(self):
        base = world(Predicate('P', (Function('a'),)))
        wrong = world(Predicate('P', (Function('f', (Function('a'),)),)))
        with self.assertRaises(SemanticInputError):
            evaluate_formula('P(a)', base.language, base.interpretation, {},
                             parse=lambda text, language: base.formula,
                             validate=lambda *args, **kwargs: wrong)

    def test_validator_cannot_silently_relax_requested_limits(self):
        base = world(Predicate('P', (Function('a'),)))
        with self.assertRaises(SemanticInputError):
            evaluate_formula('P(a)', base.language, base.interpretation, {},
                             parse=lambda text, language: base.formula,
                             validate=lambda *args, **kwargs: base,
                             limits=EvaluationLimits(max_steps=1))

    def test_revisions_are_nonnegative_integers(self):
        base = world(Predicate('P', (Function('a'),)))
        for revision in (True, -1, '1'):
            with self.subTest(revision=revision), self.assertRaises(SemanticInputError):
                evaluate_formula('P(a)', base.language, base.interpretation, {},
                                 parse=lambda text, language: base.formula, revision=revision)


if __name__ == '__main__':
    unittest.main()
