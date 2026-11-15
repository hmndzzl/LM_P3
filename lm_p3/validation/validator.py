# Validación del lenguaje textual antes de construir el AST compartido
from __future__ import annotations

from lm_p3.models.errors import SemanticInputError
from lm_p3.models.language import Language


def validate_language(language: Language) -> None:
    # No normaliza nombres, las mayúsculas y minúsculas se conservan
    if not isinstance(language, Language):
        raise TypeError('Se requiere Language.')
    if set(language.functions) & set(language.predicates):
        raise SemanticInputError('ambiguous_symbol',
                                 'Un símbolo no puede ser función y predicado.', 'language')
    for kind, symbols in (('functions', language.functions),
                          ('predicates', language.predicates)):
        for name, arity in symbols.items():
            if not isinstance(name, str) or not name.isidentifier():
                raise SemanticInputError('invalid_name',
                                         'Usa un identificador sin espacios ni operadores.',
                                         f'language.{kind}')
            if type(arity) is not int or arity < 0:
                raise SemanticInputError('invalid_arity',
                                         'La aridad debe ser un entero no negativo.',
                                         f'language.{kind}.{name}')
