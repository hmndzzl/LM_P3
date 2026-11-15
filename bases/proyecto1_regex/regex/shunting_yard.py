"""
Implementación del algoritmo Shunting Yard para transformar expresiones regulares
de notación infija (infix) a notación postfija (postfix).
"""

from .tokens import BINARY_OPS, POSTFIX_OPS, EPSILON, CONCAT_DISPLAY


def get_precedence(token):
    """Devuelve el nivel de precedencia de un operador."""
    kind, value = token
    if kind == 'LPAREN':
        return 1
    if kind == 'OP' and value == '|':
        return 2
    if kind == 'CONCAT':
        return 3
    if kind == 'OP' and value in ('?', '*', '+'):
        return 4
    return 5


def display(token):
    """Representación en texto de un token."""
    kind, value = token
    return CONCAT_DISPLAY if kind == 'CONCAT' else value


def display_postfix(token):
    """Representación de un token postfijo escapando literales que coincidan con operadores."""
    kind, value = token
    if kind == 'LIT' and value in BINARY_OPS | POSTFIX_OPS | {CONCAT_DISPLAY, '(', ')', '\\'}:
        return '\\' + value
    return display(token)


def tokenize(regex):
    """Convierte una cadena de expresión regular en una lista de tokens clasificados."""
    tokens = []
    i = 0
    n = len(regex)

    while i < n:
        c = regex[i]

        if c == '\\':
            if i + 1 >= n:
                raise ValueError("Caracter de escape '\\' al final de la expresion sin caracter siguiente.")
            tokens.append(('LIT', regex[i + 1]))
            i += 2
        elif c.isspace():
            i += 1
        elif c == '(':
            tokens.append(('LPAREN', '('))
            i += 1
        elif c == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
        elif c == '^':
            raise ValueError(
                "El operador '^' no esta soportado. "
                "Use '\\^' si desea reconocer el caracter '^' literalmente."
            )
        elif c in BINARY_OPS or c in POSTFIX_OPS:
            tokens.append(('OP', c))
            i += 1
        else:
            tokens.append(('LIT', c))
            i += 1

    return tokens


def validate_tokens(tokens):
    """Valida la consistencia de los paréntesis y operandos en la secuencia de tokens."""
    paren_depth = 0
    expect_operand = True

    for idx, (kind, value) in enumerate(tokens):
        if kind == 'LIT':
            expect_operand = False

        elif kind == 'LPAREN':
            paren_depth += 1
            expect_operand = True

        elif kind == 'RPAREN':
            if expect_operand:
                raise ValueError(f"Parentesis de cierre en posicion {idx} sin operando/grupo previo (grupo vacio u operador colgante).")
            paren_depth -= 1
            if paren_depth < 0:
                raise ValueError(f"Parentesis de cierre en posicion {idx} sin apertura correspondiente.")
            expect_operand = False

        elif kind == 'OP':
            if value in POSTFIX_OPS:
                if expect_operand:
                    raise ValueError(f"Operador postfijo '{value}' en posicion {idx} sin operando previo valido.")
            elif value in BINARY_OPS:
                if expect_operand:
                    raise ValueError(f"Operador binario '{value}' en posicion {idx} sin operando izquierdo valido.")
                expect_operand = True

    if expect_operand:
        raise ValueError("La expresion termina con un operador que espera un operando.")
    if paren_depth != 0:
        raise ValueError("Parentesis desbalanceados: falta cerrar uno o mas '('.")


def pop_atom(output):
    """Extrae el último átomo o subexpresión completa de la lista de salida."""
    if not output:
        raise ValueError("No hay operando disponible para aplicar el operador extendido.")

    kind, value = output[-1]

    if kind == 'OP' and value == '*':
        star = output.pop()
        inner = pop_atom(output)
        return inner + [star]

    if kind == 'RPAREN':
        depth = 0
        j = len(output) - 1
        while j >= 0:
            k, _ = output[j]
            if k == 'RPAREN':
                depth += 1
            elif k == 'LPAREN':
                depth -= 1
            if depth == 0:
                break
            j -= 1
        group = output[j:]
        del output[j:]
        return group

    return [output.pop()]


def expand_extensions(tokens):
    """
    Expande operadores sintácticos extendidos:
    r+  -> (r r*)
    r?  -> (r | ε)
    """
    output = []

    for token in tokens:
        kind, value = token

        if kind == 'OP' and value == '+':
            atom = pop_atom(output)
            output.append(('LPAREN', '('))
            output.extend(atom)
            output.extend(atom)
            output.append(('OP', '*'))
            output.append(('RPAREN', ')'))

        elif kind == 'OP' and value == '?':
            atom = pop_atom(output)
            output.append(('LPAREN', '('))
            output.extend(atom)
            output.append(('OP', '|'))
            output.append(('LIT', EPSILON))
            output.append(('RPAREN', ')'))

        else:
            output.append(token)

    return output


def insert_concat(tokens):
    """Inserta operadores explícitos de concatenación '.' entre tokens contiguos correspondientes."""
    result = []
    n = len(tokens)

    for i in range(n):
        t = tokens[i]
        result.append(t)

        if i + 1 < n:
            nxt = tokens[i + 1]
            is_next_close_or_op = nxt[0] == 'RPAREN' or (nxt[0] == 'OP' and nxt[1] in (BINARY_OPS | POSTFIX_OPS))
            is_current_open_or_binary = t[0] == 'LPAREN' or (t[0] == 'OP' and t[1] in BINARY_OPS)

            if not is_current_open_or_binary and not is_next_close_or_op:
                result.append(('CONCAT', '.'))

    return result


def infix_to_postfix(regex):
    """
    Convierte una expresión regular en formato infijo a notación postfija
    aplicando el algoritmo de Shunting Yard.
    """
    tokens = tokenize(regex)
    validate_tokens(tokens)
    expanded = expand_extensions(tokens)
    formatted = insert_concat(expanded)

    postfix_tokens = []
    stack = []

    for t in formatted:
        kind, value = t

        if kind == 'LIT':
            postfix_tokens.append(t)
        elif kind == 'OP' and value == '*':
            postfix_tokens.append(t)
        elif kind == 'LPAREN':
            stack.append(t)
        elif kind == 'RPAREN':
            while stack and stack[-1][0] != 'LPAREN':
                top = stack.pop()
                postfix_tokens.append(top)
            if not stack:
                raise ValueError("Parentesis de cierre sin apertura correspondiente.")
            stack.pop()
        else:
            while stack:
                peeked = stack[-1]
                should_pop = (
                    get_precedence(peeked) > get_precedence(t)
                    or get_precedence(peeked) == get_precedence(t)
                )
                if peeked[0] != 'LPAREN' and should_pop:
                    top = stack.pop()
                    postfix_tokens.append(top)
                else:
                    break
            stack.append(t)

    while stack:
        top = stack.pop()
        if top[0] == 'LPAREN':
            raise ValueError("Parentesis desbalanceados: falta cerrar uno o mas '('.")
        postfix_tokens.append(top)

    postfix = ''.join(display_postfix(t) for t in postfix_tokens)
    return postfix


def extract_alphabet(postfix):
    """
    Extrae dinámicamente el conjunto de símbolos del alfabeto Σ a partir de la expresión postfija,
    excluyendo operadores binarios/unarios y el símbolo épsilon (ε).
    """
    alphabet = set()
    i = 0
    n = len(postfix)
    while i < n:
        if postfix[i] == '\\':
            if i + 1 < n:
                alphabet.add(postfix[i + 1])
                i += 2
            else:
                i += 1
        else:
            char = postfix[i]
            if char not in ('.', '|', '*', EPSILON):
                alphabet.add(char)
            i += 1
    return alphabet
