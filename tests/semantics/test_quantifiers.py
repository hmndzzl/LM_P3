import unittest
from itertools import product
from concurrent.futures import ThreadPoolExecutor

from lm_p3.models.ast import Binary, Function, Not, Predicate, Quantifier, Span, Variable
from lm_p3.models.errors import EvaluationCancelledError, EvaluationLimitError
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import EvaluationLimits, prepare_input
from tests.semantics.test_evaluator import world


class LogicalEvaluationTests(unittest.TestCase):
    def test_every_binary_truth_table(self):
        for left, right in product((False, True), repeat=2):
            p = Predicate('P', (Function('a'),))
            a = p if left else Not(p)
            b = p if right else Not(p)
            expected = {'∧': left and right, '∨': left or right,
                        '→': not left or right, '↔': left == right}
            for operator, value in expected.items():
                with self.subTest(operator=operator, left=left, right=right):
                    result = evaluate(world(Binary(operator, a, b)))
                    self.assertEqual(result.value, value)
                    self.assertEqual([c.value for c in result.trace.children], [left, right])

    def test_double_negation(self):
        self.assertTrue(evaluate(world(Not(Not(Predicate('P', (Function('a'),)))))).value)

    def test_four_quantifier_outcomes_and_required_coverage(self):
        p = Predicate('P', (Variable('x'),))
        cases = [
            (Quantifier('∃', 'x', p), True, 'a', ('a',), 'existential_witness'),
            (Quantifier('∀', 'x', p), False, 'b', ('a', 'b'), 'universal_counterexample'),
            (Quantifier('∀', 'x', Binary('∨', p, Not(p))), True, None, ('a', 'b'), 'universal_complete'),
            (Quantifier('∃', 'x', Binary('∧', p, Not(p))), False, None, ('a', 'b'), 'existential_complete'),
        ]
        for formula, value, decisive, checked, reason in cases:
            with self.subTest(reason=reason):
                result = evaluate(world(formula))
                self.assertEqual(result.value, value)
                self.assertEqual(result.trace.decisive_element, decisive)
                self.assertEqual(result.trace.checked_elements, checked)
                self.assertEqual(result.trace.reason, reason)
                self.assertEqual(result.trace.complete, len(checked) == 2)
                self.assertEqual(result.trace.unvisited_elements, ('a', 'b')[len(checked):])
                self.assertEqual(result.trace.domain_size, 2)
                self.assertEqual(len(result.trace.children), len(checked))
                self.assertEqual([dict(t.environment)['x'] for t in result.trace.children], list(checked))

    def test_nested_quantifiers_retain_correct_assignment(self):
        formula = Quantifier('∀', 'x', Quantifier('∃', 'y', Predicate('R', (Variable('x'), Variable('y')))))
        result = evaluate(world(formula))
        self.assertFalse(result.value)
        self.assertEqual(result.trace.decisive_element, 'b')
        first, second = result.trace.children
        self.assertEqual(first.decisive_element, 'b')
        self.assertEqual(second.checked_elements, ('a', 'b'))
        self.assertEqual(dict(second.children[-1].environment), {'x': 'b', 'y': 'b'})
        self.assertEqual(first.children[0].node_id, second.children[0].node_id)
        self.assertNotEqual(first.children[0].trace_id, second.children[0].trace_id)

    def test_shadowing_does_not_leak_into_sibling_or_next_evaluation(self):
        p = Predicate('P', (Variable('x'),))
        formula = Binary('∧', Quantifier('∃', 'x', p), Not(p))
        request = world(formula, {'x': 'b'})
        for _ in range(2):
            result = evaluate(request)
            self.assertTrue(result.value)
            self.assertEqual(dict(result.trace.children[1].environment)['x'], 'b')
            self.assertEqual(dict(request.environment), {'x': 'b'})
        nested = Quantifier('∀', 'x', Binary('↔', p, Binary('∧', Quantifier('∃', 'x', p), p)))
        self.assertTrue(evaluate(world(nested)).value)

    def test_source_span_is_preserved(self):
        p = Predicate('P', (Variable('x'),), span=Span(2, 6))
        self.assertEqual(evaluate(world(p, {'x': 'a'})).trace.span, Span(2, 6))

    def test_budget_exhaustion_returns_no_result(self):
        original = world(Quantifier('∀', 'x', Predicate('P', (Variable('x'),))))
        request = prepare_input(original.language, original.interpretation, original.formula,
                                limits=EvaluationLimits(max_steps=2))
        with self.assertRaises(EvaluationLimitError):
            evaluate(request)
        self.assertFalse(evaluate(original).value)

    def test_cancellation_does_not_turn_into_false_or_poison_next_run(self):
        request = world(Predicate('P', (Function('a'),)))
        with self.assertRaises(EvaluationCancelledError):
            evaluate(request, cancelled=lambda: True)
        self.assertTrue(evaluate(request).value)

    def test_same_snapshot_can_be_evaluated_concurrently(self):
        request = world(Quantifier('∀', 'x', Predicate('P', (Variable('x'),))))
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(evaluate, [request] * 12))
        self.assertTrue(all(result == results[0] for result in results))
        self.assertFalse(results[0].value)
        self.assertEqual(dict(request.environment), {})

    def test_cancellation_during_traversal_discards_partial_evidence(self):
        request = world(Quantifier('∀', 'x', Predicate('P', (Variable('x'),))))
        calls = 0
        def cancelled():
            nonlocal calls
            calls += 1
            return calls == 4
        with self.assertRaises(EvaluationCancelledError):
            evaluate(request, cancelled=cancelled)
        self.assertFalse(evaluate(request).value)


if __name__ == '__main__':
    unittest.main()
