import unittest

from lm_p3.models.ast import Binary, Function, Predicate, Quantifier, Variable
from lm_p3.models.errors import SemanticInputError
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.comparison import compare
from lm_p3.semantics.inputs import prepare_input
from tests.semantics.test_evaluator import world


def variant(base, *, functions=None, relations=None, environment=None, formula=None, domain=None):
    old = base.interpretation
    return prepare_input(base.language, Interpretation(domain or old.domain,
                         functions if functions is not None else old.functions,
                         relations if relations is not None else old.relations),
                         formula if formula is not None else base.formula,
                         environment if environment is not None else base.environment)


class ComparisonTests(unittest.TestCase):
    def test_one_function_output_changes_truth_without_mutating_base(self):
        base = world(Predicate('P', (Function('f', (Function('a'),)),)))
        changed = variant(base, functions={'f': {('a',): 'a', ('b',): 'a'}, 'a': {(): 'a'}})
        result = compare(base, changed)
        self.assertFalse(result.before.value)
        self.assertTrue(result.after.value)
        self.assertTrue(result.truth_changed)
        self.assertEqual((result.change.kind, result.change.symbol, result.change.arguments), ('function', 'f', ('a',)))
        self.assertEqual((result.change.before, result.change.after), ('b', 'a'))
        self.assertEqual(base.interpretation.functions['f'][('a',)], 'b')
        self.assertIn('0', [change.trace_id for change in result.evidence_changes])

    def test_one_irrelevant_function_output_preserves_truth(self):
        base = world(Predicate('P', (Function('a'),)))
        changed = variant(base, functions={'f': {('a',): 'a', ('b',): 'a'}, 'a': {(): 'a'}})
        result = compare(base, changed)
        self.assertFalse(result.truth_changed)
        self.assertEqual(result.evidence_changes, ())

    def test_single_relation_membership_is_one_change(self):
        base = world(Predicate('P', (Variable('x'),)), {'x': 'b'})
        changed = variant(base, relations={'P': {('a',), ('b',)}, 'R': {('a', 'b')}})
        result = compare(base, changed)
        self.assertEqual(result.change.kind, 'relation')
        self.assertEqual((result.change.before, result.change.after), (False, True))
        self.assertTrue(result.truth_changed)

    def test_one_free_assignment_is_one_change(self):
        base = world(Predicate('P', (Variable('x'),)), {'x': 'a'})
        result = compare(base, variant(base, environment={'x': 'b'}))
        self.assertEqual(result.change.kind, 'assignment')
        self.assertEqual(result.change.symbol, 'x')
        self.assertTrue(result.truth_changed)

    def test_rejects_zero_changes_and_multiple_changes(self):
        base = world(Predicate('P', (Variable('x'),)), {'x': 'a'})
        with self.assertRaises(SemanticInputError):
            compare(base, base)
        changed = variant(base, relations={'P': {('a',), ('b',)}, 'R': {('a', 'b')}}, environment={'x': 'b'})
        with self.assertRaises(SemanticInputError):
            compare(base, changed)

    def test_changed_formula_domain_and_language_require_new_base(self):
        base = world(Predicate('P', (Function('a'),)))
        variants = [variant(base, formula=Binary('∧', base.formula, base.formula)),
                    variant(base, domain=('b', 'a'))]
        language = Language(functions=base.language.functions, predicates={'P': 1, 'R': 2, 'Q': 1})
        old = base.interpretation
        variants.append(prepare_input(language, Interpretation(old.domain, old.functions,
                        dict(old.relations, Q={('a',)})), base.formula))
        for changed in variants:
            with self.subTest(changed=changed), self.assertRaises(SemanticInputError):
                compare(base, changed)

    def test_witness_change_is_not_a_truth_change(self):
        original = world(Quantifier('∃', 'x', Predicate('P', (Variable('x'),))))
        base = variant(original, relations={'P': {('a',), ('b',)}, 'R': {('a', 'b')}})
        changed = variant(base, relations={'P': {('b',)}, 'R': {('a', 'b')}})
        result = compare(base, changed)
        self.assertFalse(result.truth_changed)
        self.assertEqual(result.before.trace.decisive_element, 'a')
        self.assertEqual(result.after.trace.decisive_element, 'b')
        self.assertTrue(any(c.before is None for c in result.evidence_changes))

    def test_bound_or_extra_assignments_cannot_be_compared_as_free(self):
        base = world(Quantifier('∃', 'x', Predicate('P', (Variable('x'),))), {'x': 'a'})
        with self.assertRaises(SemanticInputError):
            compare(base, variant(base, environment={'x': 'b'}))
        free = world(Predicate('P', (Variable('x'),)), {'x': 'a'})
        with self.assertRaises(SemanticInputError):
            compare(free, variant(free, environment={'x': 'a', 'unused': 'b'}))

    def test_invalid_variant_cannot_be_certified(self):
        base = world(Predicate('P', (Function('a'),)))
        for kwargs in [dict(relations={'P': set(), 'R': {('a', 'b')}}),
                       dict(functions={'f': {('a',): 'b'}, 'a': {(): 'a'}})]:
            with self.subTest(kwargs=kwargs), self.assertRaises(SemanticInputError):
                variant(base, **kwargs)


if __name__ == '__main__':
    unittest.main()
