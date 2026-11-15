"""Reconstrucción del árbol sintáctico a partir de una tabla CYK."""

from __future__ import annotations

from dataclasses import dataclass

from src.cyk.cyk_parser import BinaryPointer, CYKResult, TerminalPointer


@dataclass(frozen=True)
class ParseTreeNode:
    """Nodo inmutable de un árbol de derivación."""

    symbol: str
    children: tuple["ParseTreeNode", ...] = ()

    @property
    def is_leaf(self) -> bool:
        """Indica si el nodo representa un terminal de la entrada."""

        return not self.children

    def to_nested_tuple(self) -> str | tuple[str, tuple[object, ...]]:
        """Expone una representación simple útil para interfaces y pruebas."""

        if self.is_leaf:
            return self.symbol
        return self.symbol, tuple(child.to_nested_tuple() for child in self.children)


def build_parse_tree(result: CYKResult) -> ParseTreeNode:
    """Reconstruye una derivación desde la celda raíz ``V[1][n]``.

    Cuando una celda contiene varias derivaciones, se elige la primera según el
    orden de las producciones de la gramática y de las particiones de CYK.
    """

    if not isinstance(result, CYKResult):
        raise TypeError("La reconstrucción requiere un CYKResult.")
    if not result.accepted:
        raise ValueError("No existe un árbol sintáctico para una entrada rechazada.")

    return _build_node(result, 1, len(result.tokens), result.start_symbol)


def _build_node(
    result: CYKResult, start: int, span: int, symbol: str
) -> ParseTreeNode:
    pointers = result.table[start][span].get(symbol)
    if not pointers:
        raise ValueError(
            f"La celda V[{start}][{span}] no contiene el símbolo {symbol!r}."
        )

    pointer = pointers[0]
    if isinstance(pointer, TerminalPointer):
        terminal = ParseTreeNode(pointer.token)
        return ParseTreeNode(symbol, (terminal,))
    if isinstance(pointer, BinaryPointer):
        left = _build_node(result, start, pointer.split, pointer.left_symbol)
        right = _build_node(
            result,
            start + pointer.split,
            span - pointer.split,
            pointer.right_symbol,
        )
        return ParseTreeNode(symbol, (left, right))

    raise TypeError(f"Backpointer desconocido para el símbolo {symbol!r}.")
