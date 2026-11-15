import unittest
from dataclasses import FrozenInstanceError, replace

from lm_p3.models.ast import Binary, Function, Not, Predicate, Quantifier, Span, Variable
from lm_p3.models.errors import EvaluationLimitError, SemanticInputError
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import EvaluationLimits, ValidatedInput, prepare_input
from tests.semantics.test_evaluator import world


class NormalizedInputTests(unittest.TestCase):
    def test_invalid_interpretation_matrix(self):
        base = world(Predicate('P', (Function('a'),)))
        old = base.interpretation
        cases = [
            ('empty_domain', Interpretation((), old.functions, old.relations)),
            ('duplicate_domain', Interpretation(('a', 'a'), old.functions, old.relations)),
            ('bad_domain_element', Interpretation(('a', 2), old.functions, old.relations)),
            ('missing_function', Interpretation(old.domain, {}, old.relations)),
            ('unknown_relation', Interpretation(old.domain, old.functions, dict(old.relations, Q={('a',)}))),
            ('partial_function', Interpretation(old.domain, {'f': {('a',): 'a'}, 'a': {(): 'a'}}, old.relations)),
            ('empty_function', Interpretation(old.domain, {'f': {}, 'a': {(): 'a'}}, old.relations)),
            ('empty_relation', Interpretation(old.domain, old.functions, dict(old.relations, P=set()))),
            ('bad_tuple_arity', Interpretation(old.domain, old.functions, dict(old.relations, P={('a', 'b')}))),
            ('outside_domain', Interpretation(old.domain, old.functions, dict(old.relations, P={('c',)}))),
            ('invalid_output', Interpretation(old.domain, {'f': {('a',): 'c', ('b',): 'a'}, 'a': {(): 'a'}}, old.relations)),
        ]
        for name, interpretation in cases:
            with self.subTest(name=name), self.assertRaises(SemanticInputError):
                prepare_input(base.language, interpretation, base.formula)

    def test_invalid_ast_matrix(self):
        base = world(Predicate('P', (Function('a'),)))
        p = base.formula
        cases = [Variable('x'), Function('a'), None, {'kind': 'predicate'},
                 Predicate('P', (p,)), Predicate('P', (Function('unknown'),)),
                 Predicate('P', (Function('f'),)), Binary('?', p, p),
                 Quantifier('?', 'x', p), Quantifier('∀', '', p), Not(Variable('x')),
                 Predicate('P', (Variable(''),)),
                 Predicate('P', (Function('a'),), span=Span(-1, 1))]
        for formula in cases:
            with self.subTest(formula=formula), self.assertRaises(SemanticInputError):
                prepare_input(base.language, base.interpretation, formula)

    def test_invalid_language_arities_and_ambiguous_names(self):
        base = world(Predicate('P', (Function('a'),)))
        for arity in (-1, True, '1'):
            bad = Language(dict(base.language.functions, f=arity), base.language.predicates)
            with self.subTest(arity=arity), self.assertRaises(SemanticInputError):
                prepare_input(bad, base.interpretation, base.formula)
        with self.assertRaises(SemanticInputError):
            prepare_input(Language({'P': 0}, {'P': 1}), Interpretation(('a',), {'P': {(): 'a'}}, {'P': {('a',)}}), Predicate('P', (Function('P'),)))

    def test_missing_and_outside_assignments_including_extras(self):
        for environment in ({}, {'x': 'c'}, {'x': 'a', 'extra': 'c'}, {'x': []}):
            with self.subTest(environment=environment), self.assertRaises(SemanticInputError):
                world(Predicate('P', (Variable('x'),)), environment)

    def test_extra_valid_assignment_is_allowed_but_not_free(self):
        request = world(Predicate('P', (Function('a'),)), {'extra': 'b'})
        self.assertEqual(request.free_variables, frozenset())
        self.assertTrue(evaluate(request).value)

    def test_singleton_domain_and_zero_arity_symbols(self):
        language = Language({'c': 0, 'f': 2}, {'T': 0})
        interpretation = Interpretation(('only',), {'c': {(): 'only'}, 'f': {('only', 'only'): 'only'}}, {'T': {()}})
        self.assertTrue(evaluate(prepare_input(language, interpretation, Predicate('T'))).value)
        with self.assertRaises(SemanticInputError):
            prepare_input(language, Interpretation(('only',), {'c': {(): 'only'}, 'f': {}}, {'T': {()}}), Predicate('T'))

    def test_all_declared_symbols_are_checked_even_if_formula_does_not_use_them(self):
        base = world(Predicate('P', (Function('a'),)))
        functions = {'f': {('a',): 'a'}, 'a': {(): 'a'}}
        with self.assertRaises(SemanticInputError):
            prepare_input(base.language, Interpretation(('a', 'b'), functions, base.interpretation.relations), base.formula)

    def test_snapshots_do_not_follow_source_mutations_and_are_not_mutable(self):
        functions = {'f': {('a',): 'b', ('b',): 'a'}, 'a': {(): 'a'}}
        relations = {'P': {('a',)}}
        interpretation = Interpretation(('a', 'b'), functions, relations)
        request = prepare_input(Language({'f': 1, 'a': 0}, {'P': 1}), interpretation, Predicate('P', (Function('f', (Function('a'),)),)))
        functions['f'][('a',)] = 'a'
        relations['P'].add(('b',))
        self.assertFalse(evaluate(request).value)
        with self.assertRaises(TypeError):
            request.interpretation.functions['f'][('a',)] = 'a'
        with self.assertRaises(FrozenInstanceError):
            request.formula.name = 'Q'
        with self.assertRaises(TypeError):
            request.environment['x'] = 'a'

    def test_cannot_construct_validated_input_without_boundary(self):
        base = world(Predicate('P', (Function('a'),)))
        with self.assertRaises(TypeError):
            ValidatedInput(base.language, base.interpretation, base.formula, {}, base.limits, frozenset(), None)

    def test_dataclass_replace_cannot_bypass_certification(self):
        base = world(Predicate('P', (Function('a'),)))
        with self.assertRaises((TypeError, ValueError)):
            replace(base, formula=Predicate('Unknown'))

    def test_depth_and_input_size_limits_reject_before_evaluating(self):
        base = world(Predicate('P', (Function('a'),)))
        formula = base.formula
        for _ in range(150):
            formula = Not(formula)
        with self.assertRaises(EvaluationLimitError):
            prepare_input(base.language, base.interpretation, formula)
        with self.assertRaises(EvaluationLimitError):
            prepare_input(base.language, base.interpretation, base.formula, limits=EvaluationLimits(max_input_nodes=1))

    def test_bad_limits_are_rejected(self):
        for kwargs in ({'max_steps': 0}, {'max_depth': 129}, {'max_input_nodes': True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                EvaluationLimits(**kwargs)
        base = world(Predicate('P', (Function('a'),)))
        with self.assertRaises(TypeError):
            prepare_input(base.language, base.interpretation, base.formula, limits=False)


if __name__ == '__main__':
    unittest.main()
