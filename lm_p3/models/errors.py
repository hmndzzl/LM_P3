# Los errores semánticos esperados nunca contienen un valor de verdad.


class SemanticInputError(ValueError):
    def __init__(self, code: str, message: str, field: str = '') -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field


class EvaluationLimitError(RuntimeError):
    code = 'evaluation_limit'


class EvaluationCancelledError(RuntimeError):
    code = 'evaluation_cancelled'
