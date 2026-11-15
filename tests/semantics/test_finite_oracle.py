# Se contrastan fórmulas con operaciones de conjuntos, sin recorrer el AST esperado.
import unittest
from itertools import combinations, product

from lm_p3.models.ast import Binary, Function, Not, Predicate, Quantifier, Variable
from lm_p3.models.language import Interpretation, Language
from lm_p3.semantics.evaluator import evaluate
from lm_p3.semantics.inputs import prepare_input


def nonempty_subsets(values):
    for size in range(1, len(values) + 1):
        yield from (frozenset(items) for items in combinations(values, size))


class FiniteOracleTests(unittest.TestCase):
    def test_900_results_against_finite_set_definitions(self):
        domain = ('a', 'b')
        x, y = Variable('x'), Variable('y')
        p = Predicate('P', (x,))
        r = Predicate('R', (x, y))
        formulas = [Quantifier('∀', 'x', Quantifier('∃', 'y', r)),
                    Quantifier('∃', 'x', Quantifier('∀', 'y', r)),
                    Quantifier('∀', 'x', Binary('→', Predicate('P', (Function('f', (x,)),)), p)),
                    Binary('↔', Not(Quantifier('∀', 'x', p)), Quantifier('∃', 'x', Not(p))),
                    Quantifier('∀', 'x', Binary('∨', p, Not(p)))]
        results_checked = 0
        for unary in nonempty_subsets([(a,) for a in domain]):
            for binary in nonempty_subsets(list(product(domain, repeat=2))):
                for outputs in product(domain, repeat=2):
                    table = {(a,): b for a, b in zip(domain, outputs)}
                    interpretation = Interpretation(domain, {'f': table}, {'P': unary, 'R': binary})
                    language = Language({'f': 1}, {'P': 1, 'R': 2})
                    # Las expectativas usan directamente las definiciones finitas de ∀ y ∃.
                    expected = [all(any((a, b) in binary for b in domain) for a in domain),
                                any(all((a, b) in binary for b in domain) for a in domain),
                                all((table[(a,)],) not in unary or (a,) in unary for a in domain),
                                True, True]
                    for formula, value in zip(formulas, expected):
                        with self.subTest(unary=unary, binary=binary, outputs=outputs, formula=formula):
                            self.assertEqual(evaluate(prepare_input(language, interpretation, formula)).value, value)
                            results_checked += 1
        self.assertEqual(results_checked, 900)


if __name__ == '__main__':
    unittest.main()
