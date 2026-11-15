# Casos de aceptación resueltos independientemente del evaluador.
import unittest

from lm_p3.models.ast import Binary, Function, Not, Predicate, Quantifier, Variable
from lm_p3.models.errors import SemanticInputError
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import prepare_input


def world(formula, environment=None):
    language = Language(functions={'f': 1, 'a': 0}, predicates={'P': 1, 'R': 2})
    interpretation = Interpretation(
        domain=('a', 'b'),
        functions={'f': {('a',): 'b', ('b',): 'a'}, 'a': {(): 'a'}},
        relations={'P': {('a',)}, 'R': {('a', 'b')}},
    )
    return prepare_input(language, interpretation, formula, environment or {})


class AtomicEvaluationTests(unittest.TestCase):
    def test_function_application_and_nested_terms_have_evidence(self):
        false_result = evaluate(world(Predicate('P', (Function('f', (Function('a'),)),))))
        self.assertFalse(false_result.value)
        self.assertEqual(false_result.trace.terms[0].value, 'b')
        self.assertEqual(false_result.trace.terms[0].children[0].value, 'a')
        true_result = evaluate(world(Predicate('P', (Function('f', (Function('f', (Function('a'),)),)),))))
        self.assertTrue(true_result.value)
        self.assertEqual(true_result.trace.reason, 'predicate_member')

    def test_open_formula_uses_environment_without_mutation(self):
        env = {'x': 'a'}
        inp = world(Predicate('P', (Variable('x'),)), env)
        self.assertTrue(evaluate(inp).value)
        env['x'] = 'b'
        self.assertTrue(evaluate(inp).value, 'La entrada debe conservar una copia inmutable')
        self.assertFalse(evaluate(world(inp.formula, env)).value)

    def test_rejects_unvalidated_objects(self):
        with self.assertRaises(TypeError):
            evaluate({'value': True})

    def test_invalid_inputs_never_receive_truth_even_on_unused_branch(self):
        formulas = [Predicate('Unknown'), Predicate('P', ()),
                    Predicate('P', (Variable('missing'),)),
                    Binary('∨', Predicate('P', (Function('a'),)), Predicate('Unknown'))]
        for formula in formulas:
            with self.subTest(formula=formula), self.assertRaises(SemanticInputError):
                world(formula)

    def test_custom_symbols_binary_function_and_three_element_domain(self):
        language = Language({'combinar': 2}, {'Coincide': 2})
        domain = ('rojo', 'verde', 'azul')
        table = {(a, b): b for a in domain for b in domain}
        interpretation = Interpretation(domain, {'combinar': table},
                                        {'Coincide': {(a, a) for a in domain}})
        formula = Predicate('Coincide', (Function('combinar', (Variable('x'), Variable('y'))), Variable('y')))
        request = prepare_input(language, interpretation, formula, {'x': 'rojo', 'y': 'azul'})
        result = evaluate(request)
        self.assertTrue(result.value)
        self.assertEqual(result.trace.terms[0].value, 'azul')


if __name__ == '__main__':
    unittest.main()
