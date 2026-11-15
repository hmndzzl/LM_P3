"""Renderizado en consola y exportación DOT de árboles sintácticos."""

from __future__ import annotations

from pathlib import Path

from src.cyk.parse_tree import ParseTreeNode


def render_ascii(tree: ParseTreeNode) -> str:
    """Representa ``tree`` mediante ramas Unicode legibles en consola."""

    _require_tree(tree)
    lines = [tree.symbol]

    def visit(node: ParseTreeNode, prefix: str) -> None:
        for index, child in enumerate(node.children):
            last = index == len(node.children) - 1
            lines.append(f"{prefix}{'└── ' if last else '├── '}{child.symbol}")
            visit(child, prefix + ("    " if last else "│   "))

    visit(tree, "")
    return "\n".join(lines)


def to_dot(tree: ParseTreeNode) -> str:
    """Genera una descripción Graphviz DOT sin depender de Graphviz."""

    _require_tree(tree)
    lines = ["digraph ParseTree {", "  rankdir=TB;", "  node [shape=box];"]
    next_id = 0

    def visit(node: ParseTreeNode) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        label = node.symbol.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  n{node_id} [label="{label}"];')
        for child in node.children:
            child_id = visit(child)
            lines.append(f"  n{node_id} -> n{child_id};")
        return node_id

    visit(tree)
    lines.append("}")
    return "\n".join(lines) + "\n"


def export_dot(tree: ParseTreeNode, destination: str | Path) -> Path:
    """Escribe el árbol en ``destination`` y devuelve la ruta utilizada."""

    path = Path(destination)
    path.write_text(to_dot(tree), encoding="utf-8")
    return path


def _require_tree(tree: ParseTreeNode) -> None:
    if not isinstance(tree, ParseTreeNode):
        raise TypeError("Se requiere un ParseTreeNode para visualizar el árbol.")
