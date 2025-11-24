import re
from typing import Optional
from .common import remove_comments, find_matching_paren

__all__ = ["number_of_methods", "max_number_of_params"]

KEYWORDS = {
    "if","for","while","switch","catch","else","class","enum",
    "extension","typedef","operator","return","assert","throw","new"
}

def _prev_ident(s: str, start_idx: int) -> Optional[str]:
    """Return identifier immediately preceding '(' that starts at start_idx."""
    i = start_idx - 1
    # skip spaces/newlines
    while i >= 0 and s[i].isspace():
        i -= 1
    # read identifier backwards
    j = i
    while j >= 0 and (s[j].isalnum() or s[j] == "_"):
        j -= 1
    ident = s[j+1:i+1]
    return ident if ident else None

def _iter_signatures(code: str):
    """
    Yield (paren_open, paren_close) for declarations that look like:
        <ret/type> name ( ... ) { ... }
    We skip control-flow keywords (if, for, while, switch, catch, else).
    """
    s = remove_comments(code)
    i, n = 0, len(s)
    while True:
        idx = s.find("(", i)
        if idx == -1:
            break
        close = find_matching_paren(s, idx)
        if close == -1:
            i = idx + 1
            continue
        # next non-space after ')'
        k = close + 1
        while k < n and s[k].isspace():
            k += 1
        if k < n and s[k] == "{":
            ident = _prev_ident(s, idx)
            if ident and ident not in KEYWORDS:
                yield (idx, close)
        i = close + 1

def number_of_methods(code: str) -> int:
    return sum(1 for _ in _iter_signatures(code))

def max_number_of_params(code: str) -> int:
    s = remove_comments(code)
    max_p = 0
    for op, cp in _iter_signatures(s):
        params = s[op+1:cp]
        if not params.strip():
            continue
        # Count top-level commas ignoring nested <>{}[]() and quoted strings
        stack, in_q, commas = [], None, 0
        j = 0
        while j < len(params):
            ch = params[j]
            if in_q:
                if ch == in_q:
                    in_q = None
                j += 1
                continue
            if ch in ("'", '"'):
                in_q = ch
            elif ch in "<{[(":
                stack.append(ch)
            elif ch in ">}])":
                if stack:
                    stack.pop()
            elif ch == "," and not stack:
                commas += 1
            j += 1
        cur = commas + 1 if params.strip() else 0
        if cur > max_p:
            max_p = cur
    return max_p
