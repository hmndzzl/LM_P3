# Frontera de filas Python antes de perder duplicados; sin JSON ni HTTP.
from __future__ import annotations

from lm_p3.models.language import Interpretation, Language
from lm_p3.validation.validator import _Checks, _domain, _environment, _interpretation, _language


def build_language(functions: object, predicates: object) -> Language:
    # Las declaraciones repetidas se rechazan, incluso con la misma aridad.
    checks = _Checks()
    groups = []
    for kind, declarations in (('functions', functions), ('predicates', predicates)):
        rows = checks.sequence(declarations, f'language.{kind}')
        result = {}
        for index, row in enumerate(rows if rows is not None else ()):
            path = f'language.{kind}[{index}]'
            if not isinstance(row, (list, tuple)) or len(row) != 2:
                checks.add('invalid_declaration', 'Declara un nombre y una aridad.', path)
                continue
            name, arity = row
            if not isinstance(name, str) or not name.isidentifier():
                checks.add('invalid_name', 'Usa un identificador sin espacios ni operadores.', path)
                continue
            if type(arity) is not int or arity < 0:
                checks.add('invalid_arity', 'La aridad debe ser un entero no negativo.', path)
                continue
            if name in result:
                checks.add('duplicate_declaration', f'{name} está declarado más de una vez.', path, symbol=name)
            else:
                result[name] = arity
        groups.append(result)
    language = Language(*groups)
    _language(language, checks)
    checks.finish()
    return language


def build_interpretation(language: Language, domain: object, function_rows: object,
                         relations: object) -> Interpretation:
    checks = _Checks()
    _language(language, checks)
    checks.finish()
    ordered, functions, predicates = _interpretation(language, domain, function_rows, relations,
                                                     checks, raw=True)
    checks.finish()
    return Interpretation(ordered, functions, predicates)


def build_environment(language: Language, domain: object, assignments: object) -> dict[str, str]:
    checks = _Checks()
    _language(language, checks)
    checks.finish()
    ordered = _domain(domain, checks)
    environment = _environment(language, ordered, assignments, checks, raw=True)
    checks.finish()
    return environment
