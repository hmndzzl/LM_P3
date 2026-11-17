# Contrato del motor publicado como recurso estático, sin un servidor Python remoto.
import json
import unittest
from copy import deepcopy

from lm_p3.server.browser import execute
from tests.server.test_codec import sample_request


class BrowserBridgeTests(unittest.TestCase):
    def test_same_evaluation_and_revision_as_local_codec(self):
        result = json.loads(execute('evaluate', json.dumps(sample_request())))
        self.assertEqual(result['status'], 'evaluated')
        self.assertFalse(result['evaluation']['value'])
        self.assertEqual(result['revision'], 3)

    def test_true_quantifier_and_exhaustive_false_are_real_computations(self):
        data = sample_request()
        for formula, expected in [('∃x P(x)', True), ('∃x (P(x) ∧ ¬P(x))', False)]:
            data['formula'] = formula
            result = json.loads(execute('evaluate', json.dumps(data)))
            self.assertEqual(result['evaluation']['value'], expected)
            if not expected:
                self.assertTrue(result['evaluation']['trace']['complete'])

    def test_analyze_and_compare_use_the_same_contract(self):
        data = sample_request()
        analysis = {k: data[k] for k in ('revision', 'functions', 'predicates', 'formula')}
        self.assertEqual(json.loads(execute('analyze', json.dumps(analysis)))['free_variables'], ['x'])
        variant = deepcopy(data)
        variant['assignments'] = [['x', 'b']]
        result = json.loads(execute('compare', json.dumps({'revision': 4, 'base': data, 'variant': variant})))
        self.assertTrue(result['comparison']['truth_changed'])

    def test_invalid_requests_never_receive_truth(self):
        for operation, payload in [('unknown', '{}'), ('evaluate', '{'),
                                   ('evaluate', '{"revision":3,"revision":4}')]:
            result = json.loads(execute(operation, payload))
            self.assertEqual(result['status'], 'invalid')
            self.assertNotIn('evaluation', result)
            self.assertTrue(result['errors'])

    def test_request_size_limit_does_not_become_false(self):
        result = json.loads(execute('evaluate', ' ' * (256 * 1024 + 1)))
        self.assertEqual(result['status'], 'not_evaluated')
        self.assertNotIn('evaluation', result)


if __name__ == '__main__':
    unittest.main()
