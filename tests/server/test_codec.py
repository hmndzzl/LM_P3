from copy import deepcopy
import json
import unittest

from lm_p3.models.errors import SemanticInputError
from lm_p3.server.codec import decode_request, error_response, process_request


def sample_request():
    return {'revision': 3, 'functions': [['f', 1]], 'predicates': [['P', 1]],
            'domain': ['a', 'b'], 'function_rows': {'f': [[['a'], 'b'], [['b'], 'a']]},
            'relations': {'P': [['a']]}, 'assignments': [['x', 'a']], 'formula': 'P(f(x))'}


class CodecTests(unittest.TestCase):
    def test_real_evaluation_and_serializable_evidence_preserve_input(self):
        data = sample_request()
        original = deepcopy(data)
        result = process_request('evaluate', decode_request(json.dumps(data).encode()))
        self.assertIs(result['evaluation']['value'], False)
        self.assertEqual(result['revision'], 3)
        self.assertEqual(result['evaluation']['trace']['terms'][0]['value'], 'b')
        json.dumps(result)
        self.assertEqual(data, original)

    def test_analysis_needs_neither_interpretation_nor_environment(self):
        data = {'revision': 4, 'functions': [], 'predicates': [['P', 1]],
                'formula': '∀x P(x) ∧ P(𝑦)'}
        result = process_request('analyze', data)
        self.assertEqual(result['free_variables'], ['𝑦'])
        self.assertNotIn('evaluation', result)

    def test_json_rejects_duplicate_keys_invalid_encoding_and_non_objects(self):
        for body in (b'{"revision":1,"revision":2}', b'{"a":{"x":1,"x":2}}',
                     b'[]', b'null', b'\xff', b'{', b'{"a":NaN}'):
            with self.subTest(body=body), self.assertRaises(SemanticInputError):
                decode_request(body)

    def test_missing_extra_fields_and_bad_types_are_rejected(self):
        for patch in ({'revision': True}, {'revision': -1}, {'formula': 12}, {'ast': {}},
                      {'functions': {'f': 1}}):
            data = sample_request()
            data.update(patch)
            with self.subTest(patch=patch), self.assertRaises(SemanticInputError):
                process_request('evaluate', data)
        data = sample_request()
        del data['assignments']
        with self.assertRaises(SemanticInputError):
            process_request('evaluate', data)

    def test_conflicts_survive_transport_and_errors_have_no_truth(self):
        data = sample_request()
        data['function_rows']['f'].append([['a'], 'a'])
        with self.assertRaises(SemanticInputError) as caught:
            process_request('evaluate', decode_request(json.dumps(data).encode()))
        result = error_response(caught.exception, 3)
        self.assertEqual(result['errors'][0]['code'], 'conflicting_function_row')
        self.assertNotIn('evaluation', result)
        self.assertNotIn('value', result)
        json.dumps(result)

    def test_syntax_errors_preserve_original_unicode_span(self):
        data = sample_request()
        data['formula'] = 'P(𝑥) ∧ P(x,y)'
        with self.assertRaises(SemanticInputError) as caught:
            process_request('evaluate', data)
        issue = error_response(caught.exception)['errors'][0]
        self.assertEqual(issue['code'], 'arity_mismatch')
        self.assertEqual(issue['span'], {'start': 7, 'end': 13})
        self.assertEqual(issue['details']['actual'], 2)
