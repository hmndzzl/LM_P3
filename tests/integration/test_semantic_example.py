# Se verifica el ejemplo real sin importar código de las bases heredadas.
import json
import unittest

from examples.semantica import demonstration


class SemanticExampleTests(unittest.TestCase):
    def test_example_is_serializable_and_has_four_required_outcomes(self):
        data = json.loads(json.dumps(demonstration(), ensure_ascii=False))
        self.assertEqual([r['value'] for r in data['evaluations']], [True, False, True, False])
        self.assertEqual(data['evaluations'][0]['trace']['unvisited_elements'], ['b'])
        self.assertTrue(data['comparison']['truth_changed'])
        self.assertFalse(data['comparison']['before']['value'])
        self.assertTrue(data['comparison']['after']['value'])


if __name__ == '__main__':
    unittest.main()
