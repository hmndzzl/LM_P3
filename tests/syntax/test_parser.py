from dataclasses import asdict
import unittest

from lm_p3.models.ast import Binary, Function, Not, Predicate, Quantifier, Span, Variable
from lm_p3.models.errors import EvaluationLimitError, FormulaSyntaxError, SemanticInputError
from lm_p3.models.language import Language
from lm_p3.syntax.lexer import tokenize
from lm_p3.syntax.parser import analyze, parse


def without_spans(node):
    def clean(value):
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items() if key != 'span'}
        if isinstance(value, (tuple, list)):
            return tuple(clean(item) for item in value)
        return value
    return clean(asdict(node))


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.language = Language({'f': 1, 'g': 2, 'c': 0}, {'P': 1, 'Q': 1, 'R': 2, 'T': 0})
        self.p = Predicate('P', (Variable('x'),))
        self.q = Predicate('Q', (Variable('x'),))
        self.r = Predicate('R', (Variable('x'), Variable('y')))

    def assertFormula(self, text, expected, language=None):
        result = parse(text, language or self.language)
        self.assertEqual(without_spans(expected), without_spans(result))
        return result

    def test_atomic_ast_and_exact_original_positions(self):
        self.assertEqual(parse(' P(f(x)) ', self.language),
                         Predicate('P', (Function('f', (Variable('x', Span(5, 6)),), Span(3, 7)),),
                                   Span(1, 8)))

    def test_nested_functions_and_multiple_arguments(self):
        self.assertFormula('R(g(f(x),y),f(c))', Predicate('R', (
            Function('g', (Function('f', (Variable('x'),)), Variable('y'))),
            Function('f', (Function('c'),)),
        )))

    def test_user_names_unicode_and_unknown_identifiers_are_variables(self):
        language = Language({'siguiente': 1}, {'Conoce': 2, 'Está_listo': 1})
        self.assertFormula('Conoce(siguiente(alguien),𝑥)', Predicate('Conoce', (
            Function('siguiente', (Variable('alguien'),)), Variable('𝑥'))), language)
        self.assertFormula('Está_listo(niño)', Predicate('Está_listo', (Variable('niño'),)), language)

    def test_zero_arity_with_and_without_parentheses(self):
        for text in ('T', 'T()'):
            with self.subTest(text=text):
                self.assertFormula(text, Predicate('T'))
        for text in ('P(c)', 'P(c())'):
            with self.subTest(text=text):
                self.assertFormula(text, Predicate('P', (Function('c'),)))

    def test_every_canonical_connective_has_a_manual_expected_ast(self):
        self.assertFormula('¬P(x)', Not(self.p))
        for operator in ('∧', '∨', '→', '↔'):
            with self.subTest(operator=operator):
                self.assertFormula(f'P(x) {operator} Q(x)', Binary(operator, self.p, self.q))
        for operator in ('∀', '∃'):
            with self.subTest(operator=operator):
                self.assertFormula(f'{operator}x P(x)', Quantifier(operator, 'x', self.p))

    def test_every_keyboard_alias_uses_canonical_ast_operators(self):
        cases = [('~P(x)', Not(self.p)), ('P(x)&Q(x)', Binary('∧', self.p, self.q)),
                 ('P(x)|Q(x)', Binary('∨', self.p, self.q)),
                 ('P(x) v Q(x)', Binary('∨', self.p, self.q)),
                 ('P(x)->Q(x)', Binary('→', self.p, self.q)),
                 ('P(x)<->Q(x)', Binary('↔', self.p, self.q)),
                 ('Ax P(x)', Quantifier('∀', 'x', self.p)),
                 ('Ex(P(x))', Quantifier('∃', 'x', self.p))]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertFormula(text, expected)

    def test_precedence_all_levels_and_prefixes(self):
        self.assertFormula('¬P(x) ∧ Q(x) ∨ T → P(y) ↔ T',
                           Binary('↔', Binary('→', Binary('∨',
                               Binary('∧', Not(self.p), self.q), Predicate('T')),
                               Predicate('P', (Variable('y'),))), Predicate('T')))
        self.assertFormula('¬∀x ∃y R(x,y)', Not(Quantifier('∀', 'x',
                           Quantifier('∃', 'y', self.r))))

    def test_implication_right_and_other_binary_operators_left(self):
        self.assertFormula('P(x) → Q(x) → T',
                           Binary('→', self.p, Binary('→', self.q, Predicate('T'))))
        for operator in ('∧', '∨', '↔'):
            with self.subTest(operator=operator):
                self.assertFormula(f'P(x) {operator} Q(x) {operator} T',
                                   Binary(operator, Binary(operator, self.p, self.q), Predicate('T')))

    def test_parentheses_override_associativity_and_precedence(self):
        self.assertFormula('(P(x) → Q(x)) → T',
                           Binary('→', Binary('→', self.p, self.q), Predicate('T')))
        self.assertFormula('P(x) ∧ (Q(x) ∨ T)',
                           Binary('∧', self.p, Binary('∨', self.q, Predicate('T'))))

    def test_minimum_quantifier_scope_is_same_for_aliases(self):
        expected = Binary('∧', Quantifier('∀', 'x', self.p), self.q)
        for text in ('∀x P(x) ∧ Q(x)', 'Ax P(x) & Q(x)'):
            with self.subTest(text=text):
                self.assertFormula(text, expected)
                self.assertEqual(analyze(text, self.language).free_variables, {'x'})
        self.assertFormula('∀x (P(x) ∧ Q(x))', Quantifier('∀', 'x', Binary('∧', self.p, self.q)))
        self.assertEqual(analyze('∀x (P(x) ∧ Q(x))', self.language).free_variables, set())

    def test_nested_shadowing_and_free_occurrence_outside_quantifier(self):
        result = analyze('(∀x (P(x) ∨ ∃x R(x,y))) ∧ P(x)', self.language)
        self.assertEqual(result.free_variables, {'x', 'y'})
        self.assertEqual(result.formula.left.body.right.variable, 'x')
        self.assertEqual(analyze('Ax Ey R(x,y)', self.language).free_variables, set())

    def test_v_can_be_a_variable_and_alias_only_in_infix_position(self):
        self.assertFormula('∀v P(v) v Q(v)', Binary('∨',
            Quantifier('∀', 'v', Predicate('P', (Variable('v'),))), Predicate('Q', (Variable('v'),))))
        self.assertFormula('P(Ax)', Predicate('P', (Variable('Ax'),)))

    def test_declared_names_take_priority_over_compact_aliases(self):
        language = Language({}, {'Ax': 1, 'Ex': 1, 'v': 1, 'P': 1})
        for name in ('Ax', 'Ex', 'v'):
            with self.subTest(name=name):
                self.assertFormula(f'{name}(x)', Predicate(name, (Variable('x'),)), language)
        self.assertFormula('∀x Ax(x)', Quantifier('∀', 'x', Predicate('Ax', (Variable('x'),))), language)
        with self.assertRaises(FormulaSyntaxError):
            parse('P(x) v P(x)', language)

    def test_quantifier_alias_preserves_long_variable_name_and_positions(self):
        result = parse('Apersona P(persona)', self.language)
        self.assertEqual(result.variable, 'persona')
        self.assertEqual(result.span, Span(0, 19))
        self.assertEqual(result.body.span, Span(9, 19))
        self.assertEqual(result.body.arguments[0].span, Span(11, 18))

    def test_predicate_cannot_be_term_or_function_used_as_formula(self):
        for text, code in [('P(Q(x))', 'predicate_as_term'), ('f(x)', 'expected_predicate'),
                           ('P(desconocida(x))', 'unknown_symbol'), ('Desconocido(x)', 'unknown_symbol')]:
            with self.subTest(text=text), self.assertRaises(FormulaSyntaxError) as caught:
                parse(text, self.language)
            self.assertEqual(caught.exception.code, code)

    def test_arity_error_contains_code_span_and_parameters(self):
        for text, name, expected, actual in [('P(x,y)', 'P', 1, 2), ('P(f())', 'f', 1, 0),
                                             ('P', 'P', 1, 0), ('T(x)', 'T', 0, 1)]:
            with self.subTest(text=text), self.assertRaises(FormulaSyntaxError) as caught:
                parse(text, self.language)
            error = caught.exception
            self.assertEqual(error.code, 'arity_mismatch')
            self.assertEqual(error.field, 'formula')
            self.assertEqual(dict(error.details), {'symbol': name, 'expected': expected, 'actual': actual})
            self.assertGreater(error.span.end, error.span.start)
            self.assertFalse(hasattr(error, 'value'))

    def test_incomplete_or_surplus_text_is_rejected(self):
        cases = ['', '   ', 'P(', 'P(x', 'P(x))', '(P(x)', 'P(x) Q(x)', 'P(x)&',
                 '&P(x)', 'P(,x)', 'P(x,)', '∀', '∀(P(x))', '∀x', 'Ex', '()',
                 'P(x) -> -> Q(x)', 'P(x) <->', '~', 'P(x y)', 'P(x) trailing']
        for text in cases:
            with self.subTest(text=text), self.assertRaises(FormulaSyntaxError) as caught:
                parse(text, self.language)
            self.assertLessEqual(caught.exception.span.end, len(text))
            self.assertFalse(hasattr(caught.exception, 'value'))

    def test_declared_names_cannot_be_bound_as_variables(self):
        for text in ('∀f P(f)', 'Af P(x)', '∃P P(x)'):
            with self.subTest(text=text), self.assertRaises(FormulaSyntaxError) as caught:
                parse(text, self.language)
            self.assertEqual(caught.exception.code, 'invalid_bound_variable')

    def test_unicode_positions_count_code_points_not_utf16_units(self):
        result = parse('P(𝑥) & Q(y)', self.language)
        self.assertEqual(result.left.arguments[0].span, Span(2, 3))
        self.assertEqual(result.right.span, Span(7, 11))
        self.assertEqual(len('P(𝑥) '.encode('utf-16-le')) // 2, 6)

    def test_invalid_characters_equality_and_latex_are_not_silent_aliases(self):
        for text, code in [('x=y', 'unsupported_equality'), (r'\neg P(x)', 'invalid_character'),
                           ('P(x) && Q(x)', 'expected_formula'), ('P(x);', 'invalid_character'),
                           ("__import__('os')", 'invalid_character')]:
            with self.subTest(text=text), self.assertRaises(FormulaSyntaxError) as caught:
                parse(text, self.language)
            self.assertEqual(caught.exception.code, code)

    def test_error_at_end_of_input_has_zero_width_span(self):
        with self.assertRaises(FormulaSyntaxError) as caught:
            parse('P(x) &', self.language)
        self.assertEqual(caught.exception.span, Span(6, 6))

    def test_parser_limits_cover_parentheses_prefixes_terms_and_flat_chains(self):
        cases = ['(' * 129 + 'P(x)' + ')' * 129, '¬' * 129 + 'P(x)',
                 'P(' + 'f(' * 129 + 'x' + ')' * 130, ' & '.join(['P(x)'] * 140),
                 ' ' * 100_001, '¬ ' * 20_001 + 'P(x)']
        for text in cases:
            with self.subTest(length=len(text)), self.assertRaises(EvaluationLimitError) as caught:
                parse(text, self.language)
            self.assertFalse(hasattr(caught.exception, 'value'))

    def test_successful_parse_after_failure_has_no_shared_state(self):
        with self.assertRaises(FormulaSyntaxError):
            parse('P(', self.language)
        self.assertFormula('P(x)', self.p)


class LexerTests(unittest.TestCase):
    def test_longest_aliases_canonical_values_and_original_lexemes(self):
        tokens = tokenize('P(x)<->~Q(x)->R(x,y)')
        operators = [(t.kind, t.lexeme, t.span) for t in tokens if t.kind in ('↔', '¬', '→')]
        self.assertEqual(operators, [('↔', '<->', Span(4, 7)), ('¬', '~', Span(7, 8)),
                                     ('→', '->', Span(12, 14))])

    def test_identifier_boundaries_preserve_words_and_combining_marks(self):
        tokens = tokenize('Ax Existe v vecino x_1 a\u0301 𝑥')
        self.assertEqual([t.value for t in tokens[:-1]], ['Ax', 'Existe', 'v', 'vecino', 'x_1', 'a\u0301', '𝑥'])

    def test_multiline_offsets_and_type_errors(self):
        self.assertEqual(tokenize('\n P(x)')[0].span, Span(2, 3))
        with self.assertRaises(TypeError):
            tokenize(None)


class LanguageValidationTests(unittest.TestCase):
    def test_invalid_language_declarations_are_rejected_before_parsing(self):
        cases = [(Language({'f': 1}, {'f': 1}), 'ambiguous_symbol'),
                 (Language({'f': -1}, {'P': 1}), 'invalid_arity'),
                 (Language({'f': True}, {'P': 1}), 'invalid_arity'),
                 (Language({'f': 1.0}, {'P': 1}), 'invalid_arity'),
                 (Language({'bad name': 1}, {'P': 1}), 'invalid_name'),
                 (Language({}, {'=': 2}), 'invalid_name')]
        for language, code in cases:
            with self.subTest(code=code), self.assertRaises(SemanticInputError) as caught:
                parse('P(x)', language)
            self.assertEqual(caught.exception.code, code)


if __name__ == '__main__':
    unittest.main()
