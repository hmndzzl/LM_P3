from http.client import HTTPConnection
import json
import threading
import unittest
from unittest.mock import patch

from lm_p3.models.errors import EvaluationLimitError
from lm_p3.server.http import MAX_BODY, make_server
from tests.server.test_codec import sample_request


class LocalHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path='/api/evaluate', *, body=None, headers=None, method='POST'):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        defaults = {'Content-Type': 'application/json',
                    'Origin': f'http://127.0.0.1:{self.server.server_port}'}
        defaults.update(headers or {})
        payload = json.dumps(sample_request()) if body is None else body
        try:
            connection.request(method, path, body=payload if method == 'POST' else None, headers=defaults)
            response = connection.getresponse()
            raw = response.read()
            content = json.loads(raw) if 'application/json' in response.getheader('Content-Type', '') else raw
            return response.status, content, dict(response.getheaders())
        finally:
            connection.close()

    def test_real_false_and_true_are_both_successful_http_responses(self):
        for formula, expected in [('P(f(x))', False), ('∃x P(x)', True)]:
            data = sample_request()
            data['formula'] = formula
            status, result, headers = self.request(body=json.dumps(data))
            self.assertEqual(status, 200)
            self.assertIs(result['evaluation']['value'], expected)
            self.assertEqual(result['revision'], 3)
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            self.assertIn("default-src 'self'", headers['Content-Security-Policy'])

    def test_analysis_is_available_before_assigning_variables(self):
        data = {'revision': 1, 'functions': [], 'predicates': [['P', 1]], 'formula': 'P(y)'}
        status, result, _ = self.request('/api/analyze', body=json.dumps(data))
        self.assertEqual(status, 200)
        self.assertEqual(result['free_variables'], ['y'])

    def test_frontend_assets_are_served_without_exposing_project_files(self):
        for path, expected_type in [('/', 'text/html'), ('/css/tokens.css', 'text/css'),
                                    ('/css/styles.css', 'text/css'), ('/js/app.js', 'text/javascript'),
                                    ('/js/api.js', 'text/javascript'), ('/js/editors.js', 'text/javascript'),
                                    ('/js/errors.js', 'text/javascript'), ('/js/evidence.js', 'text/javascript')]:
            with self.subTest(path=path):
                status, body, headers = self.request(path, method='GET')
                self.assertEqual(status, 200)
                self.assertTrue(headers['Content-Type'].startswith(expected_type))
                self.assertGreater(len(body), 0)

    def test_invalid_data_never_calls_engine(self):
        data = sample_request()
        data['relations']['P'] = []
        with patch('lm_p3.application.service.evaluate') as engine:
            status, result, _ = self.request(body=json.dumps(data))
        self.assertEqual(status, 400)
        self.assertEqual(result['revision'], 3)
        self.assertNotIn('evaluation', result)
        engine.assert_not_called()

    def test_host_origin_and_static_paths_are_restricted(self):
        for headers in ({'Host': 'example.com'}, {'Origin': 'https://example.com'}, {'Origin': ''}):
            with self.subTest(headers=headers):
                self.assertEqual(self.request(headers=headers)[0], 403)
        for path in ('/README.md', '/bases/README.md', '/../README.md', '/.git/config', '/unknown'):
            with self.subTest(path=path):
                self.assertEqual(self.request(path, method='GET')[0], 404)

    def test_malformed_duplicate_and_oversized_json_are_rejected(self):
        self.assertEqual(self.request(body='{')[0], 400)
        self.assertEqual(self.request(body='{"x":1,"x":2}')[0], 400)
        self.assertEqual(self.request(headers={'Content-Length': str(MAX_BODY + 1)})[0], 413)
        self.assertEqual(self.request(headers={'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('/api/unknown')[0], 404)

    def test_limits_and_unexpected_failures_have_no_truth_or_traceback(self):
        with patch('lm_p3.server.http.process_request', side_effect=EvaluationLimitError('Límite alcanzado.')):
            status, result, _ = self.request()
        self.assertEqual(status, 422)
        self.assertNotIn('evaluation', result)
        with patch('lm_p3.server.http.process_request', side_effect=RuntimeError('detalle privado')):
            with self.assertLogs(level='ERROR'):
                status, result, _ = self.request()
        self.assertEqual(status, 500)
        self.assertNotIn('detalle privado', json.dumps(result))
