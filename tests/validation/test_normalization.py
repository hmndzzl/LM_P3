from copy import deepcopy
from dataclasses import FrozenInstanceError
import unittest

from lm_p3.models.errors import EvaluationLimitError, InputValidationError, SemanticInputError
from lm_p3.models.language import Language
from lm_p3.validation.normalization import build_environment, build_interpretation, build_language


class NormalizationTests(unittest.TestCase):
    def setUp(self):
        self.language = Language({'f': 1}, {'P': 1})
        self.data = {'domain': ['a', 'b'],
                     'function_rows': {'f': [[['a'], 'b'], [['b'], 'a']]},
                     'relations': {'P': [['a']]}}

    def build(self, **changes):
        data = deepcopy(self.data)
        data.update(changes)
        return build_interpretation(self.language, **data)

    def assertInvalid(self, callback, code, field=None):
        with self.assertRaises(InputValidationError) as caught:
            callback()
        error = caught.exception
        self.assertIsInstance(error, SemanticInputError)
        self.assertIn(code, [issue.code for issue in error.errors])
        if field is not None:
            self.assertTrue(any(issue.code == code and issue.field == field for issue in error.errors))
        self.assertFalse(hasattr(error, 'value'))
        self.assertTrue(all(not hasattr(issue, 'value') for issue in error.errors))
        return error

    def test_language_is_built_from_rows_with_custom_names(self):
        language = build_language([['sucesor', 1], ['inicio', 0]], [['Pertenece', 2]])
        self.assertEqual(dict(language.functions), {'sucesor': 1, 'inicio': 0})
        self.assertEqual(dict(language.predicates), {'Pertenece': 2})

    def test_duplicate_declarations_are_not_overwritten_even_if_identical(self):
        for arity in (1, 2):
            with self.subTest(arity=arity):
                self.assertInvalid(lambda: build_language([['f', 1], ['f', arity]], [['P', 1]]),
                                   'duplicate_declaration', 'language.functions[1]')
        self.assertInvalid(lambda: build_language([['P', 1]], [['P', 1]]), 'ambiguous_symbol')

    def test_declaration_shapes_names_and_arities(self):
        cases = [(None, 'invalid_structure'), ({'f': 1}, 'invalid_structure'),
                 (['f'], 'invalid_declaration'), ([['f']], 'invalid_declaration'),
                 ([[[], 1]], 'invalid_name'), ([['bad name', 1]], 'invalid_name'),
                 ([['f', True]], 'invalid_arity'), ([['f', -1]], 'invalid_arity'),
                 ([['f', '1']], 'invalid_arity')]
        for rows, code in cases:
            with self.subTest(rows=rows):
                self.assertInvalid(lambda: build_language(rows, []), code)

    def test_valid_interpretation_preserves_domain_order_and_copies_sources(self):
        original = deepcopy(self.data)
        result = self.build()
        self.assertEqual(result.domain, ('a', 'b'))
        self.assertEqual(result.functions['f'][('a',)], 'b')
        self.assertEqual(self.data, original)
        data = deepcopy(self.data)
        result = build_interpretation(self.language, **data)
        data['function_rows']['f'][0][1] = 'a'
        data['relations']['P'].append(['b'])
        self.assertEqual(result.functions['f'][('a',)], 'b')
        self.assertEqual(result.relations['P'], {('a',)})

    def test_domain_errors_do_not_leak_type_errors(self):
        cases = [(None, 'invalid_structure'), ('ab', 'invalid_structure'),
                 ({'a', 'b'}, 'invalid_structure'), ([], 'invalid_domain'),
                 (['a', 'a'], 'duplicate_domain'), (['a', []], 'invalid_domain'),
                 (['a', 1], 'invalid_domain'), (['a', '  '], 'invalid_domain')]
        for domain, code in cases:
            with self.subTest(domain=domain):
                self.assertInvalid(lambda: self.build(domain=domain), code)

    def test_missing_and_extra_tables_are_localized(self):
        self.assertInvalid(lambda: self.build(function_rows={}), 'missing_interpretation', 'functions.f')
        self.assertInvalid(lambda: self.build(relations={}), 'missing_interpretation', 'relations.P')
        self.assertInvalid(lambda: self.build(relations={'P': [['a']], 'Q': [['b']]}),
                           'unknown_symbol', 'relations.Q')
        self.assertInvalid(lambda: self.build(function_rows=[]), 'invalid_structure', 'functions')
        self.assertInvalid(lambda: self.build(relations=[]), 'invalid_structure', 'relations')

    def test_function_row_shapes_tuple_arity_and_domain_membership(self):
        cases = [(None, 'invalid_structure'), ({('a',): 'b'}, 'invalid_structure'),
                 ([], 'empty_interpretation'), ([['a']], 'invalid_function_row'),
                 ([[[], 'a']], 'invalid_tuple_arity'), ([[['a', 'b'], 'a']], 'invalid_tuple_arity'),
                 ([[['c'], 'a']], 'outside_domain'), ([[['a'], 'c']], 'outside_domain'),
                 ([[[[]], 'a']], 'outside_domain'), ([[['a'], []]], 'outside_domain'),
                 ([['a', 'b']], 'invalid_structure')]
        for rows, code in cases:
            with self.subTest(rows=rows):
                self.assertInvalid(lambda: self.build(function_rows={'f': rows}), code)

    def test_function_totality_reports_a_missing_tuple_without_building_cartesian_table(self):
        error = self.assertInvalid(lambda: self.build(function_rows={'f': [[['a'], 'b']]}),
                                   'partial_function', 'functions.f')
        issue = next(issue for issue in error.errors if issue.code == 'partial_function')
        self.assertEqual(issue.details['missing_tuple'], "('b',)")
        self.assertIn('f(b)', issue.message)

    def test_conflicting_function_rows_are_rejected_in_either_order(self):
        for first, second in [('a', 'b'), ('b', 'a')]:
            with self.subTest(first=first):
                rows = [[['a'], first], [['a'], second], [['b'], 'a']]
                self.assertInvalid(lambda: self.build(function_rows={'f': rows}),
                                   'conflicting_function_row', 'functions.f[1].output')

    def test_identical_rows_do_not_fill_a_missing_function_input(self):
        incomplete = [[['a'], 'b'], [['a'], 'b']]
        self.assertInvalid(lambda: self.build(function_rows={'f': incomplete}), 'partial_function')
        complete = self.data['function_rows']['f'] + [[['a'], 'b']]
        self.assertEqual(len(self.build(function_rows={'f': complete}).functions['f']), 2)

    def test_nonempty_relations_have_valid_tuples_and_redundant_rows_are_sets(self):
        cases = [(None, 'invalid_structure'), ({('a',)}, 'invalid_structure'),
                 ([], 'empty_interpretation'), ([[]], 'invalid_tuple_arity'),
                 ([['a', 'b']], 'invalid_tuple_arity'), ([['c']], 'outside_domain'),
                 ([['a', []]], 'outside_domain'), (['a'], 'invalid_structure')]
        for rows, code in cases:
            with self.subTest(rows=rows):
                self.assertInvalid(lambda: self.build(relations={'P': rows}), code)
        self.assertEqual(self.build(relations={'P': [['a'], ['a']]}).relations['P'], {('a',)})

    def test_zero_arity_functions_and_relations(self):
        language = build_language([['c', 0]], [['T', 0]])
        result = build_interpretation(language, ['only'], {'c': [[[], 'only']]}, {'T': [[]]})
        self.assertEqual(result.functions['c'][()], 'only')
        self.assertEqual(result.relations['T'], {()})
        self.assertInvalid(lambda: build_interpretation(language, ['only'], {'c': []}, {'T': [[]]}),
                           'empty_interpretation', 'functions.c')
        self.assertInvalid(lambda: build_interpretation(language, ['only'], {'c': [[[], 'only']]}, {'T': []}),
                           'empty_interpretation', 'relations.T')

    def test_binary_total_function_requires_four_unique_rows(self):
        language = Language({'g': 2}, {})
        rows = [[['a', 'a'], 'a'], [['a', 'b'], 'a'], [['b', 'a'], 'b'], [['b', 'b'], 'b']]
        result = build_interpretation(language, ['a', 'b'], {'g': rows}, {})
        self.assertEqual(len(result.functions['g']), 4)
        self.assertInvalid(lambda: build_interpretation(language, ['a', 'b'], {'g': rows[:-1]}, {}),
                           'partial_function')

    def test_all_sixteen_binary_table_subsets_are_total_only_when_complete(self):
        language = Language({'g': 2}, {})
        rows = [[['a', 'a'], 'a'], [['a', 'b'], 'a'], [['b', 'a'], 'b'], [['b', 'b'], 'b']]
        for mask in range(16):
            subset = [row for index, row in enumerate(rows) if mask & (1 << index)]
            with self.subTest(mask=mask):
                if mask == 15:
                    self.assertEqual(len(build_interpretation(language, ['a', 'b'], {'g': subset}, {}).functions['g']), 4)
                else:
                    self.assertInvalid(lambda: build_interpretation(language, ['a', 'b'], {'g': subset}, {}),
                                       'empty_interpretation' if mask == 0 else 'partial_function')

    def test_very_large_declared_arity_is_rejected_without_constructing_d_to_n(self):
        language = Language({'g': 10**12}, {})
        self.assertInvalid(lambda: build_interpretation(language, ['a', 'b'], {'g': [[['a'], 'a']]}, {}),
                           'invalid_tuple_arity')

    def test_fresh_request_after_validation_failure_is_unaffected(self):
        self.assertInvalid(lambda: self.build(relations={'P': []}), 'empty_interpretation')
        self.assertEqual(self.build().domain, ('a', 'b'))

    def test_opaque_domain_elements_are_not_trimmed_or_converted(self):
        language = Language({}, {'P': 1})
        result = build_interpretation(language, [' elemento ', 'otro valor'], {}, {'P': [[' elemento ']]})
        self.assertEqual(result.domain, (' elemento ', 'otro valor'))

    def test_environment_rows_preserve_extras_and_catch_conflicting_duplicates(self):
        result = build_environment(self.language, ['a', 'b'], [['x', 'a'], ['extra', 'b'], ['x', 'a']])
        self.assertEqual(result, {'x': 'a', 'extra': 'b'})
        self.assertInvalid(lambda: build_environment(self.language, ['a', 'b'], [['x', 'a'], ['x', 'b']]),
                           'conflicting_assignment', 'environment[1]')

    def test_environment_shapes_names_and_values(self):
        cases = [(None, 'invalid_structure'), ({'x': 'a'}, 'invalid_structure'),
                 (['x'], 'invalid_assignment'), ([['x']], 'invalid_assignment'),
                 ([[[], 'a']], 'invalid_variable'), ([['bad name', 'a']], 'invalid_variable'),
                 ([['f', 'a']], 'invalid_variable'), ([['P', 'a']], 'invalid_variable'),
                 ([['x', []]], 'invalid_assignment'), ([['x', 'c']], 'invalid_assignment')]
        for assignments, code in cases:
            with self.subTest(assignments=assignments):
                self.assertInvalid(lambda: build_environment(self.language, ['a', 'b'], assignments), code)

    def test_multiple_independent_errors_are_returned_together(self):
        error = self.assertInvalid(lambda: self.build(function_rows={'f': []}, relations={'P': []}),
                                   'empty_interpretation')
        self.assertEqual({issue.field for issue in error.errors}, {'functions.f', 'relations.P'})
        self.assertEqual(error.code, error.errors[0].code)
        self.assertEqual(error.field, error.errors[0].field)
        with self.assertRaises(FrozenInstanceError):
            error.errors[0].code = 'hidden'
        with self.assertRaises(TypeError):
            error.errors[0].details['hidden'] = 'value'

    def test_external_collection_budget_fails_without_truth(self):
        with self.assertRaises(EvaluationLimitError) as caught:
            self.build(domain=['a'] * 20_001)
        self.assertFalse(hasattr(caught.exception, 'value'))

    def test_invalid_language_fails_before_building_interpretation_or_environment(self):
        self.assertInvalid(lambda: build_interpretation(None, ['a'], {}, {}), 'invalid_structure')
        self.assertInvalid(lambda: build_environment(Language({'f': True}, {}), ['a'], []), 'invalid_arity')


if __name__ == '__main__':
    unittest.main()
