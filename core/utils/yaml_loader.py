from __future__ import annotations

import ast
from typing import Any, TextIO


def safe_load(stream: TextIO | str) -> Any:
    """A small YAML subset loader (stdlib-only).

    Supports the subset of YAML used in this repository:
      - mappings via `key: value`
      - nested blocks via indentation (spaces)
      - lists via `- item`
      - quoted strings
      - inline lists/dicts using JSON/Python-literal compatible syntax
      - booleans/null/numbers

    It is *not* a full YAML implementation.
    """

    text = stream.read() if hasattr(stream, "read") else str(stream)
    return _parse_block(_preprocess_lines(text))


def _preprocess_lines(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for raw in text.splitlines():
        # Strip comments (naive, but works for our configs).
        line = raw.split("#", 1)[0].rstrip("\n").rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        out.append((indent, line.lstrip(" ")))
    return out


def _parse_scalar(value: str) -> Any:
    v = value.strip()
    if v == "":
        return ""

    lower = v.lower()
    if lower in {"true", "yes"}:
        return True
    if lower in {"false", "no"}:
        return False
    if lower in {"null", "none", "~"}:
        return None

    # numbers
    try:
        if "." in v:
            return float(v)
        return int(v)
    except Exception:
        pass

    # inline list/dict or quoted string using Python literal syntax
    if (v.startswith("[") and v.endswith("]")) or (v.startswith("{") and v.endswith("}")):
        try:
            return ast.literal_eval(v)
        except Exception:
            return v

    if (v.startswith("\"") and v.endswith("\"")) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]

    return v


def _peek_next_nonempty(lines: list[tuple[int, str]], start: int) -> tuple[int, str] | None:
    for i in range(start, len(lines)):
        return lines[i]
    return None


def _parse_block(lines: list[tuple[int, str]], start: int = 0, indent: int = 0) -> Any:
    """Parse a block starting at `start`, assuming current indent >= `indent`.

    Returns the parsed object if start==0; otherwise returns (obj, next_index).
    """

    idx = start
    # Decide container type on first meaningful line
    container: Any
    if idx < len(lines) and lines[idx][0] >= indent and lines[idx][1].startswith("-"):
        container = []
    else:
        container = {}

    while idx < len(lines):
        line_indent, line = lines[idx]
        if line_indent < indent:
            break
        if line_indent > indent:
            # This can happen if previous key created a nested container and we didn't consume it.
            raise ValueError(f"Invalid indentation at line: {line}")

        if isinstance(container, list):
            if not line.startswith("-"):
                break
            item = line[1:].lstrip(" ")

            # inline dict entry: - key: value
            if ":" in item:
                key, rest = item.split(":", 1)
                key = key.strip()
                rest = rest.strip()
                if rest == "":
                    # nested dict/list
                    nxt = _peek_next_nonempty(lines, idx + 1)
                    if nxt is None or nxt[0] <= line_indent:
                        container.append({key: {}})
                        idx += 1
                        continue
                    nested_obj, next_idx = _parse_block(lines, idx + 1, indent=nxt[0])
                    container.append({key: nested_obj})
                    idx = next_idx
                    continue

                container.append({key: _parse_scalar(rest)})
                idx += 1
                continue

            # scalar list item, or nested block if item is empty
            if item == "":
                nxt = _peek_next_nonempty(lines, idx + 1)
                if nxt is None or nxt[0] <= line_indent:
                    container.append(None)
                    idx += 1
                    continue
                nested_obj, next_idx = _parse_block(lines, idx + 1, indent=nxt[0])
                container.append(nested_obj)
                idx = next_idx
                continue

            container.append(_parse_scalar(item))
            idx += 1
            continue

        # dict container
        if line.startswith("-"):
            # A list inside a dict must be declared by key first.
            raise ValueError(f"List item without a parent key at indent {indent}: {line}")

        if ":" not in line:
            raise ValueError(f"Invalid mapping entry: {line}")

        key, rest = line.split(":", 1)
        key = key.strip()
        rest = rest.strip()

        if rest != "":
            container[key] = _parse_scalar(rest)
            idx += 1
            continue

        # Determine if this key maps to list or dict by looking ahead.
        nxt = _peek_next_nonempty(lines, idx + 1)
        if nxt is None or nxt[0] <= line_indent:
            container[key] = {}
            idx += 1
            continue

        nested_indent = nxt[0]
        nested_obj, next_idx = _parse_block(lines, idx + 1, indent=nested_indent)
        container[key] = nested_obj
        idx = next_idx

    if start == 0:
        return container
    return container, idx
