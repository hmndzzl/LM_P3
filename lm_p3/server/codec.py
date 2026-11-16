# Traducción de JSON a los constructores de M2 y resultados de M1.
from __future__ import annotations

from dataclasses import asdict
import json

from lm_p3.application.service import evaluate_formula
from lm_p3.models.errors import SemanticInputError
from lm_p3.syntax.parser import analyze, parse
from lm_p3.validation.normalization import build_environment, build_interpretation, build_language


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SemanticInputError('duplicate_key', f'La clave {key} está repetida.', 'request')
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise SemanticInputError('invalid_json', 'JSON no admite NaN ni valores infinitos.', 'request')


def decode_request(body: bytes) -> dict:
    try:
        data = json.loads(body.decode('utf-8'), object_pairs_hook=_unique_object,
                          parse_constant=_invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, SemanticInputError):
            raise
        raise SemanticInputError('invalid_json', 'Envía un objeto JSON válido en UTF-8.', 'request') from error
    if not isinstance(data, dict):
        raise SemanticInputError('invalid_structure', 'La petición debe ser un objeto JSON.', 'request')
    return data


def error_response(error: Exception, revision: int | None = None) -> dict:
    errors = []
    for issue in getattr(error, 'errors', (error,)):
        span = getattr(issue, 'span', None)
        errors.append({'code': getattr(issue, 'code', 'internal_error'), 'message': str(issue.message)
                       if hasattr(issue, 'message') else str(issue),
                       'field': getattr(issue, 'field', ''),
                       'span': asdict(span) if span is not None else None,
                       'details': dict(getattr(issue, 'details', {}))})
    return {'status': 'invalid' if isinstance(error, SemanticInputError) else 'not_evaluated',
            'revision': revision, 'errors': errors}


def process_request(operation: str, data: dict) -> dict:
    required = {'revision', 'functions', 'predicates', 'formula'}
    if operation == 'evaluate':
        required |= {'domain', 'function_rows', 'relations', 'assignments'}
    elif operation != 'analyze':
        raise ValueError('Operación interna no reconocida.')
    if set(data) != required:
        raise SemanticInputError('invalid_fields', 'Faltan campos o hay campos no admitidos.', 'request')
    if type(data['revision']) is not int or data['revision'] < 0:
        raise SemanticInputError('invalid_revision', 'La revisión debe ser un entero no negativo.', 'request')
    if not isinstance(data['formula'], str):
        raise SemanticInputError('invalid_formula', 'La fórmula debe ser texto.', 'formula')
    language = build_language(data['functions'], data['predicates'])
    if operation == 'analyze':
        analysis = analyze(data['formula'], language)
        return {'status': 'analyzed', 'revision': data['revision'],
                'free_variables': sorted(analysis.free_variables)}
    interpretation = build_interpretation(language, data['domain'], data['function_rows'], data['relations'])
    environment = build_environment(language, data['domain'], data['assignments'])
    outcome = evaluate_formula(data['formula'], language, interpretation, environment,
                               parse=parse, revision=data['revision'])
    return {'status': 'evaluated', **asdict(outcome)}
