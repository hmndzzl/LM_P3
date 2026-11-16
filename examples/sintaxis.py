from __future__ import annotations

from lm_p3.application.service import evaluate_formula
from lm_p3.models.errors import FormulaSyntaxError
from lm_p3.models.language import Interpretation, Language
from lm_p3.syntax.parser import analyze, parse


def main() -> None:
    language = Language({'f': 1}, {'P': 1})
    interpretation = Interpretation(('a', 'b'), {'f': {('a',): 'b', ('b',): 'a'}},
                                    {'P': {('a',)}})
    cases = [('Ex P(x)', {}), ('Ax P(x)', {}), ('Ax (P(x) | ~P(x))', {}),
             ('Ex (P(x) & ~P(x))', {}), ('P(f(x))', {'x': 'a'})]
    for text, environment in cases:
        analysis = analyze(text, language)
        outcome = evaluate_formula(text, language, interpretation, environment, parse=parse)
        result = outcome.evaluation
        print(f'{text}: {"Verdadero" if result.value else "Falso"}; '
              f'variables libres={sorted(analysis.free_variables)}; razón={result.trace.reason}; '
              f'elemento decisivo={result.trace.decisive_element}; '
              f'comprobados={result.trace.checked_elements}')
    try:
        parse('P(x,y)', language)
    except FormulaSyntaxError as error:
        print(f'Entrada inválida: {error.message} Código={error.code}; '
              f'rango=[{error.span.start},{error.span.end}). Sin valor de verdad.')


if __name__ == '__main__':
    main()
