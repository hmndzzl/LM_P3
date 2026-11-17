# Adaptador para ejecutar el mismo contrato del servidor dentro de Pyodide.
from __future__ import annotations

import json

from lm_p3.models.errors import EvaluationLimitError, SemanticInputError
from lm_p3.server.codec import decode_request, error_response, process_request

MAX_BODY = 256 * 1024
MAX_RESPONSE = 8 * 1024 * 1024


def execute(operation: str, payload: str) -> str:
    revision = None
    try:
        if operation not in ('analyze', 'evaluate', 'compare'):
            raise SemanticInputError('invalid_operation', 'Operación no admitida.', 'request')
        body = payload.encode('utf-8')
        if len(body) > MAX_BODY:
            raise EvaluationLimitError('La petición supera 256 KB. Reduce los datos.')
        data = decode_request(body)
        if type(data.get('revision')) is int and data['revision'] >= 0:
            revision = data['revision']
        result = process_request(operation, data)
        serialized = json.dumps(result, ensure_ascii=False, allow_nan=False)
        if len(serialized.encode('utf-8')) > MAX_RESPONSE:
            raise EvaluationLimitError('La evidencia supera 8 MB. Reduce la fórmula o el dominio.')
        return serialized
    except (SemanticInputError, EvaluationLimitError) as error:
        return json.dumps(error_response(error, revision), ensure_ascii=False, allow_nan=False)
    except Exception:
        # Los detalles internos no se convierten en verdad ni se muestran como diagnósticos de usuario.
        return json.dumps(error_response(RuntimeError('No se pudo completar la evaluación. Reintenta la operación.'), revision))
