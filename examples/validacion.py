# Demo reproducible de filas externas, diagnóstico múltiple y bloqueo del motor.
from __future__ import annotations

from lm_p3.application.service import evaluate_formula
from lm_p3.models.errors import InputValidationError
from lm_p3.syntax.parser import parse
from lm_p3.validation.normalization import build_environment, build_interpretation, build_language


def main() -> None:
    language = build_language([['f', 1]], [['P', 1]])
    domain = ['a', 'b']
    rows = [[['a'], 'b'], [['b'], 'a']]
    environment = build_environment(language, domain, [['x', 'a']])
    scenarios = [
        ('Entrada válida', {'f': rows}, {'P': [['a']]}),
        ('Dos tablas vacías', {'f': []}, {'P': []}),
        ('Salidas contradictorias', {'f': rows + [[['a'], 'a']]}, {'P': [['a']]}),
    ]
    for label, functions, relations in scenarios:
        print(label)
        try:
            interpretation = build_interpretation(language, domain, functions, relations)
            result = evaluate_formula('P(f(x))', language, interpretation, environment, parse=parse)
            print(f'  {"Verdadero" if result.evaluation.value else "Falso"}: '
                  f'{result.evaluation.trace.reason}')
        except InputValidationError as error:
            count = len(error.errors)
            label = 'error' if count == 1 else 'errores'
            print(f'  No evaluado: {count} {label} de entrada.')
            for issue in error.errors:
                print(f'  {issue.field} [{issue.code}]: {issue.message}')


if __name__ == '__main__':
    main()
