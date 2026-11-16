from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from lm_p3.application.service import evaluate_formula
from lm_p3.models.errors import EvaluationLimitError, InputValidationError, SemanticInputError
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import EvaluationLimits, prepare_input
from lm_p3.syntax.parser import parse
from lm_p3.validation.normalization import build_environment, build_interpretation, build_language
from lm_p3.validation.validator import validate_input


def evaluate_rows(data, **kwargs):
    language = build_language(data['functions'], data['predicates'])
    interpretation = build_interpretation(language, data['domain'], data['function_rows'], data['relations'])
    environment = build_environment(language, data['domain'], data['assignments'])
    return evaluate_formula(data['text'], language, interpretation, environment, parse=parse, **kwargs)


class ExternalValidationIntegrationTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'fixtures' / 'validation_cases.json'
        self.fixture = json.loads(path.read_text(encoding='utf-8'))

    def test_r7_fixture_matrix_blocks_the_real_engine_on_every_invalid_input(self):
        self.assertEqual(self.fixture['version'], 1)
        for case in self.fixture['cases']:
            with self.subTest(name=case['name']), patch('lm_p3.application.service.evaluate', wraps=evaluate) as engine:
                data = deepcopy(self.fixture['base'])
                data.update(case['overrides'])
                original = deepcopy(data)
                if 'value' in case:
                    result = evaluate_rows(data)
                    self.assertIs(result.evaluation.value, case['value'])
                    self.assertEqual(engine.call_count, 1)
                else:
                    with self.assertRaises(SemanticInputError) as caught:
                        evaluate_rows(data)
                    error = caught.exception
                    self.assertEqual((error.code, error.field), (case['code'], case['field']))
                    self.assertFalse(hasattr(error, 'value'))
                    self.assertFalse(hasattr(error, 'evaluation'))
                    engine.assert_not_called()
                self.assertEqual(data, original)

    def test_service_uses_m2_validator_and_preserves_revision_and_custom_limits(self):
        with patch('lm_p3.validation.validator.prepare_input', wraps=prepare_input) as certify:
            result = evaluate_rows(self.fixture['base'], revision=11, limits=EvaluationLimits(max_steps=8))
            self.assertEqual(result.revision, 11)
            self.assertFalse(result.evaluation.value)
            self.assertEqual(certify.call_count, 1)
            self.assertEqual(certify.call_args.kwargs['limits'], EvaluationLimits(max_steps=8))

    def test_explicit_validator_injection_and_evaluation_limits_still_work(self):
        result = evaluate_rows(self.fixture['base'], validate=validate_input)
        self.assertFalse(result.evaluation.value)
        with self.assertRaises(EvaluationLimitError) as caught:
            evaluate_rows(self.fixture['base'], limits=EvaluationLimits(max_steps=1))
        self.assertFalse(hasattr(caught.exception, 'value'))

    def test_redundant_rows_remain_valid_but_conflicting_rows_never_get_overwritten(self):
        data = deepcopy(self.fixture['base'])
        data['function_rows']['f'].append([['a'], 'b'])
        data['relations']['P'].append(['a'])
        data['assignments'].append(['x', 'a'])
        self.assertFalse(evaluate_rows(data).evaluation.value)
        data['function_rows']['f'][-1][1] = 'a'
        with self.assertRaises(InputValidationError) as caught:
            evaluate_rows(data)
        self.assertEqual(caught.exception.code, 'conflicting_function_row')


if __name__ == '__main__':
    unittest.main()
